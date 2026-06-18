
from __future__ import annotations
from wsgiref.simple_server import make_server
from urllib.parse import parse_qs
from pathlib import Path
import json
from jinja2 import Environment, FileSystemLoader, select_autoescape

from .model import ROOT, TASKS, STATE, read_json, ensure_runtime, WORKERS
from .secretariat import summarize
from .archive import tree_view, search, ensure_archive
from .governance import WORKER_TO_BUREAU, DOMAIN_BUREAUS, COUNCILLORS
from .hooks import recent_events, lifecycle_for

TEMPLATE_DIR = ROOT / "web" / "templates"
env = Environment(loader=FileSystemLoader(str(TEMPLATE_DIR)), autoescape=select_autoescape(["html", "xml"]))

NAV = [
    {"key": "overview", "label": "中枢总览", "href": "/overview", "title": "中枢总览", "hint": "框架模块 + agent 工作态势"},
    {"key": "memory", "label": "记忆系统", "href": "/memory", "title": "记忆系统", "hint": "内阁高层记忆与六部分层记忆"},
    {"key": "skills-core", "label": "思考 Skills", "href": "/skills-core", "title": "思考 Skills", "hint": "面向高级 AI 的核心思考层"},
    {"key": "skills-worker", "label": "Worker Skills", "href": "/skills-worker", "title": "Worker Skills", "hint": "面向小模型/开源模型的可执行工作层"},
    {"key": "context-units", "label": "上下文单元", "href": "/context-units", "title": "上下文单元", "hint": "内阁-六部多智能体协调包"},
    {"key": "hooks-runtime", "label": "Hooks", "href": "/hooks-runtime", "title": "Hooks", "hint": "生命周期、门禁、闭环、失败停止"},
    {"key": "mcp-rag", "label": "MCP / RAG", "href": "/mcp-rag", "title": "MCP / RAG", "hint": "工具接口、向量库、维护检索"},
    {"key": "headless", "label": "Headless", "href": "/headless", "title": "Headless", "hint": "昼夜运行、心跳、守护与人工接管"},
    {"key": "sdk-adapters", "label": "SDK / Adapters", "href": "/sdk-adapters", "title": "SDK / Adapters", "hint": "Hermes/Codex/Claude Code/OpenClaw 兼容层"},
    {"key": "templates", "label": "子工程模板", "href": "/templates", "title": "子工程模板", "hint": "数据平台、小说/OC/IP、研究、工程等模板"},
    {"key": "agents", "label": "Agent 工作台", "href": "/agents", "title": "Agent 工作台", "hint": "worker、bureau、任务归属、参议位"},
    {"key": "tasks", "label": "任务流", "href": "/tasks", "title": "任务流", "hint": "任务队列、prompt、日志、审计和产物路径"},
    {"key": "hooks", "label": "生命周期", "href": "/hooks", "title": "生命周期", "hint": "任务创建、执行前后、归档、审计、停止门事件"},
    {"key": "archive", "label": "档案检索", "href": "/archive", "title": "档案检索", "hint": "project.json、archive tree 和内容搜索"},
    {"key": "layers", "label": "框架链路", "href": "/layers", "title": "框架链路", "hint": "从对话到归档的治理链路"},
    {"key": "docs", "label": "文档", "href": "/docs", "title": "文档", "hint": "维护文档索引"},
]
SECTIONS = {item["key"]: item for item in NAV}

