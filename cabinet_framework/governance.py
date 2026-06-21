from __future__ import annotations
from dataclasses import dataclass, asdict

FORBIDDEN_RISK_WORDS = ["密钥", "token", "auth", "公开发布", "商用发布", "付费", "删除", "不可逆"]
RESEARCH_WORDS = ["调研", "参考", "比较", "兼容", "未知", "不确定", "codex", "claude", "openclaw", "mcp"]

COUNCILLORS = {
    "prime_minister": "内阁首辅：总路线、优先级、跨部门冲突、项目作品集定位",
    "memory_councillor": "记忆参议：长期记忆、高层记忆、部门记忆、上下文压缩",
    "skill_councillor": "技能参议：thinking skill / worker skill 分离、迁移、版本治理",
    "runtime_councillor": "运行参议：hooks、headless、调度、stop gate、生命周期闭环",
    "interop_councillor": "兼容参议：Hermes/Codex/Claude Code/OpenClaw/通用 CLI 适配",
    "tooling_councillor": "工具参议：MCP、RAG、SDK、dashboard、工程模板",
    "risk_councillor": "刑名参议：权限、审计、密钥、来源署名、失败模式",
}

DOMAIN_BUREAUS = {
    "cabinet_office": "内阁：高层目标、路线、决策、跨部门协调",
    "civil_service_ministry": "吏部：agent/worker 编制、上下文单元、角色任免",
    "finance_ministry": "户部：资源、成本、数据资产、向量索引、指标",
    "ritual_ministry": "礼部：知识、skills、文档、prompt 礼制、对外说明",
    "war_ministry": "兵部：执行、调度、headless、任务推进和异常处置",
    "justice_ministry": "刑部：权限、审计、风险、回滚、失败复盘",
    "works_ministry": "工部：工程、SDK、MCP、dashboard、项目模板",
}

WORKER_TO_BUREAU = {
    "cabinet_strategy_worker": "cabinet_office",
    "memory_steward_worker": "civil_service_ministry",
    "thinking_skill_curator_worker": "ritual_ministry",
    "worker_skill_builder_worker": "ritual_ministry",
    "context_unit_worker": "civil_service_ministry",
    "hook_lifecycle_worker": "war_ministry",
    "mcp_rag_worker": "works_ministry",
    "headless_ops_worker": "war_ministry",
    "sdk_adapter_worker": "works_ministry",
    "dashboard_worker": "works_ministry",
    "domain_template_worker": "works_ministry",
    "documentation_worker": "ritual_ministry",
    "research_worker": "finance_ministry",
    "skill_forge_worker": "ritual_ministry",
    "autonomous_dispatch_worker": "war_ministry",
}

TASK_TOKEN_BUDGETS = {
    "strategy": {"max_turns": 60, "fast_path": False, "full_council": True},
    "memory": {"max_turns": 45, "fast_path": True, "full_council": False},
    "thinking_skill": {"max_turns": 55, "fast_path": True, "full_council": False},
    "worker_skill": {"max_turns": 55, "fast_path": True, "full_council": False},
    "context_unit": {"max_turns": 50, "fast_path": True, "full_council": False},
    "hooks": {"max_turns": 45, "fast_path": True, "full_council": False},
    "mcp_rag": {"max_turns": 60, "fast_path": True, "full_council": False},
    "headless": {"max_turns": 50, "fast_path": True, "full_council": False},
    "sdk_adapter": {"max_turns": 65, "fast_path": True, "full_council": False},
    "dashboard": {"max_turns": 50, "fast_path": True, "full_council": False},
    "domain_template": {"max_turns": 50, "fast_path": True, "full_council": False},
    "docs": {"max_turns": 35, "fast_path": True, "full_council": False},
    "research": {"max_turns": 45, "fast_path": True, "full_council": False},
    "skill_forge": {"max_turns": 55, "fast_path": True, "full_council": True},
    "autonomous": {"max_turns": 80, "fast_path": True, "full_council": True},
}

AUDIT_STRATEGY = {k: "end" for k in TASK_TOKEN_BUDGETS}
AUDIT_STRATEGY["docs"] = "full"
AUDIT_STRATEGY["research"] = "skip"
AUDIT_STRATEGY["skill_forge"] = "full"
AUDIT_STRATEGY["autonomous"] = "full"

