from __future__ import annotations
from .model import TaskPacket, TASKS, REPORTS, STATE, now, slug, write_json, read_json
from .hooks import hook_task_created

DEFAULT_FORBIDDEN = [".env", "*token*", "*auth*", "~/.hermes/auth.json", "public_publish_without_review", "destructive_delete"]
DEFAULT_ALLOWED = ["projects/", "memory/", "skills/", "context_units/", "hooks/", "mcp/", "sdk/", "dashboard/", "adapters/", "templates/", "reports/", "STATE/", "runtime/", "docs/"]

CORE_FRAMEWORK_KEYS = ["记忆", "skill", "上下文", "hook", "mcp", "headless", "sdk", "dashboard", "兼容", "codex", "claude", "openclaw", "子工程"]


def _needs_full_framework_plan(request: str) -> bool:
    lower = request.lower()
    return ("框架" in request or "agent" in lower) and sum(1 for k in CORE_FRAMEWORK_KEYS if k.lower() in lower) >= 4


def _task(base_id: str, suffix: str, title: str, task_type: str, worker: str, objective: str, context: str,
          allowed_paths=None, criteria=None, gates=None) -> TaskPacket:
    allowed_paths = allowed_paths or DEFAULT_ALLOWED
    criteria = criteria or ["产出可落地文件", "说明宿主兼容性", "标注来源/边界", "保留扩展点", "完成自我质疑"]
    gates = gates or ["scope_gate", "compatibility_gate", "source_attribution_gate", "output_gate", "self_critique_gate"]
    return TaskPacket(
        task_id=f"{base_id}-{suffix}",
        title=title[:90],
        task_type=task_type,
        worker=worker,
        objective=objective,
        context=context,
        allowed_paths=allowed_paths,
        forbidden_paths=DEFAULT_FORBIDDEN,
        acceptance_criteria=criteria,
        required_outputs=[f"runtime/outputs/{base_id}-{suffix}.md"],
        gates=gates,
        created_at=now(),
        parent_request=context,
    )


def _make_full_framework_plan(decision) -> list[TaskPacket]:
    request = decision.request
    base_id = f"T-{now()}-framework"
    tasks: list[TaskPacket] = []
    if decision.needs_autoresearch:
        tasks.append(_task(base_id, "research", "兼容性与竞品调研：" + request[:42], "research", "research_worker",
            "调研 Hermes/Codex/Claude Code/OpenClaw/OpenCode 等宿主差异，列出可抽象层与必须署名来源。", request,
            criteria=["列出宿主能力差异", "列出不能声称原创的 Hermes 机制", "给 SDK/adapter worker 输入摘要"], gates=["report_gate", "source_attribution_gate"]))
    tasks.extend([
        _task(base_id, "strategy", "顶层框架路线：" + request[:46], "strategy", "cabinet_strategy_worker",
              "定义该 GitHub 作品的总贡献、边界、模块图、子工程定位和演进路线。", request),
        _task(base_id, "memory", "内阁-六部记忆系统：" + request[:40], "memory", "memory_steward_worker",
              "建立 memory 目录、内阁高层记忆和六部分层记忆的读写协议、冲突规则与检索方式。", request),
        _task(base_id, "thinking-skills", "核心思考 skill 迁移：" + request[:38], "thinking_skill", "thinking_skill_curator_worker",
              "把核心思考层 skills 独立成 skills/thinking，并写清适用对象是高级 AI/规划层。", request),
        _task(base_id, "worker-skills", "worker skill 封装：" + request[:38], "worker_skill", "worker_skill_builder_worker",
              "建立 skills/worker，面向开源/小参数模型的可执行工作卡、检查表和输入输出契约。", request),
        _task(base_id, "context-units", "上下文单元与内阁-六部：" + request[:36], "context_unit", "context_unit_worker",
              "定义多智能体上下文单元、角色包、交接包、压缩摘要和部门边界。", request),
        _task(base_id, "hooks", "Hooks 生命周期闭环：" + request[:42], "hooks", "hook_lifecycle_worker",
              "补全任务生命周期、前置审权、执行后检查、归档、审计、失败停止和报告闭环。", request),
        _task(base_id, "mcp-rag", "MCP / RAG 工具层：" + request[:42], "mcp_rag", "mcp_rag_worker",
              "设计可选 MCP、向量索引、RAG 检索、工具注册和未来维护接口。", request),
        _task(base_id, "headless", "Headless 昼夜运行：" + request[:42], "headless", "headless_ops_worker",
              "设计后台守护、队列推进、心跳、失败阈值、dashboard 监督和人工接管点。", request),
        _task(base_id, "sdk-adapters", "Agent SDK 与宿主适配：" + request[:38], "sdk_adapter", "sdk_adapter_worker",
              "建立 Hermes/Codex/Claude Code/OpenClaw/generic CLI 适配层，不绑定单一宿主。", request),
        _task(base_id, "dashboard", "Dashboard 监督中枢：" + request[:42], "dashboard", "dashboard_worker",
              "把 dashboard 定位为监督，不承担会话；展示项目、任务、记忆、skills、hooks、headless、审计。", request),
        _task(base_id, "templates", "子工程模板体系：" + request[:42], "domain_template", "domain_template_worker",
              "定义数据平台、小说/OC/IP、研究、工程等子工程模板，支持稍改命令即可生成。", request),
        _task(base_id, "docs", "GitHub 作品集说明：" + request[:42], "docs", "documentation_worker",
              "写 README、架构文档、能力边界、Hermes 来源声明、快速开始和贡献扩展指南。", request),
    ])
    return tasks


