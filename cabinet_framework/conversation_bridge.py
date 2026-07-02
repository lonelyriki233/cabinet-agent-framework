"""Conversation bridge: Hermes chat → framework runtime with auto-dispatch + v1.0 harness support."""

from __future__ import annotations

from .harness_intake import request_to_harness


def register_conversation_request(request: str, authority: str = "L2", source: str = "hermes_chat",
                                   auto_dispatch: bool = False) -> dict:
    """Register an actionable chat request into the framework runtime.

    v1.0 behavior:
    - ordinary chat request is converted into a HarnessProject + HarnessTask(s)
    - legacy TaskPacket creation is still preserved for compatibility/dashboard
    """
    harness_result = request_to_harness(request, authority=authority, source=source, persist_runtime_tasks=True)
    result = {
        "source": source,
        "request": request,
        "authority": authority,
        "decision": harness_result.get("decision", {}),
        "council": harness_result.get("council", {}),
        "mandate": harness_result.get("mandate", {}),
        "created_tasks": harness_result.get("legacy_tasks", []),
        "harness": {
            "project": harness_result.get("project"),
            "tasks": harness_result.get("harness_tasks", []),
        },
        "auto_dispatched": False,
    }

    if auto_dispatch and result["created_tasks"]:
        try:
            from .autonomous_worker import auto_intake
            auto_result = auto_intake(request, authority=authority, source=source)
            result["auto_dispatched"] = True
            result["auto_result"] = {
                "skills_created": auto_result.get("skills_created", []),
                "stages": len(auto_result.get("stages", [])),
            }
        except Exception as e:
            result["auto_error"] = str(e)[:200]

    return result
