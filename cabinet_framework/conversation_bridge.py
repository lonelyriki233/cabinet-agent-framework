from __future__ import annotations
from dataclasses import asdict

from .leader import classify_request
from .secretariat import make_packet, persist_tasks
from .governance import convene_strategy_council, relay_mandate, WORKER_TO_BUREAU
from .model import TASKS, read_json, write_json, ensure_runtime, STATE


def register_conversation_request(request: str, authority: str = "L2", source: str = "hermes_chat") -> dict:
    """Register an actionable chat request into the framework runtime.

    This is the bridge between normal Hermes conversation and the dashboard.
    If the agent receives an actionable user task while operating in this project,
    it should call this before doing the work so the task appears in the dashboard.
    """
    ensure_runtime()
    decision = classify_request(request)
    council = convene_strategy_council(
        request,
        decision.primary_worker,
        decision.needs_autoresearch,
        task_type=decision.task_type,
    )
    mandate = relay_mandate(request, authority)
    result = {
        "source": source,
        "request": request,
        "authority": authority,
        "decision": decision.to_dict(),
        "council": council.to_dict(),
        "mandate": mandate.to_dict(),
        "created_tasks": [],
    }
    if not mandate.approved:
        state = read_json(STATE / "project.json", {}) or {}
        state.setdefault("blockers", []).append({"source": source, "request": request, "reason": mandate.reason})
        write_json(STATE / "project.json", state)
        return result

    if decision.needs_secretariat:
        tasks = make_packet(decision)
        persist_tasks(tasks)
        for t in tasks:
            p = TASKS / f"{t.task_id}.json"
            data = read_json(p)
            data["authority_level"] = authority
            data["source"] = source
            data["conversation_registered"] = True
            data["bureau"] = WORKER_TO_BUREAU.get(t.worker, "unknown_bureau")
            write_json(p, data)
            result["created_tasks"].append(data)
    return result
