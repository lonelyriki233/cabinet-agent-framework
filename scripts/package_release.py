#!/usr/bin/env python3
from __future__ import annotations
from pathlib import Path
import shutil, subprocess, sys, zipfile
ROOT = Path(__file__).resolve().parents[1]
DIST = ROOT / 'dist'
NAME = 'cabinet-agent-framework-0.1.0.zip'
EXCLUDE_DIRS={'.git','__pycache__','.pytest_cache','.ruff_cache','.mypy_cache','dist','build'}
EXCLUDE_PREFIXES=('runtime/state/','runtime/tasks/','runtime/logs/','runtime/hooks/','runtime/archive/','runtime/audits/','runtime/reports/','runtime/outputs/','runtime/rag/')

def run(cmd):
    result=subprocess.run(cmd, cwd=ROOT, text=True, capture_output=True, timeout=300)
    print(result.stdout.strip())
    if result.stderr.strip(): print(result.stderr.strip(), file=sys.stderr)
    if result.returncode != 0: raise SystemExit(result.returncode)

def include(p: Path) -> bool:
    rel=p.relative_to(ROOT).as_posix()
    if any(part in EXCLUDE_DIRS for part in p.parts): return False
    if any(rel.startswith(prefix) for prefix in EXCLUDE_PREFIXES): return False
    if p.suffix in {'.pyc'}: return False
    if p.name in {'.env','auth.json','credentials.json'}: return False
    return True

def main() -> int:
    run([sys.executable, '-m', 'unittest', 'discover', '-s', 'tests', '-v'])
    run([sys.executable, 'scripts/public_audit.py'])
    run([sys.executable, '-m', 'cabinet_framework.cli', 'gate'])
    DIST.mkdir(exist_ok=True)
    out=DIST/NAME
    if out.exists(): out.unlink()
    with zipfile.ZipFile(out, 'w', zipfile.ZIP_DEFLATED) as zf:
        for p in sorted(ROOT.rglob('*')):
            if p.is_file() and include(p):
                zf.write(p, p.relative_to(ROOT).as_posix())
    print(f'PACKAGE_CREATED {out} size={out.stat().st_size}')
    return 0
if __name__ == '__main__': raise SystemExit(main())
