# GitHub 提交说明

如果上传 GitHub，不是上传一堆 MD，而是上传一个最小可用 AI Coding Harness：

## 包含

- `cabinet_framework/`：可运行 MVP 代码。
- `pyproject.toml`：项目元信息。
- `AGENTS.md` / `SOUL.md`：agent 启动规则与身份。
- `FRAMEWORK.md` / `TASK_MODEL.md`：架构与任务模型。
- `AUTO_RESEARCH_PROTOCOL.md` / `AUTONOMOUS_DEV_PROTOCOL.md` / `SELF_ITERATION_PROTOCOL.md` / `SELF_CRITIQUE_PROTOCOL.md`：自主能力协议。
- `SKILL_POLICY.md` / `HOOKS_POLICY.md` / `MCP_POLICY.md` / `CHECK_PROTOCOL.md`：harness 治理层。

## 能演示

```bash
python3 -m cabinet_framework.cli init
python3 -m cabinet_framework.cli intake --request "为高性能数据分析平台设计图表大数据渲染方案，需要调研技术选型、性能取舍和维护策略"
python3 -m cabinet_framework.cli tasks
python3 -m cabinet_framework.cli tick --mode prompt
python3 -m cabinet_framework.cli gate
```

## 证明点

- 不是单任务 prompt。
- 有领袖/中书/worker 分层。
- 有 autoresearch。
- 有挂机 tick。
- 有 worker prompt 生成。
- 有 self critique 和 skill iteration 要求。
- 有 gates。
- 可进一步接 `tick --mode hermes` 变成真实 agent 执行。
