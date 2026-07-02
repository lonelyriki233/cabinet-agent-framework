from __future__ import annotations
import argparse
from pathlib import Path
from .model import ensure_runtime, TASKS, STATE, ROOT, read_json, write_json
from .leader import classify_request
from .secretariat import make_packet, persist_tasks, summarize
from .worker import run_task, tick, build_worker_prompt, worker_command
from .gates import run_gates
from .governance import convene_strategy_council, relay_mandate, WORKER_TO_BUREAU
from .dispatcher import drain_queue, heartbeat
from .dashboard import serve as dashboard_serve
from .archive import search as archive_search, tree_view as archive_tree
from .conversation_bridge import register_conversation_request
from .hooks import recent_events, lifecycle_for
from .autonomous_worker import auto_intake, iterate_from_feedback, get_autonomous_status
from .skill_forge import SkillForge, list_all_skills
from .capability import write_capability_audit, render_text
from .capability_contracts import install_default_contracts, export_parametric_example
from .project_harness import (
    create_project as harness_create_project,
    create_harness_task,
    register_artifact,
    run_stage_gate,
    harness_status,
    run_demo_loop,
)
from .worker_runtime import run_harness_worker, submit_worker_manifest, run_worker_and_gate
from .harness_intake import request_to_harness
from .context_engine import context_summary, project_context_index, register_task_memory
from .lifecycle_gate import advance_task_stage, lifecycle_status, list_blockers, resolve_blocker


def cmd_init(args): ensure_runtime(); print("caf init: PASS")

def cmd_intake(args):
    ensure_runtime(); decision = classify_request(args.request)
    council = convene_strategy_council(args.request, decision.primary_worker, decision.needs_autoresearch, decision.task_type)
    mandate = relay_mandate(args.request, args.authority)
    print("Leader Gateway 判断:")
    for k, v in decision.to_dict().items(): print(f"- {k}: {v}")
    print("Strategy Council 拟议:"); print(f"- active_councillors: {', '.join(council.active_councillors)}"); print(f"- principal_contradiction: {council.principal_contradiction}"); print(f"- draft_mandate: {council.draft_mandate}")
    print("Mandate Relay 审权:")
    for k, v in mandate.to_dict().items(): print(f"- {k}: {v}")
    if not mandate.approved: print("STOP: mandate not approved"); return
    if decision.needs_secretariat:
        tasks = make_packet(decision); persist_tasks(tasks)
        for t in tasks:
            p = TASKS / f"{t.task_id}.json"; data = read_json(p); data["authority_level"] = args.authority; data["bureau"] = WORKER_TO_BUREAU.get(t.worker, "unknown_bureau"); write_json(p, data)
        print(f"Chief Coordinator 拆解: created {len(tasks)} task(s)")
        for t in tasks: print(f"- {t.task_id} -> {WORKER_TO_BUREAU.get(t.worker, 'unknown_bureau')} -> {t.worker}")

def cmd_status(args): ensure_runtime(); print((STATE / "project.json").read_text(encoding="utf-8")); print(summarize())
def cmd_tasks(args): ensure_runtime(); [print(f"{t['task_id']} [{t.get('status')}] {t['worker']} :: {t['title']}") for t in [read_json(p) for p in sorted(TASKS.glob('*.json'))]]
def cmd_prompt(args): ensure_runtime(); print(build_worker_prompt(read_json(Path(args.task))))
def cmd_run(args): ensure_runtime(); print(run_task(Path(args.task), mode=args.mode))
def cmd_tick(args): ensure_runtime(); print(tick(mode=args.mode))
def cmd_gate(args):
    ensure_runtime(); ok, messages = run_gates(); [print(m) for m in messages]; print("caf gate: PASS" if ok else "caf gate: FAIL"); raise SystemExit(0 if ok else 1)
