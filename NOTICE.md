# OpenReader notices

Copyright © 2026 Patricio Bastian Calderon Sanhueza. Owner-distributed application
binaries use the terms in [OPENREADER-BINARY-LICENSE.txt](licenses/OPENREADER-BINARY-LICENSE.txt).
The main application source remains private at launch. Source copies separately
provided under the AGPL retain that grant in [LICENSE](LICENSE). See
[LICENSING.md](LICENSING.md) for the distribution policy.

OpenReader uses third-party code and assets under their own licenses. The
maintained top-level inventory is [THIRD_PARTY_LICENSES.md](THIRD_PARTY_LICENSES.md).
The OpenReader copyright and AGPL grant do not replace those third-party terms.

No proprietary restriction imposed by OpenReader's owner applies to the
separately licensed GPL helper or overrides other component-license rights.
The helper, including the copy inside this app, may be copied, modified and
redistributed under GPL-3.0-or-later. See
[THIRD-PARTY-RIGHTS.txt](licenses/THIRD-PARTY-RIGHTS.txt) and the complete
component texts in
[PHONEMIZER-DEPENDENCIES.txt](licenses/PHONEMIZER-DEPENDENCIES.txt).

The application-wide component copyright and license texts are in
[APPLICATION-DEPENDENCIES.txt](licenses/APPLICATION-DEPENDENCIES.txt).
Matching covered-library source and native build materials are available without
login at https://catalog.openreader.io/compliance/index.html . The bundled
[library modification instructions](licenses/LGPL-LIBRARY-MODIFICATION.md)
describe replacing LGPL libraries in a personal application copy. Num2words,
pycountry and soxr Python source remains editable outside the backend archive;
native LGPL libraries remain separately replaceable. These component rights do
not require OpenReader's private application source or publisher signing key.

## GPL speech components in desktop builds

- `phonemizer-fork` is licensed GPL-3.0-or-later and credits Mathieu Bernard
  for the underlying phonemizer work. Its published source distribution and
  license metadata are at <https://pypi.org/project/phonemizer-fork/>.
- eSpeak NG, including the shared library and language data packaged through
  `espeakng-loader`, is licensed GPL-3.0-or-later. Its project, source, and
  copyright notices are at <https://github.com/espeak-ng/espeak-ng>.
- The espeakng-loader 0.2.4 Python wrapper is MIT-licensed, matching upstream
  commit `0ddc87adf77e5850d7eeb542ac8a87d421b64daa`. Its copyright and permission
  text are in [ESPEAKNG-LOADER-MIT.txt](licenses/ESPEAKNG-LOADER-MIT.txt).

The GNU GPL version 3 text is included in [licenses/GPL-3.0.txt](licenses/GPL-3.0.txt)
and in the Mac app's `Contents/SharedSupport` directory.
The Apache 2.0 text for Apache-licensed dependencies is included in
[licenses/APACHE-2.0.txt](licenses/APACHE-2.0.txt) and the same app directory.

The macOS build places these components in a separate GPL pronunciation helper
that communicates with the main backend through a text-and-phonemes protocol.
Other desktop platforms may still package them in the main backend. Kokoro uses
them for English pronunciation fallback and for some other languages' G2P.
When distributing a compiled desktop app containing them, provide
the GPL license texts, applicable copyright notices, and the corresponding
source for the distributed version. Public source and standalone build
instructions are available without login at
https://github.com/patriciobcs/openreader-phonemizer-helper/releases.
Choose the source release whose manifest identifies your helper executable
and complete distribution. The package includes the frozen Python source,
dependency source archives, native source/build materials and component
notices. Its source verifier checks the matching executable, complete helper
tree and compiled Python source coverage. A changed or re-signed helper needs
a newly matching distribution manifest.

## Optional model downloads

Model weights download on demand and are not part of the desktop application
bundle. Kokoro and Qwen3 models are listed as Apache-2.0 in the pinned model
cards. Voxtral TTS is listed as CC BY-NC 4.0; Higgs Audio v2 generation materials
and its required tokenizer use the Boson community license incorporating Meta terms.
Both macOS distribution channels provide links to the model terms
before download. Boson AI USA, Inc. owns the Higgs Materials, and Meta Platforms,
Inc. owns the underlying Meta Llama 3 materials. The complete Boson and Meta
agreements are included in [licenses/BOSON-HIGGS-AUDIO-2.txt](licenses/BOSON-HIGGS-AUDIO-2.txt)
and [licenses/META-LLAMA-3.txt](licenses/META-LLAMA-3.txt).

Voxtral TTS was developed by Mistral AI and is used here through the
`mlx-community/Voxtral-4B-TTS-2603-mlx-4bit` quantized conversion. The model
and reference voices are under [CC BY-NC 4.0](https://creativecommons.org/licenses/by-nc/4.0/).
OpenReader does not modify the downloaded weights. See the
[original model card](https://huggingface.co/mistralai/Voxtral-4B-TTS-2603)
and [MLX conversion](https://huggingface.co/mlx-community/Voxtral-4B-TTS-2603-mlx-4bit).

Meta Llama 3 is licensed under the Meta Llama 3 Community License, Copyright © Meta Platforms, Inc. All Rights Reserved.
Boson Higgs Audio 2 is licensed under the Boson Community License, Copyright © Boson AI USA, Inc. All Rights Reserved.

Parakeet audiobook alignment/transcription is based on Parakeet by NVIDIA and
Suno, licensed under [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/).
OpenReader uses the [MLX conversion](https://huggingface.co/mlx-community/parakeet-tdt_ctc-110m)
at revision `d62547387c356a1ab6bb3d85d98b2103f655282e` of the
[original model](https://huggingface.co/nvidia/parakeet-tdt_ctc-110m). The
conversion changes the model format for MLX; OpenReader does not modify the
downloaded weights. The human-audiobook interface identifies this model and its
terms before first use/download.

Built with Higgs Materials licensed from Boson AI USA, Inc., Copyright Boson AI USA, Inc., All Rights Reserved and Meta Llama 3 licensed under the Meta Llama 3 Community License, Copyright Meta Platforms, Inc., All Rights Reserved; based on Meta Llama 3.
See [THIRD_PARTY_LICENSES.md](THIRD_PARTY_LICENSES.md) for the exact model
repositories and license links. Availability in OpenReader does not change a
model owner's license or grant permission beyond that license.
