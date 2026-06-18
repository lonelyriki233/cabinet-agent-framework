
from __future__ import annotations
from pathlib import Path
from datetime import datetime
import json
from typing import Any

from .model import ROOT, RUNTIME, STATE, read_json, write_json

HOOKS_DIR = RUNTIME / "hooks"
EVENTS = HOOKS_DIR / "events.jsonl"
LIFECYCLE = HOOKS_DIR / "lifecycle"

RISK_TERMS = [".env", "token", "auth", "secret", "password", "生产部署", "数据库迁移", "大规模删除", "主分支", "merge", "账单"]


def _ts() -> str:
    return datetime.now().isoformat(timespec="seconds")


def ensure_hooks() -> None:
    HOOKS_DIR.mkdir(parents=True, exist_ok=True)
    LIFECYCLE.mkdir(parents=True, exist_ok=True)
    if not EVENTS.exists():
        EVENTS.write_text("", encoding="utf-8")


def _rel(p: Path) -> str:
    try:
        return str(p.relative_to(ROOT))
    except Exception:
        return str(p)


def _rooted(path: str) -> Path:
    p = Path(path)
    return p if p.is_absolute() else ROOT / p


def emit_hook(event: str, result: str = "pass", task: dict | None = None, details: dict | None = None) -> dict:
    ensure_hooks()
    task_id = (task or {}).get("task_id") or "global"
    record = {
        "ts": _ts(),
        "event": event,
        "result": result,
        "task_id": task_id,
        "worker": (task or {}).get("worker"),
        "task_type": (task or {}).get("task_type"),
        "details": details or {},
    }
    with EVENTS.open("a", encoding="utf-8") as f:
        f.write(json.dumps(record, ensure_ascii=False) + "\n")
    lifecycle_file = LIFECYCLE / f"{task_id}.json"
    lifecycle = read_json(lifecycle_file, []) or []
    lifecycle.append(record)
    write_json(lifecycle_file, lifecycle)
    state = read_json(STATE / "project.json", {}) or {}
    state["last_hook"] = record
    if result in {"fail", "blocked"}:
        state.setdefault("blockers", []).append({"hook": event, "task_id": task_id, "details": details or {}})
    write_json(STATE / "project.json", state)
    return record


def hook_task_created(task: dict) -> dict:
    return emit_hook("task.created", "pass", task, {"status": task.get("status"), "required_outputs": task.get("required_outputs", [])})


def _path_allowed(path: str, allowed_paths: list[str]) -> bool:
    norm = path.replace("\\", "/").lstrip("/")
    allowed = [a.replace("\\", "/").rstrip("/") for a in allowed_paths]
    return any(norm == a or norm.startswith(a + "/") for a in allowed)


def hook_before_task_run(task: dict) -> tuple[bool, dict]:
    problems: list[str] = []
    allowed = task.get("allowed_paths", [])
    for out in task.get("required_outputs", []):
        if not _path_allowed(out, allowed):
            problems.append(f"required output outside allowed paths: {out}")
    text = "\n".join(str(task.get(k, "")) for k in ["title", "objective", "context"])
    auth = task.get("authority_level", "L1")
    if auth in {"L0", "L1", "L2"}:
        touched = [term for term in RISK_TERMS if term.lower() in text.lower()]
        # Mentioning forbidden paths in the explicit forbidden list is fine; risky user intent is not.
        if touched and any(term not in str(task.get("forbidden_paths", [])) for term in touched):
            problems.append("risk terms in task intent under insufficient authority: " + ", ".join(touched))
    if problems:
        rec = emit_hook("task.before_run", "blocked", task, {"problems": problems})
        return False, rec
    rec = emit_hook("task.before_run", "pass", task, {"mode": "scope_and_risk_checked"})
    return True, rec


def hook_after_task_run(task: dict, mode: str, run_result: str) -> tuple[bool, dict]:
    status = task.get("status")
    details: dict[str, Any] = {"mode": mode, "status": status, "run_result": run_result}
    if mode == "prompt":
        return True, emit_hook("task.after_run", "pass", task, details | {"note": "prompt mode does not require output yet"})
    if status == "done":
        missing = [out for out in task.get("required_outputs", []) if not _rooted(out).exists()]
        details["missing_outputs"] = missing
        if missing:
            return False, emit_hook("task.after_run", "fail", task, details)
    return True, emit_hook("task.after_run", "pass" if status != "failed" else "fail", task, details)


def hook_before_archive(task: dict) -> tuple[bool, dict]:
    missing = [out for out in task.get("required_outputs", []) if not _rooted(out).exists()]
    if missing:
        return False, emit_hook("archive.before_index", "blocked", task, {"missing_outputs": missing})
    return True, emit_hook("archive.before_index", "pass", task, {"outputs": task.get("required_outputs", [])})


def hook_after_archive(task: dict, indexed: list[Any]) -> dict:
    return emit_hook("archive.after_index", "pass", task, {"indexed_count": len(indexed)})


def hook_audit_written(task: dict, audit_path: Path, result: str) -> dict:
    return emit_hook("audit.written", "pass" if result == "pass" else "fail", task, {"audit_path": _rel(audit_path), "audit_result": result})


def hook_stop_gate(cycle: int | None = None) -> tuple[bool, dict]:
    ensure_hooks()
    # Stop if the last 3 task.after_run events failed/blocked. This prevents overnight loops from grinding on broken work.
    records = []
    if EVENTS.exists():
        for line in EVENTS.read_text(encoding="utf-8").splitlines()[-20:]:
            try:
                records.append(json.loads(line))
            except Exception:
                pass
    recent = [r for r in records if r.get("event") in {"task.after_run", "task.before_run"}]
    tail = recent[-3:]
    if len(tail) == 3 and all(r.get("result") in {"fail", "blocked"} for r in tail):
        rec = emit_hook("dispatcher.stop_gate", "blocked", None, {"cycle": cycle, "reason": "three consecutive failed/blocked task hooks"})
        return False, rec
    rec = emit_hook("dispatcher.stop_gate", "pass", None, {"cycle": cycle})
    return True, rec


def lifecycle_for(task_id: str) -> list[dict]:
    ensure_hooks()
    return read_json(LIFECYCLE / f"{task_id}.json", []) or []


def recent_events(limit: int = 50) -> list[dict]:
    ensure_hooks()
    rows = []
    for line in EVENTS.read_text(encoding="utf-8").splitlines()[-limit:]:
        try:
            rows.append(json.loads(line))
        except Exception:
            pass
    return rows