def cmd_command(args): ensure_runtime(); print(worker_command(Path(args.task)))
def cmd_dispatch(args): ensure_runtime(); print(drain_queue(mode=args.mode, max_steps=args.max_steps, audit=not args.no_audit))
def cmd_heartbeat(args): ensure_runtime(); print(heartbeat(mode=args.mode, cycles=args.cycles, sleep_s=args.sleep))
def cmd_dashboard(args): ensure_runtime(); print(f"dashboard running at http://{args.host}:{args.port}/"); dashboard_serve(host=args.host, port=args.port)
def cmd_archive_search(args):
    ensure_runtime(); results = archive_search(args.query, bureau=args.bureau or None, task_type=args.task_type or None, top_k=args.top_k)
    for r in results: print(f"{r['score']:.4f} {r['bureau']} {r['task_type']} {r['task_id']} :: {r['title']} -> {r['artifact_path']}")
def cmd_archive_tree(args):
    ensure_runtime(); import json; print(json.dumps(archive_tree(), ensure_ascii=False, indent=2))
def cmd_chat_intake(args):
    ensure_runtime(); import json; result = register_conversation_request(args.request, authority=args.authority, source=args.source)
    print(json.dumps({"created": len(result.get("created_tasks", [])), "task_ids": [t["task_id"] for t in result.get("created_tasks", [])], "mandate": result.get("mandate", {})}, ensure_ascii=False, indent=2))
def cmd_hooks(args):
    ensure_runtime(); import json; print(json.dumps(lifecycle_for(args.task_id) if args.task_id else recent_events(args.limit), ensure_ascii=False, indent=2))

def cmd_forge(args):
    ensure_runtime()
    forge = SkillForge()
    result = forge.forge_skill(
        worker_name=args.worker or "unknown",
        task_type=args.task_type or "general",
        task_title=args.title or args.request,
        request=args.request,
    )
    import json; print(json.dumps({
        "skill_name": result.get("skill_name"),
        "skill_path": result.get("skill_path"),
        "existing": result.get("existing", False),
    }, ensure_ascii=False, indent=2))

def cmd_forge_list(args):
    ensure_runtime()
    import json; print(json.dumps(list_all_skills(), ensure_ascii=False, indent=2))

def cmd_forge_iterate(args):
    ensure_runtime()
    import json; result = iterate_from_feedback(args.task_id, args.feedback, improve_skill=not args.no_improve)
    print(json.dumps(result, ensure_ascii=False, indent=2))

def cmd_auto(args):
    ensure_runtime()
    import json; result = auto_intake(args.request, authority=args.authority, source=args.source, force_forge=args.force_forge)
    print(json.dumps({
        "stages": [s.get("stage") for s in result.get("stages", [])],
        "task_ids": result.get("task_ids", []),
        "skills_created": result.get("skills_created", []),
        "error": result.get("error"),
    }, ensure_ascii=False, indent=2))

def cmd_auto_status(args):
    ensure_runtime()
    import json; print(json.dumps(get_autonomous_status(), ensure_ascii=False, indent=2))

def cmd_capability_audit(args):
    ensure_runtime()
    data = write_capability_audit()
    print(render_text(data))

def cmd_install_contracts(args):
    ensure_runtime()
    import json
    print(json.dumps({"installed": install_default_contracts()}, ensure_ascii=False, indent=2))

def cmd_param_example(args):
    ensure_runtime()
    import json
    result = export_parametric_example(
        task_id=args.task_id,
        instruction=args.instruction,
        good_output=args.good_output,
        bad_output=args.bad_output,
        feedback=args.feedback,
    )
    print(json.dumps(result, ensure_ascii=False, indent=2))

def cmd_harness_project(args):
    ensure_runtime()
    import json
    result = harness_create_project(args.name, args.objective, args.acceptance or [])
    print(json.dumps(result, ensure_ascii=False, indent=2))

def cmd_harness_task(args):
    ensure_runtime()
    import json
    result = create_harness_task(
        project_id=args.project_id,
        title=args.title,
        objective=args.objective,
        stage=args.stage,
        worker=args.worker,
        acceptance_criteria=args.acceptance or [],
        required_artifact_types=args.required_type or [],
    )
    print(json.dumps(result, ensure_ascii=False, indent=2))