CONTENT_SECTIONS = {
    "memory": {"title": "记忆系统", "root": "memory", "globs": ["*.md", "*.json", "**/*.md", "**/*.json"], "accent": "#8b5cf6"},
    "skills-core": {"title": "思考 Skills", "root": "skills/thinking", "globs": ["*.md", "**/*.md"], "accent": "#38bdf8"},
    "skills-worker": {"title": "Worker Skills", "root": "skills/worker", "globs": ["*.md", "**/*.md"], "accent": "#f59e0b"},
    "context-units": {"title": "上下文单元", "root": "context_units", "globs": ["*.md", "*.json", "*.yaml", "*.yml", "**/*.md", "**/*.json", "**/*.yaml", "**/*.yml"], "accent": "#fb7185"},
    "hooks-runtime": {"title": "Hooks", "root": "hooks", "globs": ["*.md", "*.json", "*.yaml", "*.yml", "**/*.md", "**/*.json", "**/*.yaml", "**/*.yml"], "accent": "#a78bfa"},
    "mcp-rag": {"title": "MCP / RAG", "root": "mcp", "globs": ["*.md", "*.json", "*.yaml", "*.yml", "**/*.md", "**/*.json", "**/*.yaml", "**/*.yml"], "accent": "#22c55e"},
    "headless": {"title": "Headless", "root": "headless", "globs": ["*.md", "*.json", "*.yaml", "*.yml", "**/*.md", "**/*.json", "**/*.yaml", "**/*.yml"], "accent": "#06b6d4"},
    "sdk-adapters": {"title": "SDK / Adapters", "root": "adapters", "globs": ["*.md", "*.json", "*.yaml", "*.yml", "**/*.md", "**/*.json", "**/*.yaml", "**/*.yml"], "accent": "#7170ff"},
    "templates": {"title": "子工程模板", "root": "templates", "globs": ["*.md", "*.json", "*.yaml", "*.yml", "**/*.md", "**/*.json", "**/*.yaml", "**/*.yml"], "accent": "#e879f9"},
}

LAYER_FLOW = [
    {"name": "Final Authority", "cn": "用户授权源", "does": "给出目标、边界、授权等级和最终确认。", "source": "Hermes 对话 / chat-intake", "artifact": "原始请求、authority level"},
    {"name": "Leader Gateway", "cn": "需求判断层", "does": "判断任务类型、风险、是否需要 auto-research、主 worker。", "source": "cabinet_framework/leader.py", "artifact": "LeaderDecision"},
    {"name": "Strategy Council", "cn": "策略参议组", "does": "按需激活 research / architecture / engineering / risk / evidence 参议位，给出主矛盾和执行建议。", "source": "cabinet_framework/governance.py", "artifact": "CouncilDraft"},
    {"name": "Chief Coordinator", "cn": "首席协调官", "does": "把需求拆成结构化任务包，分派给领域 worker。", "source": "cabinet_framework/secretariat.py", "artifact": "runtime/tasks/*.json"},
    {"name": "Mandate Relay", "cn": "授权中继层", "does": "只做权限判断，不重新讨论方案；高风险任务升级给用户。", "source": "cabinet_framework/governance.py", "artifact": "MandateDecision"},
    {"name": "Domain Bureaus", "cn": "领域执行司", "does": "各 worker 按任务包执行，写 required_outputs、日志和自我质疑。", "source": "cabinet_framework/worker.py + hermes_bridge.py", "artifact": "runtime/outputs、runtime/logs"},
    {"name": "Audit Office", "cn": "独立监察司", "does": "运行 gate / audit，检查结构、边界、输出和任务包 schema。", "source": "cabinet_framework/gates.py + dispatcher.py", "artifact": "runtime/audits/*.json"},
    {"name": "State Archive", "cn": "状态档案", "does": "把完成任务按 bureau/task_type/task_id 分层归档并建立 embedding 检索。", "source": "cabinet_framework/archive.py", "artifact": "runtime/archive/**"},
]


def _rel(path: Path) -> str:
    try:
        return str(path.relative_to(ROOT))
    except Exception:
        return str(path)


def _existing(paths: list[str]) -> list[str]:
    return [p for p in paths if (ROOT / p).exists()]


def _task_report_paths(task: dict) -> dict:
    task_id = task.get("task_id", "")
    candidates = {
        "required_outputs": task.get("required_outputs", []),
        "worker_prompt": [task.get("worker_prompt")] if task.get("worker_prompt") else [f"runtime/logs/{task_id}.worker_prompt.txt"],
        "hermes_log": [task.get("hermes_log")] if task.get("hermes_log") else [f"runtime/logs/{task_id}.hermes.log"],
        "audit": [f"runtime/audits/{task_id}.audit.json"],
        "archive_meta": list(str(p.relative_to(ROOT)) for p in (ROOT / "runtime" / "archive").rglob("meta.json") if task_id in str(p)),
    }
    return {k: _existing([x for x in v if x]) for k, v in candidates.items()}


