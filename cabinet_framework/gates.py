from __future__ import annotations
from .model import ROOT, TASKS, read_json

FORBIDDEN_NAMES = [".env", "auth.json", "secret.key"]


def run_gates() -> tuple[bool, list[str]]:
    messages: list[str] = []
    ok = True
    required = [
        "AGENTS.md", "SOUL.md", "USER_INTENT.md", "docs/README.md",
        "docs/core/FRAMEWORK.md", "docs/core/TASK_MODEL.md", "docs/policies/HOOKS_POLICY.md",
        "cabinet_framework/cli.py", "cabinet_framework/governance.py", "cabinet_framework/hooks.py",
        "cabinet_framework/dispatcher.py", "cabinet_framework/worker.py",
    ]
    for rel in required:
        if not (ROOT / rel).exists(): ok = False; messages.append(f"FAIL missing {rel}")
    if ok: messages.append("PASS structure_gate")
    violations=[]
    for p in ROOT.rglob("*"):
        rel = str(p.relative_to(ROOT)).lower()
        if any(name in rel for name in FORBIDDEN_NAMES): violations.append(str(p.relative_to(ROOT)))
    if violations: ok = False; messages.append("FAIL forbidden_paths " + ", ".join(violations))
    else: messages.append("PASS forbidden_path_gate")
    for p in TASKS.glob("*.json"):
        task = read_json(p)
        for key in ["task_id", "worker", "objective", "acceptance_criteria", "required_outputs", "gates"]:
            if key not in task or task[key] in (None, "", []): ok = False; messages.append(f"FAIL task_packet {p.name} missing {key}")
    if ok: messages.append("PASS task_packet_schema_gate")
    return ok, messages