def cmd_harness_artifact(args):
    ensure_runtime()
    import json
    result = register_artifact(
        project_id=args.project_id,
        owner_task=args.task_id,
        path=args.path,
        artifact_type=args.type,
        status=args.status,
        validation_result={"status": args.validation_status, "message": args.validation_message},
    )
    print(json.dumps(result, ensure_ascii=False, indent=2))

def cmd_harness_gate(args):
    ensure_runtime()
    import json
    result = run_stage_gate(args.task_id)
    print(json.dumps(result, ensure_ascii=False, indent=2))
    raise SystemExit(0 if result.get("status") == "pass" else 1)

def cmd_harness_status(args):
    ensure_runtime()
    import json
    print(json.dumps(harness_status(), ensure_ascii=False, indent=2))

def cmd_harness_demo(args):
    ensure_runtime()
    import json
    result = run_demo_loop()
    print(json.dumps(result, ensure_ascii=False, indent=2))
    raise SystemExit(0 if result["gate"].get("status") == "pass" else 1)

def cmd_harness_run(args):
    ensure_runtime()
    import json
    result = run_harness_worker(args.task_id, mode=args.mode)
    print(json.dumps(result, ensure_ascii=False, indent=2))

def cmd_harness_submit(args):
    ensure_runtime()
    import json
    result = submit_worker_manifest(args.manifest)
    print(json.dumps(result, ensure_ascii=False, indent=2))

def cmd_harness_run_gate(args):
    ensure_runtime()
    import json
    result = run_worker_and_gate(args.task_id, mode=args.mode)
    print(json.dumps(result, ensure_ascii=False, indent=2))
    raise SystemExit(0 if result["gate"].get("status") == "pass" else 1)

def cmd_harness_intake(args):
    ensure_runtime()
    import json
    result = request_to_harness(args.request, authority=args.authority, source=args.source, persist_runtime_tasks=not args.no_legacy)
    print(json.dumps({
        "project_id": (result.get("project") or {}).get("project_id"),
        "legacy_task_ids": [t.get("task_id") for t in result.get("legacy_tasks", [])],
        "harness_task_ids": [t.get("task_id") for t in result.get("harness_tasks", [])],
        "decision": result.get("decision", {}),
        "mandate": result.get("mandate", {}),
    }, ensure_ascii=False, indent=2))

def cmd_harness_context(args):
    ensure_runtime()
    import json
    if args.task_id:
        print(json.dumps(context_summary(args.task_id), ensure_ascii=False, indent=2))
    elif args.project_id:
        print(json.dumps(project_context_index(args.project_id), ensure_ascii=False, indent=2))
    else:
        raise SystemExit("provide --task-id or --project-id")

def cmd_harness_memory(args):
    ensure_runtime()
    import json
    result = register_task_memory(task_id=args.task_id, title=args.title, content=args.content, kind=args.kind, tags=args.tag or [], source=args.source)
    print(json.dumps(result, ensure_ascii=False, indent=2))

def cmd_harness_advance(args):
    ensure_runtime()
    import json
    result = advance_task_stage(args.task_id, target_stage=args.target_stage, create_rework=not args.no_rework)
    print(json.dumps(result, ensure_ascii=False, indent=2))
    raise SystemExit(0 if result.get("status") == "advanced" else 1)

def cmd_harness_lifecycle(args):
    ensure_runtime()
    import json
    print(json.dumps(lifecycle_status(args.task_id), ensure_ascii=False, indent=2))

def cmd_harness_blockers(args):
    ensure_runtime()
    import json
    print(json.dumps(list_blockers(project_id=args.project_id or None, task_id=args.task_id or None, status=args.status or None), ensure_ascii=False, indent=2))

def cmd_harness_resolve_blocker(args):
    ensure_runtime()
    import json
    result = resolve_blocker(args.blocker_id, resolved_by_task_id=args.resolved_by_task_id or None, resolution=args.resolution)
    print(json.dumps(result, ensure_ascii=False, indent=2))