def _agents(tasks: list[dict]) -> list[dict]:
    rows = []
    for worker, bureau in WORKER_TO_BUREAU.items():
        owned = [t for t in tasks if t.get("worker") == worker]
        rows.append({
            "worker": worker,
            "bureau": bureau,
            "bureau_desc": DOMAIN_BUREAUS.get(bureau, ""),
            "role": WORKERS.get(worker, ""),
            "tasks_total": len(owned),
            "tasks_ready": sum(1 for t in owned if t.get("status") == "ready"),
            "tasks_done": sum(1 for t in owned if t.get("status") == "done"),
            "current": owned[-1] if owned else None,
        })
    return rows


def _docs_index() -> list[dict]:
    docs = []
    for p in sorted((ROOT / "docs").rglob("*.md")) if (ROOT / "docs").exists() else []:
        docs.append({"path": _rel(p), "title": p.stem.replace("_", " "), "group": p.parent.name})
    for name in ["README.md", "AGENTS.md", "SOUL.md", "START_PROMPT.md", "README.zh-CN.md"]:
        p = ROOT / name
        if p.exists():
            docs.insert(0, {"path": name, "title": p.stem, "group": "root"})
    return docs



def _safe_excerpt(path: Path, max_chars: int = 900) -> str:
    try:
        text = path.read_text(encoding="utf-8", errors="ignore")
    except Exception:
        return ""
    text = text.strip()
    return text[:max_chars] + ("…" if len(text) > max_chars else "")


def _content_files_for(section: str) -> list[dict]:
    cfg = CONTENT_SECTIONS.get(section, {})
    roots: list[Path] = []
    if cfg.get("root"):
        roots = [ROOT / str(cfg["root"])]
    rows: list[dict] = []
    seen: set[Path] = set()
    globs = cfg.get("globs") or ["**/*.md", "**/*.json", "**/*.yaml", "**/*.yml"]
    for root in roots:
        if not root.exists():
            continue
        for pattern in globs:
            for p in root.glob(pattern):
                if not p.is_file() or p in seen:
                    continue
                seen.add(p)
                rows.append({
                    "path": _rel(p),
                    "name": p.stem.replace("_", " "),
                    "kind": p.suffix.lstrip(".") or "text",
                    "excerpt": _safe_excerpt(p),
                    "updated": int(p.stat().st_mtime),
                })
    rows.sort(key=lambda x: x["updated"], reverse=True)
    return rows


def _task_matches_section(task: dict, section: str) -> bool:
    worker = task.get("worker", "")
    task_type = task.get("task_type", "")
    mapping = {
        "memory": {"memory_steward_worker", "memory"},
        "skills-core": {"thinking_skill_curator_worker", "thinking_skill"},
        "skills-worker": {"worker_skill_builder_worker", "worker_skill"},
        "context-units": {"context_unit_worker", "context_unit"},
        "hooks-runtime": {"hook_lifecycle_worker", "hooks"},
        "mcp-rag": {"mcp_rag_worker", "mcp_rag"},
        "headless": {"headless_ops_worker", "headless"},
        "sdk-adapters": {"sdk_adapter_worker", "sdk_adapter"},
        "templates": {"domain_template_worker", "domain_template"},
    }
    keys = mapping.get(section, set())
    return worker in keys or task_type in keys


def _module_content(tasks: list[dict]) -> dict:
    content = {}
    for key, cfg in CONTENT_SECTIONS.items():
        files = _content_files_for(key)
        related = [t for t in tasks if _task_matches_section(t, key)]
        content[key] = {
            "key": key,
            "title": cfg["title"],
            "accent": cfg["accent"],
            "root": cfg.get("root"),
            "files": files,
            "file_count": len(files),
            "tasks": related,
            "task_count": len(related),
            "ready": sum(1 for t in related if t.get("status") == "ready"),
            "prompted": sum(1 for t in related if t.get("status") == "prompted"),
            "done": sum(1 for t in related if t.get("status") == "done"),
        }
    return content


