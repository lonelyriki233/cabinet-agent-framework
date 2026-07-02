from __future__ import annotations

from typing import Any, cast

from .leader import classify_request
from .secretariat import make_packet, persist_tasks
from .governance import convene_strategy_council, relay_mandate, WORKER_TO_BUREAU
from .model import TASKS, STATE, read_json, write_json, ensure_runtime
from .project_harness import create_project, create_harness_task, add_decision, TaskStage


def _stage_for_task_type(task_type: str) -> str:
    if task_type in {"strategy", "research", "docs"}:
        return "design"
    if task_type in {"hooks", "mcp_rag", "headless", "sdk_adapter", "dashboard", "worker_skill", "thinking_skill", "context_unit", "memory", "autonomous", "skill_forge"}:
        return "implementation"
    return "implementation"


def _required_types(task: dict[str, Any]) -> list[str]:
    outputs = task.get("required_outputs") or []
    text = " ".join(outputs + [task.get("title", ""), task.get("objective", "")]).lower()
    types: list[str] = []
    if ".py" in text or "code" in text or "sdk" in text or "mcp" in text:
        types.append("code")
    if ".md" in text or "docs" in text or "文档" in text or "说明" in text or not types:
        types.append("docs")
    if "test" in text or "测试" in text:
        types.append("tests")
    return sorted(set(types))


def _acceptance(task: dict[str, Any]) -> list[str]:
    criteria = task.get("acceptance_criteria") or []
    if criteria:
        return criteria
    return ["产出真实 artifact", "artifact 已登记", "gate 审查通过"]


def request_to_harness(request: str, authority: str = "L2", source: str = "hermes_chat", persist_runtime_tasks: bool = True) -> dict[str, Any]:
    """Convert an ordinary request into CAF v1.0 Project Harness objects.

    This is the bridge from chat/intake into the v1.0 harness.
    It still preserves the legacy TaskPacket path for compatibility.
    """
    ensure_runtime()
    decision = classify_request(request)
    council = convene_strategy_council(request, decision.primary_worker, decision.needs_autoresearch, decision.task_type)
    mandate = relay_mandate(request, authority)
    result: dict[str, Any] = {
        "source": source,
        "request": request,
        "authority": authority,
        "decision": decision.to_dict(),
        "council": council.to_dict(),
        "mandate": mandate.to_dict(),
        "project": None,
        "legacy_tasks": [],
        "harness_tasks": [],
    }
    if not mandate.approved:
        state = read_json(STATE / "project.json", {}) or {}
        state.setdefault("blockers", []).append({"source": source, "request": request, "reason": mandate.reason})
        write_json(STATE / "project.json", state)
        return result

    legacy_packets = make_packet(decision)
    if persist_runtime_tasks:
        persist_tasks(legacy_packets)

    project = create_project(
        name=request[:60],
        objective=request,
        acceptance_criteria=["需求已拆解为 HarnessTask", "Worker 可执行", "Artifact/Gate 可追踪"],
    )
    add_decision(
        project["project_id"],
        "request accepted into CAF v1.0 harness",
        f"source={source}; authority={authority}; worker={decision.primary_worker}; task_type={decision.task_type}",
        ["legacy TaskPacket retained for compatibility", "HarnessTask is the v1.0 execution unit"],
    )

    for packet in legacy_packets:
        task_dict = packet.to_dict()
        if persist_runtime_tasks:
            p = TASKS / f"{packet.task_id}.json"
            data = read_json(p) or task_dict
            data["authority_level"] = authority
            data["source"] = source
            data["bureau"] = WORKER_TO_BUREAU.get(packet.worker, "unknown_bureau")
            data["harness_project_id"] = project["project_id"]
            write_json(p, data)
            task_dict = data
        harness_task = create_harness_task(
            project_id=project["project_id"],
            title=task_dict.get("title", request[:60]),
            objective=task_dict.get("objective", request),
            stage=cast(TaskStage, _stage_for_task_type(task_dict.get("task_type", decision.task_type))),
            worker=task_dict.get("worker", decision.primary_worker),
            acceptance_criteria=_acceptance(task_dict),
            required_artifact_types=_required_types(task_dict),
            allowed_paths=task_dict.get("allowed_paths") or ["."],
            source_task_id=task_dict.get("task_id"),
            source=source,
            authority_level=authority,
        )
        result["legacy_tasks"].append(task_dict)
        result["harness_tasks"].append(harness_task)

    result["project"] = project
    state = read_json(STATE / "project.json", {}) or {}
    state["last_harness_project"] = project["project_id"]
    state["last_harness_task_count"] = len(result["harness_tasks"])
    write_json(STATE / "project.json", state)
    return result
