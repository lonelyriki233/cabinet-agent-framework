"""Conversation bridge: Hermes chat → framework runtime with auto-dispatch support."""

from __future__ import annotations
from dataclasses import asdict

from .leader import classify_request
from .secretariat import make_packet, persist_tasks
from .governance import convene_strategy_council, relay_mandate, WORKER_TO_BUREAU
from .model import TASKS, read_json, write_json, ensure_runtime, STATE


def register_conversation_request(request: str, authority: str = "L2", source: str = "hermes_chat",
                                   auto_dispatch: bool = False) -> dict:
    """Register an actionable chat request into the framework runtime.

    This is the bridge between normal Hermes conversation and the dashboard.
    If auto_dispatch is True, it will also trigger the autonomous worker pipeline.
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
        "auto_dispatched": False,
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

    # Auto-dispatch via autonomous worker if requested
    if auto_dispatch and result["created_tasks"]:
        try:
            from .autonomous_worker import auto_intake
            # Re-use the same intake with auto mode
            auto_result = auto_intake(request, authority=authority, source=source)
            result["auto_dispatched"] = True
            result["auto_result"] = {
                "skills_created": auto_result.get("skills_created", []),
                "stages": len(auto_result.get("stages", [])),
            }
        except Exception as e:
            result["auto_error"] = str(e)[:200]

    return result
