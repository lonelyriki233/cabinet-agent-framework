#!/usr/bin/env python3
from __future__ import annotations
from pathlib import Path
import re, sys
ROOT = Path(__file__).resolve().parents[1]
TEXT_SUFFIXES={'.py','.md','.json','.yaml','.yml','.toml','.html','.txt','.sh'}
SECRET_PATTERNS=[
    re.compile(r'(?i)(api[_-]?key|secret|password|passwd|token)\s*[:=]\s*["\'][^"\']{8,}["\']'),
    re.compile(r'sk-[A-Za-z0-9_-]{20,}'),
    re.compile(r'ghp_[A-Za-z0-9_]{20,}'),
]
LOCAL_PATTERNS=['/mnt' + '/f/', '/home' + '/blj20', 'C:' + '\\Users\\' + 'blj20']
SKIP_PARTS={'.git','__pycache__','dist','build'}

def main() -> int:
    hits=[]
    for p in ROOT.rglob('*'):
        if not p.is_file() or p.suffix.lower() not in TEXT_SUFFIXES: continue
        if any(part in SKIP_PARTS for part in p.parts): continue
        rel=str(p.relative_to(ROOT))
        if rel.startswith('runtime/') and rel != 'runtime/README.md': continue
        text=p.read_text(encoding='utf-8', errors='ignore')
        for marker in LOCAL_PATTERNS:
            if marker in text: hits.append((rel, f'local path marker {marker}'))
        for pat in SECRET_PATTERNS:
            if pat.search(text): hits.append((rel, f'secret-like pattern {pat.pattern[:24]}'))
    if hits:
        for rel, msg in hits: print(f'FAIL {rel}: {msg}')
        return 1
    print('PUBLIC_AUDIT_PASS')
    return 0
if __name__ == '__main__': raise SystemExit(main())
