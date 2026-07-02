# Orchestrator / Supervisor

CAF 的主 agent 应承担项目监督者角色：

1. 把需求转成 Project。
2. 把 Project 拆成 HarnessTask。
3. 分配 worker。
4. 追踪 Artifact Registry。
5. 触发 Gate System。
6. Gate FAIL 时返工。
7. Gate PASS 后归档。
8. 更新 roadmap、risk、decision。

v1.0 的监督入口先通过 CLI 和 runtime/project_harness 落地，后续接入 dashboard 与自动调度。