def _task_flow(task: dict) -> list[dict]:
    """Per-task upstream-to-downstream route shown on the task report page."""
    worker = task.get("worker", "unknown_worker")
    bureau = WORKER_TO_BUREAU.get(worker, str(task.get("bureau") or "unknown_bureau"))
    return [
        {"stage": "上游输入", "unit": "Final Authority / Hermes Chat", "agent": "user + current Hermes agent", "status": "received", "evidence": task.get("parent_request") or task.get("objective", "")},
        {"stage": "需求判断", "unit": "Leader Gateway", "agent": "leader.py", "status": "classified", "evidence": task.get("task_type", "")},
        {"stage": "策略参议", "unit": "Strategy Council", "agent": "governance.py", "status": "consulted", "evidence": "按任务类型激活必要 councillors；详见 created task package"},
        {"stage": "任务拆解", "unit": "Chief Coordinator", "agent": "secretariat.py", "status": "packetized", "evidence": task.get("task_id", "")},
        {"stage": "授权中继", "unit": "Mandate Relay", "agent": "governance.py", "status": task.get("authority_level", "L2"), "evidence": task.get("source", "")},
        {"stage": "领域执行", "unit": bureau, "agent": worker, "status": task.get("status", "unknown"), "evidence": WORKERS.get(worker, "")},
        {"stage": "生命周期", "unit": "Runtime Hooks", "agent": "hooks.py", "status": f"{len(lifecycle_for(task.get('task_id', '')))} events", "evidence": "runtime/hooks/lifecycle/<task_id>.json"},
        {"stage": "监察审计", "unit": "Audit Office", "agent": "dispatcher.py + gates.py", "status": "audit pending" if not _task_report_paths(task).get("audit") else "audit written", "evidence": ", ".join(_task_report_paths(task).get("audit", []))},
        {"stage": "状态归档", "unit": "State Archive", "agent": "archive.py", "status": "archived" if _task_report_paths(task).get("archive_meta") else "not archived", "evidence": ", ".join(_task_report_paths(task).get("archive_meta", []))},
    ]


def _task_report(task: dict | None) -> dict | None:
    if not task:
        return None
    t = dict(task)
    t["bureau"] = WORKER_TO_BUREAU.get(t.get("worker", ""), t.get("bureau", "unknown_bureau"))
    t["bureau_desc"] = DOMAIN_BUREAUS.get(t["bureau"], "")
    t["worker_role"] = WORKERS.get(t.get("worker", ""), "")
    t["reports"] = _task_report_paths(t)
    lifecycle = lifecycle_for(t.get("task_id", ""))
    t["lifecycle"] = lifecycle
    t["lifecycle_count"] = len(lifecycle)
    t["current_hook"] = lifecycle[-1] if lifecycle else None
    t["flow"] = _task_flow(t)
    t["upstream"] = {
        "source": t.get("source", ""),
        "parent_request": t.get("parent_request", ""),
        "conversation_registered": t.get("conversation_registered", False),
        "authority_level": t.get("authority_level", ""),
    }
    t["downstream"] = {
        "required_outputs": t.get("required_outputs", []),
        "acceptance_criteria": t.get("acceptance_criteria", []),
        "gates": t.get("gates", []),
        "allowed_paths": t.get("allowed_paths", []),
        "forbidden_paths": t.get("forbidden_paths", []),
    }
    return t


def _find_task(task_id: str) -> dict | None:
    p = TASKS / f"{task_id}.json"
    if p.exists():
        return read_json(p)
    return None


def _state_data():
    ensure_runtime(); ensure_archive()
    state = read_json(STATE / "project.json", {}) or {}
    tasks = [read_json(p) for p in sorted(TASKS.glob("*.json"))]
    for t in tasks:
        t["bureau"] = WORKER_TO_BUREAU.get(t.get("worker", ""), "unknown_bureau")
        t["reports"] = _task_report_paths(t)
    summary = summarize()
    task_distribution = {}
    for t in tasks:
        task_distribution[t.get("worker", "unknown")] = task_distribution.get(t.get("worker", "unknown"), 0) + 1
    subject_requests = sorted({t.get("parent_request", "") for t in tasks if t.get("parent_request")})
    return {
        "framework_identity": {
            "name": "Cabinet Agent Framework",
            "role": "管理、拆解、执行、审计和归档跨宿主 agent 工作流；不是某一个子工程本身。",
            "boundary": "dashboard 中的任务统计代表框架建设和子工程工作负载，不代表所有能力已经实现。",
        },
        "subject_work": {
            "requests": subject_requests[-5:],
            "task_distribution": task_distribution,
            "note": "这里显示的是用户交给框架管理的 agent 框架任务，例如记忆、skills、上下文、hooks、MCP/RAG、headless、SDK、dashboard 和子工程模板。",
        },
        "state": state,
        "tasks": tasks,
        "summary": summary,
        "module_content": _module_content(tasks),
        "archive_tree": tree_view(),
        "workers": WORKER_TO_BUREAU,
        "agents": _agents(tasks),
        "layers": LAYER_FLOW,
        "councillors": COUNCILLORS,
        "bureaus": DOMAIN_BUREAUS,
        "docs": _docs_index(),
        "hooks": recent_events(80),
    }


