# OpenReader pronunciation helper

The GPL-3.0-or-later pronunciation process used by OpenReader's macOS Kokoro
backend. It runs Misaki's eSpeak integration, phonemizer-fork, and eSpeak NG in
a separate process. The interface carries newline-delimited JSON containing
text, a language or English fallback setting, and phoneme results.

This repository publishes the helper implementation, its original freezing
recipe, a standalone build environment, and versioned source materials. The
OpenReader main backend, reader UI, and application repository are not included.

## Release source

Download [the v0.1.0 source materials](https://github.com/patriciobcs/openreader-phonemizer-helper/releases/tag/v0.1.0).
The release provides `OpenReader-0.1.0-phonemizer-source.tar.gz` and
`SHA256SUMS.txt`. The archive includes:

- This helper's original Python source and build recipe.
- Pinned eSpeak NG 1.52.0, phonemizer-fork 3.3.2, and Misaki 0.9.4 sources.
- The exact espeakng-loader 0.2.4 Apple Silicon wheel and extracted Python loader.
- The original parent desktop dependency declarations and lockfile.
- A manifest of all included files and the complete signed helper distribution.

See [the build association](releases/v0.1.0/README.md) for the exact candidate
and verification scope. Future app candidates must verify their helper against
the source materials; the same app version alone is not sufficient evidence.

## Run from source

The tested standalone environment is Apple Silicon macOS 14 or later with
CPython 3.12 and [uv](https://docs.astral.sh/uv/). It does not need model weights
or the OpenReader application. From this repository:

```sh
uv venv --python 3.12
uv pip sync --python .venv/bin/python --require-hashes requirements.txt
.venv/bin/python scripts/smoke.py --python .venv/bin/python
```

For an interactive request:

```sh
printf '%s\n' '{"mode":"fallback","british":false,"text":"Hello world"}' |
  .venv/bin/python -m phonemizer_helper.server
```

The helper writes one JSON response per input line and continues after a
request error. Logs use stderr. No server socket or cloud service is involved.

## Build the standalone macOS helper

Install Xcode command-line tools and the environment above, then run:

```sh
.venv/bin/python phonemizer_helper/build.py
.venv/bin/python scripts/smoke.py \
  --executable dist/openreader-backend/phonemizer-helper/openreader-phonemizer-helper
```

The original build recipe fixes PyInstaller's target architecture to arm64 and
copies eSpeak NG's shared library and data into the distribution. Code signing
and the parent app sandbox are separate release steps. A rebuilt helper is not
expected to have the same executable hash as a signed app candidate: build
paths, tool environments, timestamps, and signatures can differ.

`requirements.txt` pins a minimal standalone environment constrained to the
original build's installed package versions. The exact parent environment is
also preserved in the source release's desktop lockfile. The original app
environment can cause PyInstaller hooks to collect additional optional modules;
the smaller standalone rebuild does not claim byte-for-byte equivalence.

## Protocol

Supported requests:

```json
{"mode":"fallback","british":false,"text":"Hello world"}
{"mode":"fallback","british":true,"text":"Hello world"}
{"mode":"g2p","language":"es","text":"Hola mundo"}
```

The `g2p` languages are `es`, `fr-fr`, `hi`, `it`, and `pt-br`. Successful
responses have `phonemes` and `rating`; errors have `error`. Input text must be
a string of at most 100,000 characters. The helper caches engines by mode and
language for the lifetime of the process.

## License and distribution scope

First-party helper code is GPL-3.0-or-later; see [LICENSE](LICENSE) and
[NOTICE.md](NOTICE.md). Upstream components retain their own terms.

These source materials establish a public location and a verifiable association
with one signed helper distribution. They do not certify the full application's
corresponding-source scope, LGPL relinking arrangements, unresolved upstream
loader provenance, or Mac App Store compatibility. The independent process
boundary is a technical fact; distribution review remains separate.
