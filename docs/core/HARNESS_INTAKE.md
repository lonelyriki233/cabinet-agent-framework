# Harness Intake

Harness Intake 把普通用户需求接入 CAF v1.0 Project Harness。

实现位置：

```text
cabinet_framework/harness_intake.py
```

## 作用

以前：

```text
chat/intake → legacy TaskPacket
```

现在：

```text
chat/intake
→ LeaderDecision / Mandate
→ HarnessProject
→ HarnessTask(s)
→ Worker Runtime
→ Artifact Registry
→ Gate System
```

legacy TaskPacket 仍保留，用于兼容旧 dashboard/runtime。

## CLI

```bash
python3 -m cabinet_framework.cli harness-intake \
  --request "完善 CAF worker runtime 和 gate 闭环" \
  --authority L2
```

输出：

- project_id
- legacy_task_ids
- harness_task_ids
- decision
- mandate

## chat-intake

`chat-intake` 已自动返回：

```json
{
  "created_tasks": [],
  "harness": {
    "project": {},
    "tasks": []
  }
}
```

这意味着普通 Hermes 对话需求可以直接进入 v1.0 harness。
