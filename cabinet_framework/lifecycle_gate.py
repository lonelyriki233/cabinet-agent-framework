from __future__ import annotations

from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any
import json

from .hooks import emit_hook
from .model import write_json, read_json
from .project_harness import (
    HARNESS_DIR,
    TaskStage,
    create_harness_task,
    get_task,
    now,
    run_stage_gate,
    slug,
)

BLOCKERS_FILE = HARNESS_DIR / "blockers.jsonl"
TRANSITIONS_FILE = HARNESS_DIR / "stage_transitions.jsonl"

STAGE_ORDER: list[TaskStage] = ["intake", "design", "implementation", "test", "review", "delivery", "archive"]
NEXT_STAGE: dict[str, TaskStage] = {STAGE_ORDER[i]: STAGE_ORDER[i + 1] for i in range(len(STAGE_ORDER) - 1)}
TERMINAL_STAGE: TaskStage = "archive"


@dataclass
class BlockerRecord:
    blocker_id: str
    project_id: str
    task_id: str
    stage: str
    reason: str
    gate_id: str | None = None
    messages: list[str] = field(default_factory=list)
    status: str = "open"
    rework_task_id: str | None = None
    created_at: str = field(default_factory=now)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def _task_path(task_id: str) -> Path:
    return HARNESS_DIR / "tasks" / f"{task_id}.json"


