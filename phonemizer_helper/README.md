# OpenReader phonemizer helper

This is the separately packaged pronunciation process used by the macOS Kokoro
backend. It invokes Misaki's eSpeak integration, `phonemizer-fork`, and eSpeak NG.
The helper is GPL-3.0-or-later; see [LICENSE](LICENSE). The main macOS backend
communicates with it through standard input and output. Each input line is a
JSON object containing plain text and either an English fallback setting or a
language code; each output line contains phonemes and a rating, or an error.

The helper source is `server.py` and its frozen build recipe is `build.py`.
The client is `../backend/backends/phonemizer_proxy.py`, and the pinned Python
package versions are in `../uv.lock`. Run `bun run build:backend` at the repository root to build both
the main backend and the helper. The macOS app build copies and signs the helper
inside the app bundle.

## Public source and independent build

The source repository and versioned archives are available without login:
https://github.com/patriciobcs/openreader-phonemizer-helper/releases

After extracting a source archive, use an arm64 Mac running macOS 14 or later,
CPython 3.12, Xcode command-line tools and uv. From the extracted archive root:

```sh
uv venv --python 3.12
uv pip sync --python .venv/bin/python --require-hashes phonemizer_helper/requirements.txt
.venv/bin/python -m phonemizer_helper.build
```

The helper is produced at
`dist/openreader-backend/phonemizer-helper/openreader-phonemizer-helper`.
Run that executable and send one JSON request per line on stdin, for example
`{"mode":"fallback","british":false,"text":"Hello world"}` or
`{"mode":"g2p","language":"es","text":"Hola mundo"}`. It returns phonemes on
stdout; diagnostics use stderr. You can run the helper independently of
OpenReader, modify its source and redistribute it under the GPL. No proprietary
OpenReader license or signing key is needed for standalone development/use.

The hash-pinned requirements describe the tested minimal standalone build.
The original desktop lockfile is also included in the archive. The original
larger environment caused freezing hooks to collect additional optional
modules; an independent rebuild need not be byte-identical or collect the
same optional modules. The archive nevertheless provides source for the exact
modules in its associated shipped helper.

## Contents and matching-source verification

The release packager is `../scripts/release/package-phonemizer-source.py` in
the application checkout. Its downloads directory must contain the four core
inputs plus every archive pinned in `source-dependencies.json`. Creating the
archive uses the Python 3.12 desktop environment with PyInstaller installed:

```sh
.venv/bin/python scripts/release/package-phonemizer-source.py \
  --backend /path/to/the/signed/app/Contents/Resources/backend \
  --downloads /path/to/upstream/downloads --output /path/to/helper-source.tar.gz
.venv/bin/python scripts/release/package-phonemizer-source.py \
  --verify --backend /path/to/the/signed/app/Contents/Resources/backend \
  --output /path/to/helper-source.tar.gz
```

Run those commands from `apps/desktop` in the application checkout. Pass
`--analysis` if the matching PyInstaller `Analysis-*.toc` is elsewhere.
The archive contains the following independently inspectable materials:

- This GPL helper implementation, original build recipe and standalone requirements.
- Source archives for all frozen Python distributions and the freezing tools.
- Exact Python source for all PYZ, bootstrap and base-library modules, with a
  coverage map verified by compiling the source and comparing code objects.
- eSpeak release and loader-pinned source, the MIT loader source, original
  loader wheel, OpenBLAS source/build recipes, CPython source, and GCC 11.3
  source plus its macOS build recipe and patches.
- The associated GCC native-runtime section hashes, verified independently of
  code-signing changes; `native-provenance.json` records their origin.
- License/copyright notices and hashes for the supplied dependency materials.
- A manifest identifying the exact helper executable and every distribution file.

The GCC recipe archive contains `info/recipe/parent/build.sh`, its source
configuration and macOS patches. Its source URL uses gzip; the supplied GCC
11.3.0 upstream source is the equivalent xz-compressed release. The OpenBLAS
source commit is the one named by NumPy 1.26.4's wheel build recipe. Rebuilding
native libraries requires their documented compiler/SDK tools; those are not
private OpenReader components.

Create the final source manifest **after** signing the helper. Signing changes
its executable hash even when its Python code is unchanged. Publish a new
matching archive for changed distributions and preserve older source releases.
The main OpenReader frontend and backend application source are not included.
The owner retains Kokoro and this process architecture in both release channels.