def main():
    parser = argparse.ArgumentParser(prog="caf", description="Cabinet Agent Framework: portable multi-agent runtime for Hermes/Codex/Claude Code/OpenClaw")
    sub = parser.add_subparsers(dest="cmd", required=True)
    sub.add_parser("init")
    p = sub.add_parser("intake"); p.add_argument("--request", required=True); p.add_argument("--authority", choices=["L0","L1","L2","L3","L4"], default="L1")
    p = sub.add_parser("chat-intake"); p.add_argument("--request", required=True); p.add_argument("--authority", choices=["L0","L1","L2","L3","L4"], default="L2"); p.add_argument("--source", default="hermes_chat")
    sub.add_parser("status"); sub.add_parser("tasks")
    p = sub.add_parser("prompt"); p.add_argument("--task", required=True)
    p = sub.add_parser("run"); p.add_argument("--task", required=True); p.add_argument("--mode", choices=["prompt","hermes"], default="prompt")
    p = sub.add_parser("command"); p.add_argument("--task", required=True)
    p = sub.add_parser("tick"); p.add_argument("--mode", choices=["prompt","hermes"], default="prompt")
    p = sub.add_parser("dispatch"); p.add_argument("--mode", choices=["prompt","hermes"], default="prompt"); p.add_argument("--max-steps", type=int, default=50); p.add_argument("--no-audit", action="store_true")
    p = sub.add_parser("heartbeat"); p.add_argument("--mode", choices=["prompt","hermes"], default="prompt"); p.add_argument("--cycles", type=int, default=3); p.add_argument("--sleep", type=int, default=0)
    p = sub.add_parser("dashboard"); p.add_argument("--host", default="127.0.0.1"); p.add_argument("--port", type=int, default=8788)
    p = sub.add_parser("archive-search"); p.add_argument("--query", required=True); p.add_argument("--bureau", default=""); p.add_argument("--task-type", default=""); p.add_argument("--top-k", type=int, default=5)
    p = sub.add_parser("hooks"); p.add_argument("--task-id", default=""); p.add_argument("--limit", type=int, default=50)
    # forge
    p = sub.add_parser("forge"); p.add_argument("--request", required=True); p.add_argument("--worker", default=""); p.add_argument("--task-type", default=""); p.add_argument("--title", default="")
    p = sub.add_parser("forge-list")
    p = sub.add_parser("forge-iterate"); p.add_argument("--task-id", required=True); p.add_argument("--feedback", required=True); p.add_argument("--no-improve", action="store_true")
    # auto
    p = sub.add_parser("auto"); p.add_argument("--request", required=True); p.add_argument("--authority", choices=["L0","L1","L2","L3","L4"], default="L2"); p.add_argument("--source", default="hermes_cli"); p.add_argument("--force-forge", action="store_true")
    p = sub.add_parser("auto-status")
    sub.add_parser("capability-audit")
    sub.add_parser("install-contracts")
    p = sub.add_parser("param-example"); p.add_argument("--task-id", required=True); p.add_argument("--instruction", required=True); p.add_argument("--good-output", required=True); p.add_argument("--bad-output", default=""); p.add_argument("--feedback", default="")
    p = sub.add_parser("harness-project"); p.add_argument("--name", required=True); p.add_argument("--objective", required=True); p.add_argument("--acceptance", action="append")
    p = sub.add_parser("harness-task"); p.add_argument("--project-id", required=True); p.add_argument("--title", required=True); p.add_argument("--objective", required=True); p.add_argument("--stage", choices=["intake","design","implementation","test","review","delivery","archive"], required=True); p.add_argument("--worker", required=True); p.add_argument("--acceptance", action="append"); p.add_argument("--required-type", action="append")
    p = sub.add_parser("harness-artifact"); p.add_argument("--project-id", required=True); p.add_argument("--task-id", required=True); p.add_argument("--path", required=True); p.add_argument("--type", choices=["code","docs","tests","design","logs","config","decision","review","rollback","other"], required=True); p.add_argument("--status", choices=["draft","ready","validated","rejected","archived"], default="ready"); p.add_argument("--validation-status", default="unknown"); p.add_argument("--validation-message", default="")
    p = sub.add_parser("harness-gate"); p.add_argument("--task-id", required=True)
    sub.add_parser("harness-status")
    sub.add_parser("harness-demo")
    p = sub.add_parser("harness-run"); p.add_argument("--task-id", required=True); p.add_argument("--mode", choices=["prompt","local-report"], default="prompt")
    p = sub.add_parser("harness-submit"); p.add_argument("--manifest", required=True)
    p = sub.add_parser("harness-run-gate"); p.add_argument("--task-id", required=True); p.add_argument("--mode", choices=["prompt","local-report"], default="prompt")
    p = sub.add_parser("harness-intake"); p.add_argument("--request", required=True); p.add_argument("--authority", choices=["L0","L1","L2","L3","L4"], default="L2"); p.add_argument("--source", default="hermes_chat"); p.add_argument("--no-legacy", action="store_true")
    p = sub.add_parser("harness-context"); p.add_argument("--task-id"); p.add_argument("--project-id")
    p = sub.add_parser("harness-memory"); p.add_argument("--task-id", required=True); p.add_argument("--title", required=True); p.add_argument("--content", required=True); p.add_argument("--kind", choices=["document","case","log","skill","graph","tool_trace","human_feedback"], default="case"); p.add_argument("--tag", action="append"); p.add_argument("--source", default="harness_cli")
    p = sub.add_parser("harness-advance"); p.add_argument("--task-id", required=True); p.add_argument("--target-stage", choices=["intake","design","implementation","test","review","delivery","archive"]); p.add_argument("--no-rework", action="store_true")
    p = sub.add_parser("harness-lifecycle"); p.add_argument("--task-id", required=True)
    p = sub.add_parser("harness-blockers"); p.add_argument("--project-id", default=""); p.add_argument("--task-id", default=""); p.add_argument("--status", default="")
    p = sub.add_parser("harness-resolve-blocker"); p.add_argument("--blocker-id", required=True); p.add_argument("--resolved-by-task-id", default=""); p.add_argument("--resolution", default="manual resolution")
    sub.add_parser("archive-tree"); sub.add_parser("gate")
    args = parser.parse_args(); {"init":cmd_init,"intake":cmd_intake,"chat-intake":cmd_chat_intake,"status":cmd_status,"tasks":cmd_tasks,"prompt":cmd_prompt,"run":cmd_run,"command":cmd_command,"tick":cmd_tick,"dispatch":cmd_dispatch,"heartbeat":cmd_heartbeat,"dashboard":cmd_dashboard,"archive-search":cmd_archive_search,"hooks":cmd_hooks,"forge":cmd_forge,"forge-list":cmd_forge_list,"forge-iterate":cmd_forge_iterate,"auto":cmd_auto,"auto-status":cmd_auto_status,"capability-audit":cmd_capability_audit,"install-contracts":cmd_install_contracts,"param-example":cmd_param_example,"harness-project":cmd_harness_project,"harness-task":cmd_harness_task,"harness-artifact":cmd_harness_artifact,"harness-gate":cmd_harness_gate,"harness-status":cmd_harness_status,"harness-demo":cmd_harness_demo,"harness-run":cmd_harness_run,"harness-submit":cmd_harness_submit,"harness-run-gate":cmd_harness_run_gate,"harness-intake":cmd_harness_intake,"harness-context":cmd_harness_context,"harness-memory":cmd_harness_memory,"harness-advance":cmd_harness_advance,"harness-lifecycle":cmd_harness_lifecycle,"harness-blockers":cmd_harness_blockers,"harness-resolve-blocker":cmd_harness_resolve_blocker,"archive-tree":cmd_archive_tree,"gate":cmd_gate}[args.cmd](args)
if __name__ == "__main__": main()