def make_packet(decision) -> list[TaskPacket]:
    if _needs_full_framework_plan(decision.request):
        return _make_full_framework_plan(decision)
    base_id = f"T-{now()}-{slug(decision.task_type)}"
    tasks: list[TaskPacket] = []
    if decision.needs_autoresearch and decision.primary_worker != "research_worker":
        tasks.append(_task(base_id, "research", "autoresearch: " + decision.request[:40], "research", "research_worker",
            "先调研不确定点，给出兼容性、来源边界、风险和推荐路线。", decision.request,
            criteria=["有参考边界", "有推荐路线", "说明影响哪些 worker"], gates=["report_gate", "source_attribution_gate"]))
    tasks.append(_task(base_id, "main", decision.request[:60], decision.task_type, decision.primary_worker,
        "根据用户目标完成本领域框架建设任务，产出本地成果、更新日志和自我质疑。", decision.request))
    return tasks


def persist_tasks(tasks: list[TaskPacket]) -> None:
    for t in tasks:
        data = t.to_dict()
        write_json(TASKS / f"{t.task_id}.json", data)
        hook_task_created(data)
    state = read_json(STATE / "project.json", {}) or {}
    state["tasks_created"] = int(state.get("tasks_created", 0)) + len(tasks)
    state["last_summary"] = f"创建 {len(tasks)} 个任务：" + ", ".join(t.task_id for t in tasks)
    write_json(STATE / "project.json", state)


def summarize() -> str:
    task_files = sorted(TASKS.glob("*.json"))
    tasks = [read_json(p) for p in task_files]
    ready = [t for t in tasks if t.get("status") == "ready"]
    done = [t for t in tasks if t.get("status") == "done"]
    blocked = [t for t in tasks if t.get("status") in {"blocked", "failed"}]
    lines = ["# Runtime Status Summary", "", f"- total: {len(tasks)}", f"- ready: {len(ready)}", f"- done: {len(done)}", f"- blocked/failed: {len(blocked)}", "", "## Ready Tasks"]
    for t in ready: lines.append(f"- {t['task_id']} -> {t['worker']}: {t['title']}")
    lines += ["", "## Done Tasks"]
    for t in done[-10:]: lines.append(f"- {t['task_id']} -> {t['worker']}")
    text = "\n".join(lines) + "\n"
    out = REPORTS / "runtime_summary.md"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(text, encoding="utf-8")
    state = read_json(STATE / "project.json", {}) or {}
    state["last_summary"] = "runtime/reports/runtime_summary.md"
    write_json(STATE / "project.json", state)
    return text
