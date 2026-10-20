#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later
"""Verify a downloaded source archive and, optionally, a signed helper tree."""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import runpy
import tarfile
from pathlib import Path, PurePosixPath

ROOT = Path(__file__).resolve().parent.parent


def digest(path: Path) -> str:
    with path.open('rb') as source:
        return hashlib.file_digest(source, 'sha256').hexdigest()


def inventory(helper: Path) -> dict:
    root = helper.resolve(strict=True)
    result = {}
    for item in sorted(helper.rglob('*')):
        name = item.relative_to(helper).as_posix()
        if item.is_symlink():
            resolved = item.resolve(strict=True)
            relative = resolved.relative_to(root).as_posix()
            entry = {'type': 'symlink', 'target': os.readlink(item), 'resolved': relative}
            if resolved.is_file():
                entry['sha256'] = digest(resolved)
            elif not resolved.is_dir():
                raise ValueError(f'Unsupported symlink target: {name}')
            result[name] = entry
        elif item.is_file():
            result[name] = {'type': 'file', 'sha256': digest(item)}
        elif not item.is_dir():
            raise ValueError(f'Unsupported helper entry: {name}')
    return result


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('archive', type=Path)
    parser.add_argument('--helper-dir', type=Path)
    parser.add_argument('--release', default='v0.1.1', choices=['v0.1.0', 'v0.1.1'])
    args = parser.parse_args()
    release = json.loads((ROOT / 'releases' / args.release / 'release.json').read_text())
    if digest(args.archive) != release['sourceArchive']['sha256']:
        raise ValueError('Downloaded source archive SHA-256 differs from the pinned release')
    prefix = 'openreader-phonemizer-source/'
    with tarfile.open(args.archive, 'r:gz') as archive:
        members = archive.getmembers()
        names = [item.name for item in members]
        if len(names) != len(set(names)):
            raise ValueError('Duplicate archive paths')
        for member in members:
            if not member.isfile() or not member.name.startswith(prefix):
                raise ValueError('Unexpected archive member: ' + member.name)
            relative = member.name[len(prefix):]
            parts = relative.split('/')
            if '\\' in relative or ':' in relative or any(part in {'', '.', '..'} for part in parts):
                raise ValueError('Noncanonical archive path: ' + relative)
            if PurePosixPath(relative).as_posix() != relative:
                raise ValueError('Noncanonical archive path: ' + relative)
        source = json.load(archive.extractfile(prefix + 'manifest.json'))
        expected_names = {prefix + name for name in source['files']} | {prefix + 'manifest.json'}
        if set(names) != expected_names:
            raise ValueError('Source manifest differs from archive contents')
        if source['helper_binary_sha256'] != release['helperBinarySha256']:
            raise ValueError('Helper build association differs from the release record')
        for name, expected in source['files'].items():
            handle = archive.extractfile(prefix + name)
            if hashlib.file_digest(handle, 'sha256').hexdigest() != expected:
                raise ValueError('Source checksum mismatch: ' + name)
        for name, expected in release['runtimeSourceSha256'].items():
            if source['files'].get(name) != expected or digest(ROOT / name) != expected:
                raise ValueError('Repository helper runtime differs from release source: ' + name)
        if args.helper_dir:
            helper = args.helper_dir
            if digest(helper / 'openreader-phonemizer-helper') != release['helperBinarySha256']:
                raise ValueError('Selected helper executable differs from the signed candidate')
            if inventory(helper) != source['helper_distribution']:
                raise ValueError('Selected helper distribution differs from the signed candidate')
            if release.get('sourceCoverage'):
                files = {
                    name: archive.extractfile(prefix + name).read()
                    for name in source['files']
                    if name.startswith(('frozen-sources/', 'phonemizer_helper/'))
                    or name == 'frozen-source-coverage.json'
                }
                verifier = runpy.run_path(str(ROOT / 'phonemizer_helper/source_snapshot.py'))
                verifier['verify_snapshot'](helper.parent, files)
    print('PASS: source archive, all manifest files, repository runtime, and build association')
    if args.helper_dir:
        print('PASS: complete selected signed helper distribution matches the source manifest')
        if release.get('sourceCoverage'):
            print('PASS: every frozen Python module and GCC runtime section matches its source record')


if __name__ == '__main__':
    main()
