# Signed helper source associations — v0.1.2

OpenReader application version 0.1.0 has two signed helper distributions. Download
the source archive for your channel; the hashes and parent-artifact associations
are in [release.json](release.json) and [SHA256SUMS.txt](SHA256SUMS.txt).

The helper runtime and build recipe remain unchanged. Each archive contains the
complete frozen Python source coverage, all pinned upstream source/build inputs,
notices, and the exact signed-helper file inventory. No private application code
or signing key is included. Earlier source releases remain unchanged.

Verify an archive and an extracted app's helper with Python 3.12 and the pinned
helper environment:

    .venv/bin/python scripts/verify_release.py ARCHIVE --release v0.1.2 --channel dmg --helper-dir /path/OpenReader.app/Contents/Resources/backend/phonemizer-helper

Use `--channel app-store` for the Store archive. To verify only the public
archive and its contents, omit `--helper-dir`. An installed Store-processed
copy may have Apple-applied signing changes; these records identify the signed
submission candidate, not an assertion that Apple keeps every file byte unchanged.

Other covered-library source and personal modification instructions are at
https://catalog.openreader.io/compliance/index.html . App Review and outside beta
acceptance remain separate from source verification.
