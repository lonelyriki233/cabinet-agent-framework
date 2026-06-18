# Host Adapters

目标：同一套任务包可被不同宿主执行。

- Hermes：通过 `hermes_bridge.py`、Hermes skills、cron、gateway、tools。
- Codex：通过 CLI/ACP/工作目录指令读取 AGENTS.md 与任务包。
- Claude Code：通过 CLAUDE.md/commands/hooks 风格适配。
- OpenClaw/OpenCode：通过通用 CLI agent adapter。

适配层不得污染核心协议。
