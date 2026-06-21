from __future__ import annotations
from .model import LeaderDecision, TASK_TYPE_KEYWORDS, TASK_TO_WORKER, AUTORESEARCH_KEYWORDS


def classify_request(request: str) -> LeaderDecision:
    text = request.lower()
    task_type = "strategy"
    for kind, keys in TASK_TYPE_KEYWORDS.items():
        if any(k.lower() in text for k in keys):
            task_type = kind
            break
    worker = TASK_TO_WORKER.get(task_type, "cabinet_strategy_worker")
    needs_autoresearch = any(k.lower() in text for k in AUTORESEARCH_KEYWORDS)
    broad = sum(1 for k in ["记忆", "skill", "上下文", "hook", "mcp", "headless", "sdk", "dashboard", "模板", "github"] if k.lower() in text) >= 3
    needs_secretariat = broad or len(request) > 8 or needs_autoresearch
    risk_level = "high" if any(k.lower() in text for k in ["密钥", "token", "auth", "公开发布", "商用发布", "付费", "删除"] ) else "normal"
    reason = f"任务类型={task_type}; 主 worker={worker}; broad={broad}; autoresearch={needs_autoresearch}; 风险={risk_level}"
    return LeaderDecision(request, task_type, needs_secretariat, needs_autoresearch, worker, risk_level, reason)
