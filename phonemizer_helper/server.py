# SPDX-License-Identifier: GPL-3.0-or-later
"""Line-oriented pronunciation process for the Kokoro backend.

This helper links to phonemizer-fork and eSpeak NG. It is GPL-3.0-or-later.
Only plain text, language, and phoneme strings cross the process boundary.
"""

from __future__ import annotations

import hashlib
import json
import logging
import os
import shutil
import sys
import tempfile
from pathlib import Path

logger = logging.getLogger(__name__)


def _fingerprint_espeak_data(data_path: Path) -> str:
    digest = hashlib.sha256()
    for path in sorted(data_path.rglob("*")):
        if not path.is_file():
            continue
        digest.update(path.relative_to(data_path).as_posix().encode("utf-8"))
        with path.open("rb") as source:
            for block in iter(lambda: source.read(1024 * 1024), b""):
                digest.update(block)
    return digest.hexdigest()


def _mirror_espeak_data(data_path: Path, destination: Path) -> None:
    marker_name = ".openreader-espeak-data-sha256"
    fingerprint = _fingerprint_espeak_data(data_path)
    marker = destination / marker_name
    if (destination / "phontab").is_file() and marker.is_file():
        try:
            if marker.read_text(encoding="ascii").strip() == fingerprint:
                return
        except OSError:
            pass

    destination.parent.mkdir(parents=True, exist_ok=True)
    working_dir = Path(tempfile.mkdtemp(prefix=".espeak-ng-data-", dir=destination.parent))
    staged = working_dir / "data"
    backup = working_dir / "previous"
    preserve_working_dir = False
    try:
        shutil.copytree(data_path, staged)
        if not (staged / "phontab").is_file():
            raise RuntimeError("copied eSpeak NG data is missing phontab")
        (staged / marker_name).write_text(fingerprint + "\n", encoding="ascii")
        try:
            if destination.exists() or destination.is_symlink():
                destination.rename(backup)
            staged.rename(destination)
        except BaseException:
            if backup.exists() or backup.is_symlink():
                try:
                    backup.rename(destination)
                except OSError as error:
                    preserve_working_dir = True
                    raise RuntimeError(
                        f"Could not publish eSpeak NG data; previous mirror retained at {backup}"
                    ) from error
            raise
    finally:
        if not preserve_working_dir:
            shutil.rmtree(working_dir, ignore_errors=True)


def _pyinstaller_internal_dir() -> Path | None:
    """Return PyInstaller's _internal dir when running from a frozen bundle."""
    if not getattr(sys, "frozen", False):
        return None

    meipass = getattr(sys, "_MEIPASS", None)
    if meipass:
        return Path(meipass)

    candidate = Path(sys.executable).resolve().parent / "_internal"
    if candidate.exists():
        return candidate
    return None


def _configure_frozen_espeak() -> None:
    """Pin espeak-ng paths inside the PyInstaller bundle.

    `misaki.espeak` asks `espeakng_loader` for both paths at import time. In
    frozen builds, relying on package-relative discovery is brittle because the
    Python module can live in the PYZ archive while data files are unpacked in
    `_internal/espeakng_loader`. Patch the loader once at process start so the
    later Kokoro import receives stable absolute paths.
    """
    internal_dir = _pyinstaller_internal_dir()
    if internal_dir is None:
        return

    espeak_root = internal_dir / "espeakng_loader"
    data_path = espeak_root / "espeak-ng-data"
    lib_name = "espeak-ng.dll" if sys.platform == "win32" else "libespeak-ng.dylib"
    if sys.platform.startswith("linux"):
        lib_name = "libespeak-ng.so"
    library_path = espeak_root / lib_name

    if not data_path.exists() or not library_path.exists():
        logger.warning(
            "Frozen espeak-ng resources not found: data=%s exists=%s library=%s exists=%s",
            data_path,
            data_path.exists(),
            library_path,
            library_path.exists(),
        )
        return

    if sys.platform == "darwin":
        try:
            container_data_path = (
                Path.home()
                / "Library"
                / "Application Support"
                / "io.openreader.desktop"
                / "espeak-ng-data"
            )
            _mirror_espeak_data(data_path, container_data_path)
            data_path = container_data_path
            logger.info("Using container espeak-ng data path: %s", data_path)
        except Exception as exc:
            logger.warning("Could not mirror espeak-ng data into app container: %s", exc)

    os.environ["PHONEMIZER_ESPEAK_DATA_PATH"] = str(data_path)
    os.environ["PHONEMIZER_ESPEAK_LIBRARY"] = str(library_path)
    os.environ["ESPEAK_DATA_PATH"] = str(data_path)

    try:
        import espeakng_loader

        espeakng_loader.get_data_path = lambda: str(data_path)
        espeakng_loader.get_library_path = lambda: str(library_path)
        logger.info("Pinned frozen espeak-ng data path: %s", data_path)
    except Exception as exc:
        logger.warning("Could not patch espeakng_loader paths: %s", exc)

    if sys.platform == "darwin":
        _patch_frozen_phonemizer_espeak_api()


