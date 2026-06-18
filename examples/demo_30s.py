#!/usr/bin/env python3
from __future__ import annotations
from pathlib import Path
import subprocess, sys
ROOT = Path(__file__).resolve().parents[1]

def run(cmd: list[str]) -> None:
    print('$', ' '.join(cmd))
    result = subprocess.run(cmd, cwd=ROOT, text=True, capture_output=True, timeout=120)
    if result.stdout.strip(): print(result.stdout.strip())
    if result.stderr.strip(): print(result.stderr.strip(), file=sys.stderr)
    if result.returncode != 0: raise SystemExit(result.returncode)

def main() -> int:
    run([sys.executable, 'scripts/reset_runtime.py'])
    run([sys.executable, '-m', 'cabinet_framework.cli', 'init'])
    run([sys.executable, '-m', 'cabinet_framework.cli', 'chat-intake', '--authority', 'L2', '--request', 'Demo: build a portable agent framework task with memory, skills, hooks, adapters and dashboard evidence'])
    run([sys.executable, 'scripts/build_keyword_index.py'])
    run([sys.executable, '-m', 'cabinet_framework.cli', 'gate'])
    print('\nOpen dashboard: python3 -m cabinet_framework.cli dashboard --host 127.0.0.1 --port 8788')
    return 0
if __name__ == '__main__': raise SystemExit(main())
