# Lifecycle Gate

CAF v1.0 的 Lifecycle Gate 把 Gate System 接入 HarnessTask 生命周期。

实现位置：

```text
cabinet_framework/lifecycle_gate.py
```

## 目标

以前：

```text
run_stage_gate(task_id)
```

只是独立检查。

现在：

```text
advance_task_stage(task_id)
```

必须先运行当前阶段 gate，只有 gate pass 才允许推进 stage。

## 生命周期推进

标准流程：

```text
HarnessTask 当前 stage
→ run_stage_gate(task_id)
→ pass: 更新 task.stage / task.status
→ fail: 阻止推进，记录 blocker，生成 rework task
```

## Stage 顺序

```text
intake
→ design
→ implementation
→ test
→ review
→ delivery
→ archive
```

## Gate Fail 行为

当 gate fail：

1. task 不推进 stage。
2. task.status 变为 `blocked`。
3. 写入 blocker registry。
4. emit hook：`harness.lifecycle.blocked`。
5. 默认生成 rework task。
6. 写入 transition 记录：`status=blocked`。

Blocker 文件：

```text
runtime/project_harness/blockers.jsonl
```

Transition 文件：

```text
runtime/project_harness/stage_transitions.jsonl
```

## Rework Task

返工任务会继承：

- project_id
- worker
- stage
- allowed_paths
- required_artifact_types
- acceptance_criteria

并记录：

```text
source = lifecycle_gate_rework
source_task_id = 原 task_id
dependencies = [原 task_id]
```

## CLI

推进生命周期：

```bash
python3 -m cabinet_framework.cli harness-advance --task-id <TASK_ID>
```

指定目标阶段：

```bash
python3 -m cabinet_framework.cli harness-advance --task-id <TASK_ID> --target-stage test
```

只阻塞不创建返工任务：

```bash
python3 -m cabinet_framework.cli harness-advance --task-id <TASK_ID> --no-rework
```

查看生命周期：

```bash
python3 -m cabinet_framework.cli harness-lifecycle --task-id <TASK_ID>
```

查看 blockers：

```bash
python3 -m cabinet_framework.cli harness-blockers
python3 -m cabinet_framework.cli harness-blockers --task-id <TASK_ID>
python3 -m cabinet_framework.cli harness-blockers --status open
```

## 当前边界

当前实现是 v1.0 功能闭环：

- 已有硬推进 gate
- 已有 blocker registry
- 已有 rework task generation
- 已有 hook event
- 已有 rework pass 自动关闭原 blocker
- 已有 blocker 状态流转：`open -> rework_created -> resolved`
- 已有 gate failure / blocker resolution 自动沉淀为 memory case

## Blocker / Rework 闭环

当原任务 gate fail：

```text
original task
→ gate fail
→ blocker.status = rework_created
→ rework task created
```

当返工任务 gate pass：

```text
rework task
→ gate pass
→ auto_resolve_rework_blockers()
→ blocker.status = resolved
→ original task.status = ready
→ memory case written
```

查看有效 blocker 状态：

```bash
python3 -m cabinet_framework.cli harness-blockers --task-id <TASK_ID>
```

人工关闭 blocker：

```bash
python3 -m cabinet_framework.cli harness-resolve-blocker \
  --blocker-id <BLOCKER_ID> \
  --resolved-by-task-id <TASK_ID> \
  --resolution "人工确认已解决"
```

## 记忆沉淀

Lifecycle Gate 会自动记录两类 memory case：

```text
Gate failure: <task title>
Resolved blocker: <blocker id>
```

这些会进入：

```text
runtime/memory_objects.jsonl
```

后续 Context / Memory Engine 会在相关任务里召回这些失败与修复经验。

## 后续还要补

- archive/learning 更系统地整理 gate failure case
- worker lane 自动执行 rework task
- blocker SLA / 优先级 / owner
- project-level risk summary
