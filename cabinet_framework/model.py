from __future__ import annotations
from dataclasses import dataclass, asdict
from pathlib import Path
from datetime import datetime
import json, re

ROOT = Path(__file__).resolve().parents[1]
RUNTIME = ROOT / "runtime"
TASKS = RUNTIME / "tasks"
OUTPUTS = RUNTIME / "outputs"
REPORTS = RUNTIME / "reports"
LOGS = RUNTIME / "logs"
STATE = RUNTIME / "state"
MEMORY = ROOT / "memory"
SKILLS = ROOT / "skills"
PROJECTS = ROOT / "projects"

CABINET_SYSTEM = {
    "cabinet": "内阁集群：维护高层目标、路线、重大决策、跨部门协调和最终风险边界。",
    "civil_service": "吏部：agent/worker 编制、角色任免、能力登记、上下文单元维护。",
    "finance": "户部：资源、预算、成本、数据资产、向量索引、运行指标。",
    "ritual": "礼部：知识、文档、skills、提示词规范、对外说明和交付礼制。",
    "war": "兵部：执行、调度、headless 运行、任务推进、异常处置。",
    "justice": "刑部：权限、审计、风险、回滚、合规和失败复盘。",
    "works": "工部：工程实现、SDK、MCP、工具、dashboard、项目模板。",
}

WORKERS = {
    "cabinet_strategy_worker": "高层路线、任务拆解、跨部门协调、项目蓝图",
    "memory_steward_worker": "内阁-六部记忆归档、检索、摘要和冲突整理",
    "thinking_skill_curator_worker": "核心思考 skill 的迁移、脱敏、版本和适用边界",
    "worker_skill_builder_worker": "小模型/开源模型可执行 worker skill、任务卡和检查表",
    "context_unit_worker": "多智能体上下文单元、角色包、交接包、压缩摘要",
    "hook_lifecycle_worker": "钩子、生命周期、门禁、闭环和失败停止条件",
    "mcp_rag_worker": "MCP、向量库、RAG、工具接口和知识索引",
    "headless_ops_worker": "昼夜运行、守护进程、队列、心跳、dashboard 监督",
    "sdk_adapter_worker": "Hermes/Codex/Claude Code/OpenClaw 适配器和 Agent SDK",
    "dashboard_worker": "监督仪表盘、运行态势、项目内容页、审计视图",
    "domain_template_worker": "把框架套到数据平台、小说/OC/IP、研究、工程等子项目",
    "documentation_worker": "README、架构说明、GitHub 作品集文档、真实能力边界",
    "research_worker": "外部参考、竞品/趋势、兼容性调研和方案取舍",
    "skill_forge_worker": "SkillForge：当可用 skill 不足时自动发现、调研、创建、注册新 skill",
    "autonomous_dispatch_worker": "自主调度器：自动 intake → dispatch → audit 的全链路绑定",
}

TASK_TYPE_KEYWORDS = {
    "strategy": ["框架", "项目", "作品", "github", "求职", "顶层", "路线"],
    "memory": ["记忆", "memory", "内阁", "六部", "归档"],
    "thinking_skill": ["思考skill", "思考 skill", "核心思考", "thinking"],
    "worker_skill": ["worker skill", "woker", "工作skill", "小模型", "开源模型"],
    "context_unit": ["上下文", "多智能体", "协调", "context"],
    "hooks": ["hook", "hooks", "钩子", "生命周期", "闭环"],
    "mcp_rag": ["mcp", "rag", "向量", "vector", "数据库"],
    "headless": ["headless", "昼夜", "守护", "daemon", "后台"],
    "sdk_adapter": ["sdk", "codex", "claude", "openclaw", "opencode", "hermes", "兼容"],
    "dashboard": ["dashboard", "仪表盘", "监督", "页面"],
    "domain_template": ["子工程", "模板", "平台", "小说", "oc", "ip", "数据平台"],
    "docs": ["文档", "readme", "说明", "交付", "上传"],
    "research": ["调研", "参考", "竞品", "比较", "未知"],
    "skill_forge": ["skill", "forge", "创建skill", "技能", "新领域", "不会做", "没有skill"],
    "autonomous": ["自动", "调度", "auto", "intake", "全链路", "自主"],
}

TASK_TO_WORKER = {
    "strategy": "cabinet_strategy_worker",
    "memory": "memory_steward_worker",
    "thinking_skill": "thinking_skill_curator_worker",
    "worker_skill": "worker_skill_builder_worker",
    "context_unit": "context_unit_worker",
    "hooks": "hook_lifecycle_worker",
    "mcp_rag": "mcp_rag_worker",
    "headless": "headless_ops_worker",
    "sdk_adapter": "sdk_adapter_worker",
    "dashboard": "dashboard_worker",
    "domain_template": "domain_template_worker",
    "docs": "documentation_worker",
    "research": "research_worker",
    "skill_forge": "skill_forge_worker",
    "autonomous": "autonomous_dispatch_worker",
}

AUTORESEARCH_KEYWORDS = ["调研", "参考", "兼容", "codex", "claude", "openclaw", "mcp", "sdk", "github", "求职"]


def ensure_runtime() -> None:
    for d in [RUNTIME, TASKS, OUTPUTS, REPORTS, LOGS, STATE, MEMORY, SKILLS, PROJECTS]:
        d.mkdir(parents=True, exist_ok=True)
    state_file = STATE / "project.json"
    if not state_file.exists():
        write_json(state_file, {
            "status": "ready",
            "current_direction": "Cabinet Agent Framework: portable multi-agent runtime with cabinet-six-ministries governance",
            "tasks_created": 0,
            "tasks_done": 0,
            "blockers": [],
            "last_summary": None,
            "archive_indexed": 0,
            "dashboard_port": 8788,
            "supported_hosts": ["Hermes", "Codex", "Claude Code", "OpenClaw/OpenCode", "generic CLI agents"],
        })


def now() -> str:
    return datetime.now().strftime("%Y%m%d-%H%M%S")


def slug(text: str) -> str:
    s = re.sub(r"[^a-zA-Z0-9\u4e00-\u9fff_-]+", "-", text).strip("-")
    return s[:36] or "task"


def read_json(path: Path, default=None):
    if not path.exists():
        return default
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, data) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")


def write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


@dataclass
class LeaderDecision:
    request: str
    task_type: str
    needs_secretariat: bool
    needs_autoresearch: bool
    primary_worker: str
    risk_level: str
    reason: str

    def to_dict(self):
        return asdict(self)


@dataclass
class TaskPacket:
    task_id: str
    title: str
    task_type: str
    worker: str
    objective: str
    context: str
    allowed_paths: list[str]
    forbidden_paths: list[str]
    acceptance_criteria: list[str]
    required_outputs: list[str]
    gates: list[str]
    status: str = "ready"
    created_at: str = ""
    parent_request: str = ""

    def to_dict(self):
        return asdict(self)
