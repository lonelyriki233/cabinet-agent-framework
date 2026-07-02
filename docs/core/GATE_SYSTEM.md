# Gate System

Gate System 是 CAF v1.0 的硬验收层。

## 原则

Hook 可以记录事件；Gate 必须能阻止不合格任务进入下一阶段。

## 阶段

- intake
- design
- implementation
- test
- review
- delivery
- archive

## 当前 v1.0 最小 Gate

当前实现位于：

```text
cabinet_framework/project_harness.py
```

入口：

```python
run_stage_gate(task_id)
```

检查：

1. task objective 是否存在。
2. acceptance_criteria 是否存在。
3. required_artifact_types 是否齐全。
4. implementation/test/review/delivery/archive 阶段是否登记 artifact。
5. test/review/delivery/archive 阶段 artifact validation 是否通过。
6. delivery 阶段 artifact status 是否为 validated。

## CLI

```bash
python3 -m cabinet_framework.cli harness-gate --task-id <task_id>
```

返回码：

- PASS：0
- FAIL：1
