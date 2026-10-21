# Signed helper source associations — v0.1.3

OpenReader 0.1.2 has separate signed DMG and Mac App Store helper
distributions. Choose your channel's source archive. Exact hashes, parent-binary
associations and measured frozen-source coverage are in [release.json](release.json)
and [SHA256SUMS.txt](SHA256SUMS.txt).

The helper runtime and build recipe are unchanged. The environment includes the
security-updated dependencies. Each archive contains complete frozen Python
source coverage, pinned upstream source/build inputs, notices and the exact
signed-helper inventory. No private application source or signing key is included.
Earlier source releases remain available.

Verify using Python 3.12 and the pinned helper environment:

    .venv/bin/python scripts/verify_release.py ARCHIVE --release v0.1.3 --channel dmg --helper-dir /path/OpenReader.app/Contents/Resources/backend/phonemizer-helper

Use `--channel app-store` for the Store archive. Omit `--helper-dir` to check
only the public source archive. Apple may apply signing changes to processed
Store copies; the associations identify the signed submission candidate, without
claiming byte-identical rebuilding or Apple processing.

Other covered-library source and personal-copy modification instructions:
https://catalog.openreader.io/compliance/index.html . Apple review and outside
beta acceptance are separate from source verification.
