# SPDX-License-Identifier: GPL-3.0-or-later
"""Export and verify the source of the actual frozen helper, without executing it."""

from __future__ import annotations

import ast
import json
import marshal
import zipfile
from hashlib import sha256
from pathlib import Path, PurePosixPath
from types import CodeType


def normalized_code(code: CodeType) -> CodeType:
    """Ignore build-directory names, preserving instructions, constants and line tables."""
    return code.replace(
        co_filename="<source>",
        co_consts=tuple(normalized_code(value) if isinstance(value, CodeType) else value for value in code.co_consts),
    )


def source_matches(code: CodeType, source: bytes) -> bool:
    compiled = compile(source, code.co_filename, "exec", dont_inherit=True, optimize=0)
    return normalized_code(code) == normalized_code(compiled)


def native_section_hash(path: Path) -> str:
    """Compare arm64 compiled sections across thin/fat binaries and re-signing."""
    from macholib.MachO import MachO
    from macholib.mach_o import LC_SEGMENT_64

    data = path.read_bytes()
    digest = sha256()
    found = False
    for header in MachO(str(path)).headers:
        if header.header.cputype != 0x0100000C:
            continue
        found = True
        for command, _segment, sections in header.commands:
            if command.cmd != LC_SEGMENT_64:
                continue
            for section in sections:
                if not section.offset or section.flags & 0xFF in {1, 0xC, 0x12}:
                    continue
                start = header.offset + section.offset
                if start + section.size > len(data):
                    raise ValueError("native section exceeds its file")
                digest.update(section.segname)
                digest.update(section.sectname)
                digest.update(data[start : start + section.size])
    if not found:
        raise ValueError("native source association requires an arm64 Mach-O")
    return digest.hexdigest()


def open_frozen(backend: Path):
    # Available in the same desktop environment used to freeze the helper.
    from PyInstaller.archive.readers import CArchiveReader

    executable = backend / "phonemizer-helper" / "openreader-phonemizer-helper"
    reader = CArchiveReader(str(executable))
    names = [name for name in reader.toc if name.upper().startswith("PYZ")]
    if len(names) != 1:
        raise ValueError("expected exactly one embedded helper PYZ archive")
    return reader, reader.open_embedded_archive(names[0])


def source_paths(analysis: Path) -> dict[str, Path]:
    result: dict[str, Path] = {}

    def walk(value):
        if not isinstance(value, (tuple, list)):
            return
        if len(value) == 3 and all(isinstance(item, str) for item in value) and value[2] in {"PYMODULE", "PYSOURCE"}:
            name, path, _kind = value
            if name in result and result[name] != Path(path):
                raise ValueError(f"ambiguous source path for {name}")
            result[name] = Path(path)
        else:
            for item in value:
                walk(item)

    walk(ast.literal_eval(analysis.read_text()))
    return result


def snapshot_path(source: Path, helper_source: Path) -> str:
    path = source.resolve(strict=True)
    helper_root = helper_source.resolve(strict=True)
    if path.is_relative_to(helper_root):
        return "phonemizer_helper/" + path.relative_to(helper_root).as_posix()
    parts = path.parts
    for marker, prefix in (("site-packages", "frozen-sources/site-packages"), ("python3.12", "frozen-sources/stdlib")):
        if marker in parts:
            relative = PurePosixPath(*parts[parts.index(marker) + 1 :])
            if not relative.parts or path.suffix != ".py":
                raise ValueError(f"unexpected frozen source path: {path}")
            return f"{prefix}/{relative}"
    raise ValueError(f"refusing unclassified/private source path: {path}")


