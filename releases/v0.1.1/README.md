# Source package v0.1.1 for OpenReader 0.1.0

This expands the source materials for the same signed Developer ID helper
identified by v0.1.0. No runtime implementation or bundled dependency changed.
The earlier tag and archive remain available unchanged.

The archive includes all frozen Python source, dependency source archives and
notices, native source/build recipes, the MIT loader license, and explicit GPL
rights for the helper copy supplied inside the app. See `release.json` for
checksums and coverage counts. It does not include private application code.

Download the archive and `SHA256SUMS.txt` from the release. From this repository:

```sh
shasum -a 256 -c SHA256SUMS.txt
python3 scripts/verify_release.py /path/to/OpenReader-0.1.0-phonemizer-source-v2.tar.gz
```

To additionally check the signed helper's entire file tree and compiled Python
source, use the pinned Python 3.12 build environment with PyInstaller/macholib:

```sh
.venv/bin/python scripts/verify_release.py \
  /path/to/OpenReader-0.1.0-phonemizer-source-v2.tar.gz \
  --helper-dir /path/to/OpenReader.app/Contents/Resources/backend/phonemizer-helper
```

The check covers the complete signed helper distribution and all PYZ, bootstrap
and base-library modules. It also compares the GCC runtime's compiled arm64
sections with the recorded upstream build. The native material is not a claim
of a bit-identical rebuild of every library. Independent build instructions are
in the repository README and `phonemizer_helper/README.md`.

This source package is associated with the October 20 Developer ID candidate.
Future DMG and App Store candidates need their own final signed-helper manifest.
Publishing this package does not submit an application to Apple.
