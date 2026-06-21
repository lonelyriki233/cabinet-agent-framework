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
    sub.add_parser("archive-tree"); sub.add_parser("gate")
    args = parser.parse_args(); {"init":cmd_init,"intake":cmd_intake,"chat-intake":cmd_chat_intake,"status":cmd_status,"tasks":cmd_tasks,"prompt":cmd_prompt,"run":cmd_run,"command":cmd_command,"tick":cmd_tick,"dispatch":cmd_dispatch,"heartbeat":cmd_heartbeat,"dashboard":cmd_dashboard,"archive-search":cmd_archive_search,"hooks":cmd_hooks,"forge":cmd_forge,"forge-list":cmd_forge_list,"forge-iterate":cmd_forge_iterate,"auto":cmd_auto,"auto-status":cmd_auto_status,"archive-tree":cmd_archive_tree,"gate":cmd_gate}[args.cmd](args)
if __name__ == "__main__": main()