def _patch_frozen_phonemizer_espeak_api() -> None:
    """Avoid loading copied espeak dylibs from sandbox-writable temp dirs.

    `phonemizer.backend.espeak.api.EspeakAPI` normally copies libespeak-ng into
    a fresh temp directory before calling `dlopen`. That is reasonable on
    unconstrained systems, but a sandboxed, hardened macOS app is not allowed to
    load executable code from the writable app-container temp directory. In the
    packaged app the original dylib already lives in the signed PyInstaller
    bundle, so load that bundled dylib in place instead.
    """
    try:
        import ctypes

        from phonemizer.backend.espeak import api as espeak_api
    except Exception as exc:
        logger.warning("Could not patch phonemizer espeak API: %s", exc)
        return

    if getattr(espeak_api.EspeakAPI, "_openreader_frozen_patch", False):
        return

    original_shared_library_path = espeak_api.EspeakAPI._shared_library_path

    def init_without_temp_copy(self, library, data_path):
        self._library = None

        if data_path is None:
            data_path = os.environ.get("PHONEMIZER_ESPEAK_DATA_PATH") or os.environ.get(
                "ESPEAK_DATA_PATH"
            )

        if data_path is not None:
            data_path_path = Path(os.fsdecode(data_path)).resolve()
            if not (data_path_path / "phontab").exists():
                logger.warning("Frozen espeak data path is missing phontab: %s", data_path_path)
            else:
                logger.info("Initializing frozen espeak with data path: %s", data_path_path)
            data_path = os.fsencode(data_path_path)
        else:
            logger.warning("Frozen espeak API initialized without an explicit data path")

        try:
            loaded_library = ctypes.cdll.LoadLibrary(str(library))
            library_path = original_shared_library_path(loaded_library)
        except OSError as error:
            raise RuntimeError(f"failed to load espeak library: {error}") from None

        self._tempdir = None
        self._library = loaded_library
        try:
            self._library.espeak_Initialize.argtypes = [
                ctypes.c_int,
                ctypes.c_int,
                ctypes.c_char_p,
                ctypes.c_int,
            ]
            self._library.espeak_Initialize.restype = ctypes.c_int
            if self._library.espeak_Initialize(0x02, 0, data_path, 0) <= 0:
                raise RuntimeError("failed to initialize espeak shared library")
        except AttributeError:
            raise RuntimeError("failed to load espeak library") from None

        self._library_path = library_path

    espeak_api.EspeakAPI.__init__ = init_without_temp_copy
    espeak_api.EspeakAPI._openreader_frozen_patch = True
    logger.info("Patched phonemizer espeak API for frozen macOS sandbox")



_configure_frozen_espeak()


def main() -> int:
    from misaki.espeak import EspeakFallback, EspeakG2P

    engines: dict[tuple[str, str], object] = {}
    for line in sys.stdin:
        try:
            request = json.loads(line)
            mode = request["mode"]
            text = request["text"]
            if not isinstance(text, str) or len(text) > 100_000:
                raise ValueError("text must be a string of at most 100000 characters")
            if mode == "fallback":
                british = request["british"] is True
                key = (mode, "en-gb" if british else "en-us")
                if key not in engines:
                    engines[key] = EspeakFallback(british=british)
                engine = engines[key]
                token = type("TextToken", (), {"text": text})()
                phonemes, rating = engine(token)
            elif mode == "g2p":
                language = request["language"]
                if language not in {"es", "fr-fr", "hi", "it", "pt-br"}:
                    raise ValueError("unsupported language")
                key = (mode, language)
                if key not in engines:
                    engines[key] = EspeakG2P(language=language)
                engine = engines[key]
                phonemes, rating = engine(text)
            else:
                raise ValueError("unsupported mode")
            response = {"phonemes": phonemes, "rating": rating}
        except Exception as exc:
            response = {"error": str(exc)}
        sys.stdout.write(json.dumps(response, ensure_ascii=False) + "\n")
        sys.stdout.flush()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
