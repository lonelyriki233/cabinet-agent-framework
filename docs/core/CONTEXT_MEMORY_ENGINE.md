# Context / Memory Engine

CAF v1.0 的 Context / Memory Engine 已接入 worker runtime。

实现位置：

```text
cabinet_framework/context_engine.py
```

## 目标

解决复杂项目里的上下文问题：

- 当前任务需要读什么
- 当前任务禁止读什么
- 当前任务关联哪些 artifact
- 当前项目有哪些 decision
- 当前任务有哪些 gate history
- 当前任务有哪些 blocker / rework history
- 当前任务能召回哪些 memory object
- worker 如何获得可审计 context，而不是靠一次性聊天窗口

## Context Pack

每个 HarnessTask 可以生成一个 context pack：

```text
runtime/project_harness/context_packs/<task_id>.json
```

包含：

```text
project
task
allowed_context
project_decisions
related_artifacts
gate_history
blocker_history
recalled_memory
context_rules
```

## Worker 接入

`worker_runtime.py` 生成 worker prompt 时会自动调用：

```python
build_context_pack(task_id)
```

worker prompt 现在包含：

- context_pack_path
- project_decisions
- allowed_context
- related_artifacts
- gate_history
- blocker_history
- recalled_memory
- context_rules

## Memory Object

CAF 使用 `MemoryObject` 表示可召回记忆：

```text
id
kind
title
content
tags
evidence
freshness
conflicts_with
created_at
```

每条记忆应尽量带 EvidenceTrace，避免无来源记忆污染项目。

## CLI

生成任务 context summary：

```bash
python3 -m cabinet_framework.cli harness-context --task-id <TASK>
```

查看项目上下文索引：

```bash
python3 -m cabinet_framework.cli harness-context --project-id <PROJECT>
```

登记任务记忆：

```bash
python3 -m cabinet_framework.cli harness-memory \
  --task-id <TASK> \
  --title "经验标题" \
  --content "经验内容" \
  --tag worker --tag context
```

## 边界

当前 v1.0 是轻量检索，不是向量数据库。

后续可以升级为：

- embedding / vector recall
- conflict detection
- memory freshness decay
- project-local memory namespace
- gate failure 自动沉淀为 case memory
