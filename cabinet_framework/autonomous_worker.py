"""Autonomous worker: auto-dispatch tasks, detect missing skills, forge new ones, iterate.

This is the A + C core module:
  (A) Hermes conversation → chat-intake → skill-check → dispatch → execute → audit → feedback
  (C) Missing skill → SkillForge discovery → research → create → register → calibrate → evolve
"""

from __future__ import annotations
from pathlib import Path
from datetime import datetime
import json, re, sys, urllib.request, urllib.error

from .model import (
    ROOT, RUNTIME, TASKS, OUTPUTS, REPORTS, LOGS, STATE, MEMORY, SKILLS,
    now, slug, read_json, write_json, write_text, ensure_runtime,
    TASK_TO_WORKER, WORKERS,
)
from .secretariat import make_packet, persist_tasks, summarize
from .governance import WORKER_TO_BUREAU
from .gates import run_gates
from .skill_forge import (
    SkillForge,
    skill_discovery_needed,
    estimate_skill_gap,
    find_adjacent_skills,
)

AUTO_STATE = STATE / "autonomous"


def ensure_auto_state():
    AUTO_STATE.mkdir(parents=True, exist_ok=True)
    f = AUTO_STATE / "config.json"
    if not f.exists():
        write_json(f, {
            "auto_dispatch": True,
            "auto_forge": True,
            "max_retries": 3,
            "feedback_required": True,
            "iteration_count": 0,
            "skills_forged": 0,
            "tasks_auto_completed": 0,
        })


def get_config() -> dict:
    ensure_auto_state()
    return read_json(AUTO_STATE / "config.json", {}) or {}


def set_config(**kwargs) -> dict:
    cfg = get_config()
    cfg.update(kwargs)
    write_json(AUTO_STATE / "config.json", cfg)
    return cfg


def get_autonomous_status() -> dict:
    ensure_runtime()
    ensure_auto_state()
    cfg = get_config()
    tasks = [read_json(p) for p in sorted(TASKS.glob("*.json"))]
    skills_dir = SKILLS / "worker"
    installed = [s.stem for s in skills_dir.glob("*.md")] if skills_dir.exists() else []
    return {
        "config": cfg,
        "total_tasks": len(tasks),
        "done_tasks": len([t for t in tasks if t.get("status") == "done"]),
        "pending_tasks": len([t for t in tasks if t.get("status") == "ready"]),
        "blocked_tasks": len([t for t in tasks if t.get("status") in ("blocked", "failed")]),
        "installed_worker_skills": installed,
        "skills_forged": cfg.get("skills_forged", 0),
        "auto_dispatch": cfg.get("auto_dispatch", True),
        "auto_forge": cfg.get("auto_forge", True),
    }


def auto_intake(request: str, authority: str = "L2", source: str = "hermes_chat",
                force_forge: bool = False) -> dict:
    """Full A pipeline: intake → skill check → forge if missing → dispatch → audit.
    
    Returns a dict with all stages' results.
    """
    ensure_runtime()
    ensure_auto_state()
    result = {
        "request": request,
        "authority": authority,
        "source": source,
        "stages": [],
        "error": None,
        "task_ids": [],
        "skills_created": [],
    }

    # Stage 1: Conversation bridge intake
    from .conversation_bridge import register_conversation_request
    bridge = register_conversation_request(request, authority=authority, source=source)
    result["stages"].append({"stage": "intake", "tasks_created": len(bridge.get("created_tasks", []))})
    if not bridge.get("mandate", {}).get("approved", False):
        result["error"] = "mandate_not_approved"
        return result

    created_tasks = bridge.get("created_tasks", [])
    result["task_ids"] = [t["task_id"] for t in created_tasks]

    # Stage 2: Skill check per task
    for task in created_tasks:
        task_id = task["task_id"]
        worker_name = task.get("worker", "unknown")
        task_type = task.get("task_type", "general")
        task_title = task.get("title", "")

        skill_needed = skill_discovery_needed(worker_name, task_type, task_title, request)
        if not skill_needed:
            result["stages"].append({"stage": "skill_ok", "task_id": task_id})
            continue

        # Stage 3: SkillForge - create missing skill
        if not get_config().get("auto_forge", True) and not force_forge:
            result["stages"].append({"stage": "forge_skipped", "task_id": task_id})
            continue

        forge = SkillForge()
        creation = forge.forge_skill(
            worker_name=worker_name,
            task_type=task_type,
            task_title=task_title,
            request=request,
            sources=find_adjacent_skills(task_type),
        )
        if creation.get("skill_path"):
            result["stages"].append({
                "stage": "skill_created",
                "task_id": task_id,
                "skill": creation.get("skill_name"),
                "path": creation.get("skill_path"),
            })
            result["skills_created"].append(creation.get("skill_name"))
            cfg = get_config()
            cfg["skills_forged"] = cfg.get("skills_forged", 0) + 1
            write_json(AUTO_STATE / "config.json", cfg)

            # Patch the task to reference its new skill
            task_data = read_json(TASKS / f"{task_id}.json")
            if task_data:
                task_data["forge_skill"] = creation.get("skill_name")
                write_json(TASKS / f"{task_id}.json", task_data)

    # Stage 4: Auto-dispatch (if enabled)
    if get_config().get("auto_dispatch", True):
        from .dispatcher import drain_queue
        dispatch_result = drain_queue(mode="prompt", max_steps=50, audit=True)
        result["stages"].append({"stage": "dispatch", "result": str(dispatch_result)[:200]})
        cfg = get_config()
        cfg["tasks_auto_completed"] = cfg.get("tasks_auto_completed", 0) + 1
        write_json(AUTO_STATE / "config.json", cfg)

    # Stage 5: Summary
    result["summary"] = summarize()
    return result


def iterate_from_feedback(task_id: str, feedback: str, improve_skill: bool = True) -> dict:
    """User feedback loop: learn from corrections and improve the skill."""
    ensure_auto_state()
    task = read_json(TASKS / f"{task_id}.json")
    if not task:
        return {"error": "task_not_found"}

    forged_skill_name = task.get("forge_skill")
    if not forged_skill_name or not improve_skill:
        return {"note": "no_skill_to_improve", "task_id": task_id}

    forge = SkillForge()
    improvement = forge.improve_skill_from_feedback(forged_skill_name, feedback, task)
    
    cfg = get_config()
    cfg["iteration_count"] = cfg.get("iteration_count", 0) + 1
    write_json(AUTO_STATE / "config.json", cfg)
    
    return {
        "task_id": task_id,
        "skill": forged_skill_name,
        "improvement": improvement,
    }
