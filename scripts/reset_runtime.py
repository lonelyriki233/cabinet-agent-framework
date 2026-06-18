#!/usr/bin/env python3
from pathlib import Path
import shutil

ROOT = Path(__file__).resolve().parents[1]
RUNTIME = ROOT / "runtime"
KEEP = ["tasks", "outputs", "reports", "logs", "state", "archive", "audits"]

if RUNTIME.exists():
    shutil.rmtree(RUNTIME)
for name in KEEP:
    (RUNTIME / name).mkdir(parents=True, exist_ok=True)
(RUNTIME / "README.md").write_text(
    "Runtime reset. New tasks should be created by user intake.\n",
    encoding="utf-8",
)
print(f"RESET_OK {RUNTIME}")
