# Task Model

每个任务包至少包含：task_id、title、task_type、worker、objective、context、allowed_paths、forbidden_paths、acceptance_criteria、required_outputs、gates、status、parent_request。

任务包是跨宿主协议：Hermes、Codex、Claude Code、OpenClaw 都可以读取同一 JSON/Markdown 任务。
