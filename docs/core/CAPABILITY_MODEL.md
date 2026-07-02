# CAF Capability Model

```text
CAF Core
  -> Runtime: task lifecycle / hooks / gates / archive / dashboard
  -> Non-parametric Memory: docs / logs / cases / graph / vector / evidence
  -> Parametric Memory: traces -> preference pairs -> eval sets -> LoRA/fine-tune registry
  -> Tool Contract: API / DB / MCP / GUI / device / VLA action boundary
  -> Supervision: authority / dry-run / risk / audit / rollback
  -> Domain Potential Templates: service ops / industrial ops / management audit
```

## 当前判断

CAF 现在是合格的 agent runtime 雏形，不是最终产业框架。

已具备：

- task packet
- conversation intake
- worker dispatch
- hooks / gates
- archive search
- dashboard supervision
- SkillForge
- host adapters

核心缺口：

- 非参数记忆没有统一对象模型和召回策略
- 参数化记忆没有从任务轨迹沉淀为训练/偏好/评测数据
- 工具/设备/VLA 没有 typed action contract
- 缺 dry-run simulator 和真实执行授权门
- 领域模板还停留在文档，不足以承载服务流/生产流/管理流

## 现在只做三件

1. `MemoryObject + RecallPolicy + EvidenceTrace`
2. `ToolContract + ActuationGate + dry-run simulator`
3. `SkillToDataset: task trace -> preference/eval/fine-tune data`