def app(environ, start_response):
    ensure_runtime(); ensure_archive()
    path = environ.get("PATH_INFO", "/")
    qs = parse_qs(environ.get("QUERY_STRING", ""))
    if path == "/api/state":
        payload = json.dumps(_state_data(), ensure_ascii=False, indent=2).encode("utf-8")
        start_response("200 OK", [("Content-Type", "application/json; charset=utf-8"), ("Cache-Control", "no-store")])
        return [payload]
    if path == "/api/content":
        data = _state_data()
        payload = json.dumps(data.get("module_content", {}), ensure_ascii=False, indent=2).encode("utf-8")
        start_response("200 OK", [("Content-Type", "application/json; charset=utf-8"), ("Cache-Control", "no-store")])
        return [payload]
    if path == "/api/search":
        query = qs.get("q", [""])[0]
        bureau = qs.get("bureau", [None])[0] or None
        task_type = qs.get("task_type", [None])[0] or None
        payload = json.dumps({"results": search(query, bureau=bureau, task_type=task_type, top_k=8)}, ensure_ascii=False, indent=2).encode("utf-8")
        start_response("200 OK", [("Content-Type", "application/json; charset=utf-8")])
        return [payload]
    if path.startswith("/api/tasks/"):
        task_id = path.removeprefix("/api/tasks/").strip("/")
        report = _task_report(_find_task(task_id))
        if not report:
            start_response("404 Not Found", [("Content-Type", "application/json; charset=utf-8")])
            return [json.dumps({"error": "task not found", "task_id": task_id}, ensure_ascii=False).encode("utf-8")]
        payload = json.dumps(report, ensure_ascii=False, indent=2).encode("utf-8")
        start_response("200 OK", [("Content-Type", "application/json; charset=utf-8"), ("Cache-Control", "no-store")])
        return [payload]
    selected_task = None
    if path.startswith("/tasks/"):
        task_id = path.removeprefix("/tasks/").strip("/")
        selected_task = _task_report(_find_task(task_id))
        if not selected_task:
            start_response("404 Not Found", [("Content-Type", "text/plain; charset=utf-8")])
            return [f"task not found: {task_id}".encode("utf-8")]
        path = "/tasks"
    if path in {"/", "/overview", "/memory", "/skills-core", "/skills-worker", "/context-units", "/hooks-runtime", "/mcp-rag", "/headless", "/sdk-adapters", "/templates", "/layers", "/agents", "/tasks", "/hooks", "/archive", "/docs"}:
        section = "overview" if path in {"/", "/overview"} else path.strip("/")
        # Backward compatibility for old links: /?section=tasks
        if path == "/":
            requested = qs.get("section", [section])[0]
            section = requested if requested in SECTIONS else "overview"
        item = SECTIONS.get(section, SECTIONS["overview"])
        data = _state_data()
        tpl = env.get_template("dashboard.html")
        html = tpl.render(
            section=section,
            section_title=item["title"],
            section_hint=item["hint"],
            nav=NAV,
            selected_task=selected_task,
            initial_state=data,
            **data,
        ).encode("utf-8")
        start_response("200 OK", [("Content-Type", "text/html; charset=utf-8"), ("Cache-Control", "no-store")])
        return [html]
    start_response("404 Not Found", [("Content-Type", "text/plain; charset=utf-8")])
    return [b"not found"]


def serve(host: str = "127.0.0.1", port: int = 8788) -> str:
    ensure_runtime(); ensure_archive()
    httpd = make_server(host, port, app)
    httpd.serve_forever()
    return f"http://{host}:{port}/"
