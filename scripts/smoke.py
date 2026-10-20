#!/usr/bin/env python3
"""Exercise the actual helper protocol in one process, including recovery."""
from __future__ import annotations

import argparse
import json
import subprocess
import sys


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    target = parser.add_mutually_exclusive_group(required=True)
    target.add_argument('--python')
    target.add_argument('--executable')
    args = parser.parse_args()
    command = [args.executable] if args.executable else [args.python, '-m', 'phonemizer_helper.server']
    requests = [
        {'mode': 'fallback', 'british': False, 'text': 'Hello world'},
        {'mode': 'fallback', 'british': True, 'text': 'Hello world'},
        {'mode': 'g2p', 'language': 'es', 'text': 'Hola mundo'},
        {'mode': 'g2p', 'language': 'fr-fr', 'text': 'Bonjour le monde'},
        {'mode': 'g2p', 'language': 'hi', 'text': 'नमस्ते दुनिया'},
        {'mode': 'g2p', 'language': 'it', 'text': 'Ciao mondo'},
        {'mode': 'g2p', 'language': 'pt-br', 'text': 'Olá mundo'},
        {'mode': 'g2p', 'language': 'unsupported', 'text': 'Reject this'},
        {'mode': 'fallback', 'british': False, 'text': 'x' * 100001},
        {'mode': 'unknown', 'text': 'Reject this'},
        {'mode': 'g2p', 'language': 'es', 'text': 'La recuperación funciona'},
    ]
    result = subprocess.run(
        command,
        input='\n'.join(json.dumps(request, ensure_ascii=False) for request in requests) + '\n',
        text=True,
        capture_output=True,
        timeout=120,
    )
    if result.returncode:
        sys.stderr.write(result.stderr)
        raise SystemExit(f'Helper exited with {result.returncode}')
    lines = result.stdout.splitlines()
    if len(lines) != len(requests):
        raise SystemExit(f'Expected {len(requests)} protocol replies, received {len(lines)}')
    for index, line in enumerate(lines):
        response = json.loads(line)
        if index in {7, 8, 9}:
            if not isinstance(response.get('error'), str):
                raise SystemExit(f'Request {index + 1}: invalid input was not rejected')
        elif not isinstance(response.get('phonemes'), str) or not response['phonemes'].strip():
            raise SystemExit(f'Request {index + 1}: no phonemes: {response}')
    print(f'PASS: {len(requests)} requests: English US/UK, five languages, three rejections, recovery')


if __name__ == '__main__':
    main()
