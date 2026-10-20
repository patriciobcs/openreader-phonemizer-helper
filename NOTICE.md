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
- espeakng-loader 0.2.4: its Python loader is MIT, identified in upstream commit
  0ddc87adf77e5850d7eeb542ac8a87d421b64daa. See
  `licenses/ESPEAKNG-LOADER-MIT.txt`. The eSpeak library/data retain GPL terms.
  <https://github.com/thewh1teagle/espeakng-loader>
- PyInstaller 6.22.2: GPL-2.0-or-later with its bootloader exception.
  <https://pyinstaller.org/en/stable/license.html>
- CPython 3.12: Python Software Foundation license and bundled third-party
  terms. <https://docs.python.org/3.12/license.html>

The exact source archive preserves upstream license files. Build dependency
versions and artifact hashes are recorded in `requirements.txt`; they do not
replace each dependency's own license. The archive's original `NOTICE.md` and
desktop metadata are a parent-project build snapshot, not publication of the
OpenReader application source. No main backend or frontend source is included.

`licenses/PHONEMIZER-DEPENDENCIES.txt` contains the collected dependency notices.
The source archive also contains per-package notice files and an inventory,
all frozen Python source, native source/build materials and their provenance.
GPL rights apply to the helper copy bundled in the app as well as this source.
