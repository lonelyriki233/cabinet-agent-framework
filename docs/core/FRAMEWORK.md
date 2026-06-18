# Cabinet Agent Framework

```text
User / Host Agent
  -> Conversation Bridge
  -> Leader Gateway
  -> Strategy Council
  -> Chief Coordinator
  -> Mandate Relay
  -> Cabinet + Six Ministries
  -> Domain Workers
  -> Hooks / Gates
  -> Archive / Memory / RAG
  -> Dashboard Supervision
```

定位：这是一个项目级 agent operating system。它不等于某个数据平台或小说项目；那些是它管理的子工程。

设计原则：
1. 兼容性：核心协议用文件、JSON、Markdown、CLI，不绑定 Hermes。
2. 扩展性：部门、worker、模板、hooks、MCP 都可追加。
3. 移植性：复制到项目根目录后，Claude Code/Codex/Hermes/OpenClaw 可读取 AGENTS/README 并执行。
4. 可演化：不要封死命名、模型、工具和项目类型。
