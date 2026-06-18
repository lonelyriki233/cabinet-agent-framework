from __future__ import annotations
from pathlib import Path
from .model import TASKS, LOGS, read_json, write_json, write_text, ROOT
from .hermes_bridge import execute_hermes_worker, shell_command_for_prompt
from .hooks import hook_before_task_run, hook_after_task_run


def build_worker_prompt(task: dict) -> str:
    return f"""
你是 {task['worker']}，属于 Cabinet Agent Framework 的领域 worker。

框架原则：
- 这是宿主无关的 agent 框架，不只能在 Hermes 下运行。
- Hermes 机制可以借鉴/适配，但必须标注来源，不得说成框架原创。
- thinking skill 面向高级 AI 的判断和规划；worker skill 面向开源/小参数模型的可执行工作。
- 内阁-六部体系是上下文和记忆治理结构；各部门只写本部门记忆，内阁维护高层记忆。
- 所有设计都要尊重后人智慧：保留扩展点，少写死，少封死未来。

任务ID：{task['task_id']}
任务类型：{task['task_type']}
目标：{task['objective']}
上下文：{task['context']}
允许路径：{', '.join(task['allowed_paths'])}
禁止路径：{', '.join(task['forbidden_paths'])}
验收标准：{'; '.join(task['acceptance_criteria'])}
必须输出：{'; '.join(task['required_outputs'])}

执行要求：
1. 只在允许路径内创建/修改文件。
2. 把结果写入 required_outputs 的第一个路径。
3. 输出必须包含：当前设计、可扩展点、兼容性说明、风险/失败模式、后续增强建议。
4. 若涉及 Hermes、Codex、Claude Code、OpenClaw 等宿主，必须区分“框架抽象层”和“宿主适配层”。
5. 若涉及 skills，必须区分 thinking skills 与 worker skills。
6. 若涉及记忆，必须按内阁/吏户礼兵刑工分层。
7. 末尾写“自我质疑”：我可能哪里过度设计、哪里写死、哪里需要后人扩展。
8. 不要编造已运行的测试、外部事实或未实现能力。
""".strip()


def run_task(task_path: Path, mode: str = "prompt") -> str:
    task = read_json(task_path)
    if not task:
        raise SystemExit(f"task not found: {task_path}")
    ok, rec = hook_before_task_run(task)
    if not ok:
        task["status"] = "blocked"; task["blocker"] = rec.get("details", {}); write_json(task_path, task)
        return f"HOOK_BLOCKED task.before_run {task.get('task_id')}"
    prompt = build_worker_prompt(task)
    prompt_path = LOGS / f"{task['task_id']}.worker_prompt.txt"
    write_text(prompt_path, prompt)
    if mode == "prompt":
        task["status"] = "prompted"; task["worker_prompt"] = str(prompt_path.relative_to(ROOT)); write_json(task_path, task)
        hook_after_task_run(task, mode, "PROMPT_WRITTEN")
        return f"PROMPT_WRITTEN {prompt_path.relative_to(ROOT)}"
    if mode == "hermes":
        code, log, reason = execute_hermes_worker(task_path, prompt, authority_level=task.get("authority_level", "L2"))
        task["status"] = "done" if code == 0 else ("blocked" if code == 127 else "failed")
        if code != 0: task["blocker"] = reason
        task["hermes_log"] = str(log.relative_to(ROOT)); write_json(task_path, task)
        ok, rec = hook_after_task_run(task, mode, f"HERMES_RUN exit={code}")
        if not ok:
            task["status"] = "failed"; task["blocker"] = rec.get("details", {}); write_json(task_path, task)
        return f"HERMES_RUN exit={code} log={log.relative_to(ROOT)}"
    raise SystemExit("mode must be prompt or hermes")


def next_ready_task() -> Path | None:
    for p in sorted(TASKS.glob("*.json")):
        t = read_json(p)
        if t and t.get("status") == "ready": return p
    return None


def tick(mode: str = "prompt") -> str:
    p = next_ready_task()
    if not p: return "NO_READY_TASK"
    return run_task(p, mode=mode)


def worker_command(task_path: Path) -> str:
    task = read_json(task_path)
    if not task: raise SystemExit(f"task not found: {task_path}")
    prompt = build_worker_prompt(task)
    return shell_command_for_prompt(prompt, task.get("worker", "unknown"), task.get("authority_level", "L1"))