def snapshot(backend: Path, analysis: Path, helper_source: Path) -> dict[str, bytes]:
    import PyInstaller

    paths = source_paths(analysis)
    loader = Path(PyInstaller.__file__).parent / "loader"
    for path in loader.glob("*.py"):
        paths.setdefault(path.stem, path)
    reader, pyz = open_frozen(backend)
    files: dict[str, bytes] = {}
    modules = []
    scripts = []
    base_library = []

    def include(name: str, code: CodeType) -> dict[str, str]:
        source = paths.get(name)
        if source is None or not source.is_file():
            raise ValueError(f"matching frozen source missing: {name}")
        data = source.read_bytes()
        if not source_matches(code, data):
            raise ValueError(f"source does not compile to the frozen helper code: {name}")
        relative = snapshot_path(source, helper_source)
        if relative in files and files[relative] != data:
            raise ValueError(f"conflicting source snapshot path: {relative}")
        files[relative] = data
        return {"name": name, "path": relative, "sha256": sha256(data).hexdigest()}

    for name in sorted(pyz.toc):
        code = pyz.extract(name)
        modules.append({"name": name, "namespace": True} if code is None else include(name, code))
    for name, entry in sorted(reader.toc.items()):
        if entry[-1] in {"s", "m", "M"}:
            scripts.append(include(name, marshal.loads(reader.extract(name))))

    library = backend / "phonemizer-helper" / "_internal" / "base_library.zip"
    with zipfile.ZipFile(library) as archive:
        for name in sorted(archive.namelist()):
            if not name.endswith(".pyc"):
                raise ValueError(f"unexpected base library entry: {name}")
            module = name.removesuffix(".pyc").replace("/", ".").removesuffix(".__init__")
            record = include(module, marshal.loads(archive.read(name)[16:]))
            record["entry"] = name
            base_library.append(record)

    coverage = {"schema": 1, "python": "3.12", "modules": modules, "scripts": scripts, "baseLibrary": base_library}
    files["frozen-source-coverage.json"] = (json.dumps(coverage, indent=2, sort_keys=True) + "\n").encode()
    return files


def verify_snapshot(backend: Path, files: dict[str, bytes]) -> None:
    coverage = json.loads(files["frozen-source-coverage.json"])
    if coverage.get("schema") != 1 or coverage.get("python") != "3.12":
        raise ValueError("unsupported frozen source coverage schema")
    reader, pyz = open_frozen(backend)
    modules = coverage["modules"]
    scripts = coverage["scripts"]
    if len({item["name"] for item in modules}) != len(modules) or {item["name"] for item in modules} != set(pyz.toc):
        raise ValueError("source snapshot does not cover exactly the helper PYZ modules")
    expected_scripts = {name for name, entry in reader.toc.items() if entry[-1] in {"s", "m", "M"}}
    if len({item["name"] for item in scripts}) != len(scripts) or {item["name"] for item in scripts} != expected_scripts:
        raise ValueError("source snapshot does not cover exactly the helper entry scripts")

    def check(item, code):
        if code is None:
            if item != {"name": item["name"], "namespace": True}:
                raise ValueError("invalid namespace source entry")
            return
        data = files.get(item.get("path", ""))
        if data is None or sha256(data).hexdigest() != item.get("sha256"):
            raise ValueError(f"frozen source missing or changed: {item['name']}")
        if not source_matches(code, data):
            raise ValueError(f"source does not compile to the frozen helper code: {item['name']}")

    for item in modules:
        check(item, pyz.extract(item["name"]))
    for item in scripts:
        check(item, marshal.loads(reader.extract(item["name"])))
    with zipfile.ZipFile(backend / "phonemizer-helper" / "_internal" / "base_library.zip") as archive:
        records = coverage["baseLibrary"]
        if len({item["entry"] for item in records}) != len(records) or {item["entry"] for item in records} != set(archive.namelist()):
            raise ValueError("source snapshot does not cover exactly the helper base library")
        for item in records:
            check(item, marshal.loads(archive.read(item["entry"])[16:]))
    proof = json.loads(files["phonemizer_helper/native-provenance.json"])
    required = {"libgcc_s.1.1.dylib", "libgfortran.5.dylib", "libquadmath.0.dylib"}
    if {item["library"] for item in proof["libraries"]} != required:
        raise ValueError("native source association omits a GCC runtime")
    for item in proof["libraries"]:
        library = backend / "phonemizer-helper" / "_internal" / "numpy" / ".dylibs" / item["library"]
        if native_section_hash(library) != item["upstreamSectionSha256"]:
            raise ValueError(f"native source association differs from the helper: {item['library']}")
