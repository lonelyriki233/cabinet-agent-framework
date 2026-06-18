from __future__ import annotations
from pathlib import Path
from time import sleep

from .model import TASKS, STATE, read_json, write_json, ensure_runtime
from .worker import run_task
from .governance import should_audit, WORKER_TO_BUREAU
from .secretariat import summarize
from .archive import index_task_outputs
from .hooks import hook_before_archive, hook_after_archive, hook_audit_written, hook_stop_gate, emit_hook


def _audit_task(task: dict) -> dict:
    # lightweight audit note: verify outputs exist and state is consistent
    note = {
        "task_id": task["task_id"],
        "worker": task.get("worker"),
        "task_type": task.get("task_type"),
        "audited_at": None,
        "result": "skip",
        "checks": [],
    }
    checks = []
    for out in task.get("required_outputs", []):
        checks.append((out, (Path(out).exists())))
    note["checks"] = [{"path": p, "exists": ok} for p, ok in checks]
    if all(ok for _, ok in checks):
        note["result"] = "pass"
    else:
        note["result"] = "fail"
    return note


def _append_audit(task: dict, note: dict) -> Path:
    audit_dir = STATE.parent / "audits"
    audit_dir.mkdir(parents=True, exist_ok=True)
    out = audit_dir / f"{task['task_id']}.audit.json"
    note["audited_at"] = task.get("finished_at")
    write_json(out, note)
    return out


def drain_queue(mode: str = "prompt", max_steps: int = 50, audit: bool = True) -> str:
    ensure_runtime()
    emit_hook("dispatcher.started", "pass", None, {"mode": mode, "max_steps": max_steps, "audit": audit})
    steps = []
    for _ in range(max_steps):
        ok, rec = hook_stop_gate()
        if not ok:
            steps.append("STOP_GATE_BLOCKED")
            break
        ready = None
        for p in sorted(TASKS.glob("*.json")):
            t = read_json(p)
            if t and t.get("status") == "ready":
                ready = p
                break
        if not ready:
            break
        result = run_task(ready, mode=mode)
        steps.append(result)
        task = read_json(ready)
        if task and task.get("status") == "done":
            task["finished_at"] = task.get("finished_at") or "now"
            write_json(ready, task)
            ok, rec = hook_before_archive(task)
            if ok:
                indexed = index_task_outputs(task)
                hook_after_archive(task, indexed)
                state = read_json(STATE / "project.json", {}) or {}
                state["archive_indexed"] = int(state.get("archive_indexed", 0)) + len(indexed)
                write_json(STATE / "project.json", state)
            else:
                task["status"] = "failed"
                task["blocker"] = rec.get("details", {})
                write_json(ready, task)
                steps.append("ARCHIVE_HOOK_BLOCKED")
            if audit and should_audit(task.get("task_type", ""), task.get("status", "")):
                note = _audit_task(task)
                audit_path = _append_audit(task, note)
                hook_audit_written(task, audit_path, note.get("result", "skip"))
                steps.append(f"AUDIT {audit_path}")
        # refresh state summary after each step, keep state compact
        summarize()
    state = read_json(STATE / "project.json", {}) or {}
    state["last_dispatch"] = steps[-1] if steps else "NO_READY_TASK"
    write_json(STATE / "project.json", state)
    return "\n".join(steps) if steps else "NO_READY_TASK"


def heartbeat(mode: str = "prompt", cycles: int = 3, sleep_s: int = 0) -> str:
    ensure_runtime()
    out = []
    for i in range(cycles):
        out.append(f"[cycle {i+1}] " + drain_queue(mode=mode, max_steps=1, audit=True))
        if sleep_s:
            sleep(sleep_s)
    return "\n".join(out)
