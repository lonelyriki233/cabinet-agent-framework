# Hermes Attribution

本项目会借鉴/适配 Hermes Agent 的若干机制：skills、memory、cron/headless、gateway、toolsets、MCP、delegation、kanban 等。

这些能力在文档中必须明确标注：
- `Hermes-native path`：只有 Hermes 下可直接使用。
- `Portable abstraction`：本框架抽象出的通用协议。
- `Adapter implementation`：对某个宿主的实现。

不得把 Hermes 已有机制说成完全由本框架原创。
