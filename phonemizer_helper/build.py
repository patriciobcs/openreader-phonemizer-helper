# SPDX-License-Identifier: GPL-3.0-or-later
"""Build the standalone GPL pronunciation helper for macOS."""

from __future__ import annotations

import os
import shutil
import tempfile
from pathlib import Path

import PyInstaller.__main__ as pyinstaller


def _is_complete_bundle(bundle: Path, name: str) -> bool:
    internal = bundle / "_internal"
    return (
        (bundle / name).is_file()
        and (internal / "espeakng_loader" / "libespeak-ng.dylib").is_file()
        and (internal / "espeakng_loader" / "espeak-ng-data" / "phontab").is_file()
    )


def recover_interrupted_install(out_dir: Path, destination: Path, name: str) -> None:
    """Restore the newest retained previous bundle if an interrupted swap left no public path."""
    if destination.exists():
        return
    working_dirs = sorted(
        out_dir.glob(".phonemizer-helper-*"),
        key=lambda path: path.stat().st_mtime_ns,
        reverse=True,
    )
    for working_dir in working_dirs:
        previous = working_dir / "previous"
        if not _is_complete_bundle(previous, name):
            continue
        previous.rename(destination)
        shutil.rmtree(working_dir, ignore_errors=True)
        return


def build(backend_dir: Path, out_dir: Path) -> None:
    name = "openreader-phonemizer-helper"
    out_dir.mkdir(parents=True, exist_ok=True)
    destination = out_dir / "phonemizer-helper"
    recover_interrupted_install(out_dir, destination, name)
    pyinstaller.run(
        [
            str(backend_dir / "phonemizer_helper" / "server.py"),
            "--onedir",
            "--name", name,
            "--noconfirm",
            "--clean",
            "--target-arch", "arm64",
            "--collect-all", "phonemizer",
            "--collect-all", "espeakng_loader",
            "--collect-all", "language_tags",
            "--hidden-import", "misaki.espeak",
        ]
    )

    built = backend_dir / "dist" / name
    internal = built / "_internal"
    data = internal / "espeakng_loader" / "espeak-ng-data"
    if data.is_dir():
        shutil.copytree(data, internal, dirs_exist_ok=True)

    if not (built / name).is_file():
        raise RuntimeError("GPL phonemizer helper executable missing")
    if not (internal / "espeakng_loader" / "libespeak-ng.dylib").is_file():
        raise RuntimeError("GPL phonemizer helper is missing eSpeak NG")
    if not (data / "phontab").is_file():
        raise RuntimeError("GPL phonemizer helper is missing eSpeak NG data")

    out_dir.mkdir(parents=True, exist_ok=True)
    working_dir = Path(tempfile.mkdtemp(prefix=".phonemizer-helper-", dir=out_dir))
    staged = working_dir / name
    backup = working_dir / "previous"
    preserve_working_dir = False
    try:
        shutil.move(str(built), str(staged))
        try:
            if destination.exists():
                destination.rename(backup)
            staged.rename(destination)
        except BaseException as error:
            if backup.exists() and not destination.exists():
                try:
                    backup.rename(destination)
                except BaseException as restore_error:
                    preserve_working_dir = True
                    raise RuntimeError(
                        f"Could not install phonemizer helper; previous bundle retained at {backup}"
                    ) from restore_error
            raise
    finally:
        if not preserve_working_dir:
            shutil.rmtree(working_dir, ignore_errors=True)
    for stale_dir in out_dir.glob(".phonemizer-helper-*"):
        if stale_dir != working_dir:
            shutil.rmtree(stale_dir, ignore_errors=True)


if __name__ == "__main__":
    root = Path(__file__).resolve().parent.parent
    os.chdir(root)
    build(root, root / "dist" / "openreader-backend")
