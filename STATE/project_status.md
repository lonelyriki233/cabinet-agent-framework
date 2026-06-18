# Project Status

## 当前项目

Cabinet Agent Framework。

## 当前定位

一个可运行的 AI Agent 开发框架，而非业务 demo。

## 关键边界

- 框架本体是 MVP。
- 用户交给框架管理的工程任务不是框架本体。
- dashboard 里的 worker 数量和任务分布代表“被管理工程的工作负载”，不代表框架只会做这些事。
- 如果用户要求搭建平台，框架应该把平台拆成后端、前端、数据性能、监控质量、文档等多领域任务，而不是把平台叫成 MVP。

## 当前框架已固化

- 用户任务入口
- Leader Gateway
- Strategy Council
- Chief Coordinator
- Mandate Relay
- Domain Bureaus
- Audit Office
- State Archive
- worker registry
- context protocol
- reporting protocol
- skills policy
- hooks policy
- MCP policy
- check protocol
- autoresearch protocol
- continuous dispatcher
- dashboard
- layered archive
- conversation bridge

## 下一步

用户在 Hermes 对话中给出任务后，先登记进入 runtime，再由框架拆解、执行、审计和归档.

## 对话任务入口规则

本窗口后续行动任务必须先登记进 runtime，再按 Leader Gateway -> Chief Coordinator -> Worker -> Audit -> Archive 路线执行。

本规则已登记到 runtime：`T-20260611-140641-architecture-main`。

## 被管理工程示例：高性能数据分析平台

仓库内存在一个本地高性能数据分析平台原型，作为框架可管理的工程样例，不是框架本体：

- 本地 WSGI 服务入口：`python3 -m cabinet_framework.cli perf-platform --port 8790`
- 页面：`web/templates/perf_platform.html`
- 服务端：`cabinet_framework/perf_platform.py`
- API：`/api/overview`、`/api/live`、`/api/dense-series`
- dense-series 使用服务端 min/max bucket 采样，将百万点压缩为按画布宽度绑定的渲染点，保留尖峰。
- 前端使用 Canvas 绘制密集序列，实时指标轮询带指数退避和 last-good fallback。
- 测试：`tests/test_perf_platform.py` 覆盖百万点采样、实时指标、API contract、AI 生成代码稳定性说明。
