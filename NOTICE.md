# OpenReader pronunciation helper notices

Copyright © 2026 Patricio Bastian Calderon Sanhueza.

The first-party helper implementation and build recipe are licensed under
GPL-3.0-or-later. The full GPL version 3 text is in `LICENSE`.

Third-party components retain their own copyright notices and terms:

- phonemizer-fork 3.3.2: GPL-3.0-or-later, based on Mathieu Bernard's phonemizer.
  <https://pypi.org/project/phonemizer-fork/>
- eSpeak NG 1.52.0 library and pronunciation data: GPL-3.0-or-later.
  <https://github.com/espeak-ng/espeak-ng>
- Misaki 0.9.4: Apache-2.0. <https://github.com/hexgrad/misaki>
- espeakng-loader 0.2.4 supplies the native eSpeak library/data. Its package
  metadata does not declare a license for the Python loader itself; its exact
  wheel and extracted loader source are provided in the source release for
  provenance. This repository does not invent an additional upstream grant.
- PyInstaller 6.22.2: GPL-2.0-or-later with its bootloader exception.
  <https://pyinstaller.org/en/stable/license.html>
- CPython 3.12: Python Software Foundation license and bundled third-party
  terms. <https://docs.python.org/3.12/license.html>

The exact source archive preserves upstream license files. Build dependency
versions and artifact hashes are recorded in `requirements.txt`; they do not
replace each dependency's own license. The archive's original `NOTICE.md` and
desktop metadata are a parent-project build snapshot, not publication of the
OpenReader application source. No main backend or frontend source is included.
