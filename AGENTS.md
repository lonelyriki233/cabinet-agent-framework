# AGENTS.md - Cabinet Agent Framework

本目录是可上传 GitHub 的跨宿主 agent 框架项目。先读 SOUL.md、USER_INTENT.md、docs/core/FRAMEWORK.md、docs/core/TASK_MODEL.md、docs/README.md。

边界：框架本体负责记忆、skills、上下文、hooks、MCP/RAG、headless、SDK/adapters、dashboard 和子工程模板；数据平台 MVP、小说/OC/IP MVP 都是 managed subprojects，不是框架本体。

宿主兼容：必须区分通用抽象层与 Hermes/Codex/Claude Code/OpenClaw 等宿主适配层。Hermes 机制可以迁移，但要明确标注来源，不得冒充原创。
