# Cabinet Agent Framework（内阁式 Agent 框架）

这是一个可上传 GitHub、可作为求职作品展示的项目级 agent framework。数据平台 MVP、小说/OC/IP MVP 都是它管理的子工程，不是框架本体。

## 一句话

把一个项目目录变成可被 Hermes / Codex / Claude Code / OpenClaw 等宿主 agent 共同理解和执行的 agent operating system。

## 快速验证

```bash
python3 -m cabinet_framework.cli init
python3 -m unittest discover -s tests -v
python3 -m cabinet_framework.cli gate
python3 -m cabinet_framework.cli chat-intake --authority L2 --request "建设跨 Hermes/Codex/Claude Code/OpenClaw 的 agent 框架，包含记忆、skills、上下文、hooks、MCP、headless、SDK、dashboard、子工程模板"
```

## 核心模块

- 记忆系统：`memory/` 下内阁 + 吏户礼兵刑工。
- Skills：`skills/thinking/` 与 `skills/worker/` 分离。
- 上下文单元：`context_units/`。
- Hooks：生命周期、门禁、失败停止和审计。
- MCP/RAG：可选 typed tool 和向量索引接口。
- Headless：队列、心跳、后台推进、人工接管。
- Agent SDK：TaskPacket、worker registry、adapter、hook、memory、skill loader。
- Dashboard：监督视图，不做会话入口。
- 子工程模板：数据平台、小说/OC/IP、研究、工程等 managed subprojects。

## Hermes 来源声明

本项目会适配/借鉴 Hermes 的 skills、tools、cron、gateway、MCP、delegation 等机制。文档中必须标注 Hermes-native path，不能把 Hermes 已有能力冒充成本框架原创。
