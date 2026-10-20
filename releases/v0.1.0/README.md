# Helper source for OpenReader 0.1.0 — 2026-10-20

This source release is associated with the Developer ID-signed arm64 DMG built
on 2026-10-20. The parent DMG SHA-256 is
`d801ba3a9d9fbde673c1a6bc4a9304943732782e03a9680f58caa6891bac4b3e`.
The app binary itself is not distributed by this repository.

The source archive is `OpenReader-0.1.0-phonemizer-source.tar.gz`, SHA-256
`44f8a1b669daf5e4d992bb99dabaf4edc82e45ed3b5b0d688cf9d0cf9deefffe`.
It was generated after signing and verified against the helper installed from
the completed, notarized DMG. Its manifest includes the helper executable hash
and the type, symlink target, and file hash inventory for its entire directory.
`helper-build-manifest.json` preserves the same manifest for direct inspection.

From a checkout of this tag, verify a downloaded archive with CPython 3.12+:

```sh
python3 scripts/verify_release.py OpenReader-0.1.0-phonemizer-source.tar.gz
```

Optionally verify the complete helper from an installed matching app:

```sh
python3 scripts/verify_release.py OpenReader-0.1.0-phonemizer-source.tar.gz \
  --helper-dir /Applications/OpenReader.app/Contents/Resources/backend/phonemizer-helper
```

The verifier reads the source archive without extracting or executing it. A
different signed helper or a rebuilt helper is expected to fail the exact
binary/distribution comparison even if its source version is the same.

The original `server.py`, `build.py`, and `__init__.py` in this repository match
the archive byte-for-byte. The standalone environment and smoke/verification
tools were added for this public source repository. A minimal clean-environment
rebuild passed the same protocol checks from source and as a frozen executable:
English US/UK, Spanish, French, Hindi, Italian, Brazilian Portuguese, invalid
mode/language and oversized-text rejection, followed by successful recovery.

This release establishes verified public helper source hosting. It does not
claim approval of the parent app's complete corresponding-source scope, all
native build provenance, LGPL relinking, or Mac App Store terms. A later Mac
App Store candidate must undergo its own matching-source verification.
