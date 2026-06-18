#!/usr/bin/env python3
from __future__ import annotations
from pathlib import Path
import json, re, sys
ROOT = Path(__file__).resolve().parents[1]
SOURCES = [ROOT/'memory', ROOT/'skills', ROOT/'docs', ROOT/'templates', ROOT/'adapters']
OUT = ROOT/'runtime'/'rag'/'keyword_index.jsonl'

def tokens(text: str) -> list[str]:
    return [t.lower() for t in re.findall(r"[A-Za-z0-9_\-]{3,}|[\u4e00-\u9fff]{2,}", text)]

def main() -> int:
    OUT.parent.mkdir(parents=True, exist_ok=True)
    rows=[]
    for base in SOURCES:
        if not base.exists():
            continue
        for p in base.rglob('*'):
            if p.is_file() and p.suffix.lower() in {'.md','.txt','.json','.yaml','.yml'}:
                text=p.read_text(encoding='utf-8', errors='ignore')
                freq={}
                for tok in tokens(text): freq[tok]=freq.get(tok,0)+1
                rows.append({'path': str(p.relative_to(ROOT)), 'token_count': sum(freq.values()), 'top_terms': sorted(freq, key=freq.get, reverse=True)[:30]})
    OUT.write_text('\n'.join(json.dumps(r, ensure_ascii=False) for r in rows)+'\n', encoding='utf-8')
    print(f'INDEXED {len(rows)} files -> {OUT.relative_to(ROOT)}')
    return 0
if __name__ == '__main__': raise SystemExit(main())
