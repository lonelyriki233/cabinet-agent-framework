# Token Economy Protocol - 防内耗协议

本协议解决一个问题：一个 agent 框架如果有太多层，各层可能为了“自己的上下文完整”而抢夺 token，导致总成本远超直接写代码。

## 第一原则：不产生产物就没有 token 配额

每层必须有明确的产物边界：

| 层 | 只能为这个产物消耗 token | 禁止 |
|---|---|---|
| Leader Gateway | 一段判断结果（≤30行） | 调研、拟议、长篇分析 |
| Strategy Council | 一份 draft mandate（≤80行） | 完整调研报告、技术试写 |
| Chief Coordinator | 任务包 JSON（≤50行） | 展开验收标准细节 |
| Mandate Relay | 授权判定（≤10行） | 任务细节讨论 |
| Domain Bureau worker | 按 allowed_paths 写代码/报告 | 跨领域作业 |
| Audit Office | 一份 audit note（≤40行） | 重写 worker 产出 |
| State Archive | 压缩的状态 JSON（≤10行） | 原始日志、完整 transcript |

产物不到长度或质量就不计成功；超长部分不产生额外价值。

## 第二原则：按任务类型锁定最大轮次/最大成本

```
research:        max_turns=50   fast-path: 材料明确时不召集完整 council
implementation:  max_turns=70   fast-path: 已知方案直接 dispatch
architecture:    max_turns=60   fast-path: 已有架构文档时不重新参议
maintenance:     max_turns=50   fast-path: 不触发 autoresearch
bugfix:          max_turns=40   fast-path: 不触发 audit office
evidence:       max_turns=30   fast-path: 不触发 research councillor
```

如果超过轮次仍未完成，不是自动续命，而是：

1. task 标记 `failed` 并记录 reason。
2. Chief Coordinator 判断是否值得开新 task 继续。
3. 禁止无限制 retry。

## 第三原则：参议按需启动，不逢案具呈

不是每个任务都走完整 Strategy Council。

| 条件 | 参议等级 | 激活的 councillor |
|---|---|---|
| 纯实现、方案明确 | 跳过 council | 无 |
| 涉及技术选型或取舍 | 最小 council | Research + Engineering |
| 涉及架构/系统边界 | 中等 council | + Architecture |
| 涉及权限/成本/风险 | 中等 council | + Risk |
| 交付展示相关 | 完整 council | + Evidence |

已经在 governance.py 中做了这件事：自动判断需要哪些 councillor。

但还需要确认：默认不会激活所有 councillor。

## 第四原则：worker 禁止跨领域

worker 只能在自己 Domain Bureau 的 allowed_paths 内工作。如果任务包要求改别的司，worker 必须：

1. 在 worker update 中写明“需要 XX Bureau 配合”。
2. 不自己改别人的文件。
3. 由 Chief Coordinator 创建新 task 分派给对应 Bureau。

## 第五原则：审计是抽查 + 完结审，不是每票必审

Audit Office 不是每个 task 都跑：

| 任务类型 | 审计策略 |
|---|---|
| implementation / bugfix | 仅完结审计（task done 后跑一次） |
| research | 不审计，只归档 |
| architecture | 完结审计 |
| maintenance | 抽查审计（每次 tick 有 30% 概率） |
| evidence | 全审 |

完结审计只做一次，不做周期性复查。

## 第六原则：状态归档必须压缩

State Archive 不存原始内容，只存：

- task_id
- status
- worker
- required_outputs 路径
- audit result（pass / fail / skip）
- next_task_ids（如果有）

完整产物存在于 runtime/outputs/ 中，不重复塞进状态文件。

project.json 保持在 ≤50 行。

## 第七原则：不构建平行的冗余审计

Audit Office 只存在一个实例（一个审计 agent 或模板 prompt）。如果 leader prompt 也做了检查，secretariat prompt 也做了检查，那是重复内耗。

审计职责唯一分配：

```
Audit Office: 审计 worker 产物。
Gates: 检查目录结构和任务包 schema。
Leader Gateway: 不审计，只分类。
```

## 总结

| 防内耗机制 | 对应问题 |
|---|---|
| 不产生产物就没有 token 配额 | 层间空转 |
| 按任务类型锁定 max_turns | 无限 retry |
| 参议按需启动 | 过度参议 |
| worker 禁止跨领域 | 领域争夺 |
| 审计是抽查+完结审 | 每票必审 |
| 状态归档压缩 | 状态膨胀 |
| 不构建平行审计 | 重复检查 |
