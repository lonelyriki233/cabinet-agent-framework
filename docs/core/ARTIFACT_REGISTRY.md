# Artifact Registry

Artifact Registry 是 CAF v1.0 的产物登记层。

## 为什么需要

复杂项目不能靠对话总结推进，必须靠可追踪产物推进。

每个重要产物都要登记：

- path
- owner_task
- type
- status
- sha256
- validation_result
- related_decisions

## Artifact 类型

- code
- docs
- tests
- design
- logs
- config
- decision
- review
- rollback
- other

## 状态

- draft
- ready
- validated
- rejected
- archived

## Gate 关系

Gate 不直接相信 worker 声明，必须检查 Artifact Registry。

例如 delivery gate 至少要求：

1. 当前 task 存在 artifact。
2. 必需 artifact type 齐全。
3. validation_result.status 为 pass/ok。
4. artifact status 为 validated。