COUNCILLOR_ACTIVATION = {
    "strategy": {"prime_minister", "memory", "skill", "runtime", "interop", "tooling", "risk"},
    "memory": {"prime_minister", "memory", "risk"},
    "thinking_skill": {"skill", "risk"},
    "worker_skill": {"skill", "runtime"},
    "context_unit": {"memory", "runtime"},
    "hooks": {"runtime", "risk"},
    "mcp_rag": {"tooling", "memory", "risk"},
    "headless": {"runtime", "risk"},
    "sdk_adapter": {"interop", "tooling", "risk"},
    "dashboard": {"tooling", "runtime"},
    "domain_template": {"prime_minister", "tooling", "skill"},
    "docs": {"skill", "risk"},
    "research": {"tooling", "interop"},
    "skill_forge": {"prime_minister", "skill", "runtime", "risk"},
    "autonomous": {"prime_minister", "skill", "runtime", "risk", "tooling"},
}
ORDER = ["prime_minister", "memory", "skill", "runtime", "interop", "tooling", "risk"]


def budget_for(task_type: str) -> dict:
    return TASK_TOKEN_BUDGETS.get(task_type, {"max_turns": 45, "fast_path": True, "full_council": False})


def should_audit(task_type: str, task_status: str, tick_count: int = -1) -> bool:
    s = AUDIT_STRATEGY.get(task_type, "end")
    if s == "skip": return False
    if s == "full": return True
    return task_status == "done"


@dataclass
class CouncilDraft:
    active_councillors: list[str]
    principal_contradiction: str
    draft_mandate: str
    audit_questions: list[str]
    def to_dict(self): return asdict(self)


@dataclass
class MandateDecision:
    authority_level: str
    approved: bool
    requires_user: bool
    reason: str
    allowed_next_action: str
    def to_dict(self): return asdict(self)


def convene_strategy_council(request: str, primary_worker: str, needs_autoresearch: bool, task_type: str = "strategy") -> CouncilDraft:
    base = COUNCILLOR_ACTIVATION.get(task_type, {"prime_minister", "runtime"}).copy()
    lower = request.lower()
    if needs_autoresearch or any(w.lower() in lower for w in RESEARCH_WORDS): base.add("tooling"); base.add("interop")
    if any(w in lower for w in ["公开发布", "商用", "密钥", "token", "auth", "删除"]): base.add("risk")
    active = [f"{x}_councillor" if not x.endswith("minister") and x != "prime_minister" else x for x in sorted(base, key=lambda x: ORDER.index(x) if x in ORDER else 9)]
    contradiction = "强框架一致性 vs 未来扩展自由度"
    if "兼容" in request or "codex" in lower or "claude" in lower: contradiction = "统一治理抽象 vs 各 agent 宿主能力差异"
    if "skill" in lower: contradiction = "高级思考 skill 的抽象性 vs worker skill 的可执行性"
    budget = budget_for(task_type)
    draft = f"由 {', '.join(active)} 参议；主执行归 {primary_worker}；fast_path={budget['fast_path']} max_turns={budget['max_turns']}；所有 Hermes 机制必须标注来源。"
    audit_questions = [
        "是否保持宿主无关，不把 Hermes 专属能力写成框架原创必需能力？",
        "是否把 thinking skill 与 worker skill 分开？",
        "是否保留扩展点而不是写死任务域、部门和模型？",
        "是否能被放入任意项目后由 Claude Code/Codex/Hermes/OpenClaw 读取执行？",
    ]
    return CouncilDraft(active, contradiction, draft, audit_questions)


def relay_mandate(request: str, authority_level: str = "L1") -> MandateDecision:
    risky = [w for w in FORBIDDEN_RISK_WORDS if w.lower() in request.lower()]
    if risky:
        return MandateDecision(authority_level, False, True, f"触碰高风险词: {', '.join(risky)}", "升级给用户授权")
    if authority_level == "L0":
        return MandateDecision(authority_level, False, False, "当前仅允许建议，不生成任务包", "output_advice")
    if authority_level == "L1":
        return MandateDecision(authority_level, True, False, "允许生成任务包和 worker prompt，不直接运行 worker", "create_task_packet")
    if authority_level in {"L2", "L3"}:
        return MandateDecision(authority_level, True, False, "允许低风险自动执行；每轮必须过 gate，失败即停", "dispatch_or_tick")
    return MandateDecision(authority_level, False, True, "未知授权等级", "ask_user")