def _append_jsonl(path: Path, row: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as f:
        f.write(json.dumps(row, ensure_ascii=False) + "\n")


def _read_jsonl(path: Path) -> list[dict[str, Any]]:
    if not path.exists():
        return []
    rows: list[dict[str, Any]] = []
    for line in path.read_text(encoding="utf-8").splitlines():
        if line.strip():
            try:
                item = json.loads(line)
                if isinstance(item, dict):
                    rows.append(item)
            except json.JSONDecodeError:
                continue
    return rows


def save_task(task: dict[str, Any]) -> None:
    write_json(_task_path(task["task_id"]), task)


def blocker_events() -> list[dict[str, Any]]:
    return _read_jsonl(BLOCKERS_FILE)


def list_blockers(project_id: str | None = None, task_id: str | None = None, status: str | None = None) -> list[dict[str, Any]]:
    # BLOCKERS_FILE is append-only. The public view returns the latest event per blocker_id.
    latest: dict[str, dict[str, Any]] = {}
    for row in blocker_events():
        bid = row.get("blocker_id")
        if bid:
            latest[bid] = row
    rows = list(latest.values())
    if project_id:
        rows = [r for r in rows if r.get("project_id") == project_id]
    if task_id:
        rows = [r for r in rows if r.get("task_id") == task_id or r.get("rework_task_id") == task_id]
    if status:
        rows = [r for r in rows if r.get("status") == status]
    return rows


def record_blocker(task: dict[str, Any], gate: dict[str, Any], reason: str | None = None) -> dict[str, Any]:
    messages = gate.get("messages") or []
    blocker = BlockerRecord(
        blocker_id=f"B-{now()}-{slug(task.get('title', task['task_id']))}",
        project_id=task["project_id"],
        task_id=task["task_id"],
        stage=task.get("stage", "unknown"),
        reason=reason or "; ".join([m for m in messages if str(m).startswith("FAIL")]) or "gate failed",
        gate_id=gate.get("gate_id"),
        messages=list(messages),
    ).to_dict()
    _append_jsonl(BLOCKERS_FILE, blocker)
    _remember_gate_failure(task, blocker, gate)
    emit_hook("harness.lifecycle.blocked", "blocked", task, {"blocker": blocker, "gate": gate})
    return blocker


def _remember_gate_failure(task: dict[str, Any], blocker: dict[str, Any], gate: dict[str, Any]) -> None:
    try:
        from .context_engine import register_task_memory
        register_task_memory(
            task_id=task["task_id"],
            title=f"Gate failure: {task.get('title', task['task_id'])}",
            content="\n".join([
                f"blocker_id: {blocker.get('blocker_id')}",
                f"stage: {task.get('stage')}",
                f"reason: {blocker.get('reason')}",
                "messages:",
                *[str(m) for m in gate.get("messages", [])],
            ]),
            kind="case",
            tags=["caf", "harness", "gate_failure", str(task.get("stage")), task.get("project_id", "")],
            source="lifecycle_gate",
        )
    except Exception:
        # Memory persistence must not break lifecycle safety.
        pass


def _remember_blocker_resolution(task: dict[str, Any], blocker: dict[str, Any], gate: dict[str, Any] | None = None) -> None:
    try:
        from .context_engine import register_task_memory
        register_task_memory(
            task_id=task["task_id"],
            title=f"Resolved blocker: {blocker.get('blocker_id')}",
            content="\n".join([
                f"blocker_id: {blocker.get('blocker_id')}",
                f"original_task_id: {blocker.get('task_id')}",
                f"resolved_by_task: {task.get('task_id')}",
                f"resolution: {blocker.get('resolution', '')}",
                f"gate_id: {(gate or {}).get('gate_id', '')}",
            ]),
            kind="case",
            tags=["caf", "harness", "blocker_resolved", str(task.get("stage")), task.get("project_id", "")],
            source="lifecycle_gate",
        )
    except Exception:
        pass


def create_rework_task(task: dict[str, Any], blocker: dict[str, Any]) -> dict[str, Any]:
    required = task.get("required_artifact_types") or []
    rework = create_harness_task(
        project_id=task["project_id"],
        title=f"返工：{task.get('title', task['task_id'])}",
        objective="修复 gate 失败项并重新提交可验收 artifact。\n\n失败原因：" + blocker.get("reason", "gate failed"),
        stage=task.get("stage", "implementation"),
        worker=task.get("worker", "rework_worker"),
        acceptance_criteria=(task.get("acceptance_criteria") or []) + ["原 blocker 已被解决", "重新运行 lifecycle gate 通过"],
        required_artifact_types=required,
        dependencies=[task["task_id"]],
        allowed_paths=task.get("allowed_paths") or ["."],
        source_task_id=task["task_id"],
        source="lifecycle_gate_rework",
        authority_level=task.get("authority_level"),
    )
    blocker["rework_task_id"] = rework["task_id"]
    blocker["status"] = "rework_created"
    blocker["updated_at"] = now()
    _append_jsonl(BLOCKERS_FILE, blocker)
    emit_hook("harness.lifecycle.rework_created", "pass", task, {"blocker_id": blocker["blocker_id"], "rework_task_id": rework["task_id"]})
    return rework


def resolve_blocker(blocker_id: str, *, resolved_by_task_id: str | None = None, resolution: str = "resolved", gate: dict[str, Any] | None = None) -> dict[str, Any]:
    blockers = list_blockers()
    matches = [b for b in blockers if b.get("blocker_id") == blocker_id]
    if not matches:
        raise FileNotFoundError(blocker_id)
    blocker = dict(matches[-1])
    blocker["status"] = "resolved"
    blocker["resolution"] = resolution
    blocker["resolved_by_task_id"] = resolved_by_task_id
    blocker["resolved_at"] = now()
    blocker["resolution_gate_id"] = (gate or {}).get("gate_id")
    _append_jsonl(BLOCKERS_FILE, blocker)

    # Re-open the original task for another lifecycle attempt unless it has already moved on.
    try:
        original = get_task(blocker["task_id"])
        if original.get("status") == "blocked":
            original["status"] = "ready"
            original["updated_at"] = now()
            original.setdefault("resolved_blockers", []).append(blocker_id)
            save_task(original)
    except Exception:
        pass

    resolver_task = get_task(resolved_by_task_id) if resolved_by_task_id else get_task(blocker["task_id"])
    _remember_blocker_resolution(resolver_task, blocker, gate)
    emit_hook("harness.lifecycle.blocker_resolved", "pass", resolver_task, {"blocker": blocker})
    return blocker


def auto_resolve_rework_blockers(task: dict[str, Any], gate: dict[str, Any]) -> list[dict[str, Any]]:
    if task.get("source") != "lifecycle_gate_rework":
        return []
    resolved: list[dict[str, Any]] = []
    for blocker in list_blockers(project_id=task.get("project_id"), status="rework_created"):
        if blocker.get("rework_task_id") == task.get("task_id"):
            resolved.append(resolve_blocker(
                blocker["blocker_id"],
                resolved_by_task_id=task["task_id"],
                resolution="rework task passed lifecycle gate",
                gate=gate,
            ))
    return resolved


def advance_task_stage(task_id: str, *, target_stage: TaskStage | None = None, create_rework: bool = True) -> dict[str, Any]:
    """Advance a HarnessTask only if its current-stage gate passes.

    Gate fail does not silently advance. It records a blocker and optionally creates a rework task.
    """
    task = get_task(task_id)
    current = task.get("stage")
    if current not in STAGE_ORDER:
        raise ValueError(f"invalid task stage: {current}")
    desired = target_stage or NEXT_STAGE.get(current, TERMINAL_STAGE)
    if desired not in STAGE_ORDER:
        raise ValueError(f"invalid target stage: {desired}")

    emit_hook("harness.lifecycle.before_transition", "pass", task, {"from_stage": current, "to_stage": desired})
    gate = run_stage_gate(task_id)
    if gate.get("status") != "pass":
        blocker = record_blocker(task, gate)
        rework = create_rework_task(task, blocker) if create_rework else None
        task["status"] = "blocked"
        task.setdefault("blockers", []).append(blocker["blocker_id"])
        save_task(task)
        transition = {
            "transition_id": f"TR-{now()}-{task_id}",
            "task_id": task_id,
            "project_id": task["project_id"],
            "from_stage": current,
            "to_stage": desired,
            "status": "blocked",
            "gate_id": gate.get("gate_id"),
            "blocker_id": blocker["blocker_id"],
            "rework_task_id": rework.get("task_id") if rework else None,
            "created_at": now(),
        }
        _append_jsonl(TRANSITIONS_FILE, transition)
        emit_hook("harness.lifecycle.transition_blocked", "blocked", task, transition)
        return {"status": "blocked", "task": task, "gate": gate, "blocker": blocker, "rework_task": rework, "transition": transition}

    task["stage"] = desired
    task["status"] = "completed" if desired == TERMINAL_STAGE else "ready"
    task["updated_at"] = now()
    save_task(task)
    resolved_blockers = auto_resolve_rework_blockers(task, gate)
    transition = {
        "transition_id": f"TR-{now()}-{task_id}",
        "task_id": task_id,
        "project_id": task["project_id"],
        "from_stage": current,
        "to_stage": desired,
        "status": "advanced",
        "gate_id": gate.get("gate_id"),
        "created_at": now(),
    }
    _append_jsonl(TRANSITIONS_FILE, transition)
    emit_hook("harness.lifecycle.transition_advanced", "pass", task, transition)
    return {"status": "advanced", "task": task, "gate": gate, "transition": transition, "resolved_blockers": resolved_blockers}


def lifecycle_status(task_id: str) -> dict[str, Any]:
    task = get_task(task_id)
    transitions = [r for r in _read_jsonl(TRANSITIONS_FILE) if r.get("task_id") == task_id]
    blockers = list_blockers(task_id=task_id)
    events = [r for r in blocker_events() if r.get("task_id") == task_id or r.get("rework_task_id") == task_id]
    return {"task": task, "transitions": transitions, "blockers": blockers, "blocker_events": events}
