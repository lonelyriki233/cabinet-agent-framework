# SIMULATION_AUDIT.md - 按现有 MD 推演框架是否会按要求运行

## 推演结论

当前框架主干能按用户要求走：领袖不会直接做业务项目，中书负责拆解与汇总，worker 按内容领域负责，skills/hooks/MCP/check 有职责分配。

但原版存在 4 个缺口：

1. autoresearch 没有独立启动条件。
2. agent 挂机开发只有夜间原则，缺少任务状态循环。
3. 自我迭代只有 skill 建议，没有明确复盘/升级闭环。
4. 自我检查质疑只有 check protocol，缺少反驳者/质疑清单。

本文件已把缺口转为新增协议：

- `AUTO_RESEARCH_PROTOCOL.md`
- `AUTONOMOUS_DEV_PROTOCOL.md`
- `SELF_ITERATION_PROTOCOL.md`
- `SELF_CRITIQUE_PROTOCOL.md`

## 模拟 1：用户提出新开发需求

用户说：给高性能数据分析平台设计图表大数据渲染方案。

预期流程：

1. 领袖读取 `TASK_MODEL.md`，判断为“技术调研 + 框架设计”。
2. 领袖不直接写最终方案，而是交给中书。
3. 中书生成任务拆解：
   - research_worker：调研图表方案。
   - data_perf_worker：提出数据降采样/聚合预算。
   - frontend_worker：判断渲染侧接入代价。
   - harness_worker：给出需要的 hooks/checks。
4. worker 各自只处理本领域。
5. worker 提交简洁更新日志。
6. 中书整合依赖：数据策略影响前端渲染；benchmark 结果影响方案选择。
7. 领袖向用户汇报方向、证据、风险、下一步。

判断：能走通。

## 模拟 2：autoresearch 是否会启动

原版问题：`TASK_MODEL.md` 只写“技术调研 -> research_worker”，但没有说明何时自动触发调研。

修正后规则：见 `AUTO_RESEARCH_PROTOCOL.md`。

触发条件包括：

- 任务涉及未知技术选型。
- worker 对方案信心不足。
- 需要比较框架、库、架构模式。
- 出现性能/稳定性/成本取舍。
- 面试题要求体现“技术调研”。

判断：修正后可正常启动。

## 模拟 3：agent 挂机开发是否支持

原版问题：`NIGHT_WORKFLOW.md` 有边界，但缺少“挂机时如何循环推进、何时停止、如何汇总”。

修正后规则：见 `AUTONOMOUS_DEV_PROTOCOL.md`。

挂机不是无限工作，而是：

1. 中书读取已授权任务队列。
2. 每轮只推进一个任务或一个 worker 阶段。
3. worker 写本地结果和 update。
4. 中书更新状态。
5. hooks/checks 失败则停。
6. 达到 stop condition 则停。
7. 早晨给领袖摘要。

判断：修正后支持“可控挂机开发”，不支持失控无限开发。

## 模拟 4：自我迭代是否支持

原版问题：`SKILL_POLICY.md` 说 worker 可提出 skill 建议，但缺少闭环。

修正后规则：见 `SELF_ITERATION_PROTOCOL.md`。

闭环：

worker 发现重复问题 -> 提出 skill_update_request -> 中书归并 -> harness_worker 写 skill 草案 -> 领袖批准 -> 下次任务加载 skill -> 检查是否减少错误。

判断：修正后支持。

## 模拟 5：自我检查质疑是否支持

原版问题：`CHECK_PROTOCOL.md` 有检查项，但没有“质疑者视角”。

修正后规则：见 `SELF_CRITIQUE_PROTOCOL.md`。

关键机制：

- worker 完成后必须回答“我可能哪里错了”。
- 中书必须检查“是否存在跨 worker 冲突”。
- 领袖必须检查“是否满足用户真实意图，而不是表面完成”。
- 高风险任务可启用 critique pass。

判断：修正后支持。

## 临界情况推演

| 临界情况 | 应该怎么走 | 当前判断 |
|---|---|---|
| 用户需求很模糊 | 领袖先压缩目标；必要时问一句关键澄清；中书记录 | 可走通 |
| 任务跨前端/后端/数据 | 中书拆多个 worker；禁止 worker 私聊；中书整合依赖 | 可走通 |
| worker 结果互相冲突 | 中书识别冲突，发协调任务或交领袖决策 | 需依赖中书执行质量 |
| worker 不知道技术选型 | 自动触发 research_worker | 已补协议 |
| 夜间任务失败 | stop gate 停止，早晨汇报 blocker | 已补协议 |
| worker 反复犯同一错误 | 走 skill_update_request -> skill 迭代 | 已补协议 |
| 低价 worker 输出很浅 | 中书要求补充验收证据；必要时 critique pass | 已补协议 |
| 用户要求立刻看结果 | 领袖汇报框架状态和下一步，不拿假 demo 冒充 | 可走通 |

## 总判断

框架现在更接近用户要求：它不是业务项目，也不是脚本 demo，而是一套 agent 工作制度。

仍需注意：这套框架是“协议级框架”。真正接入 Hermes profiles、cron、kanban、MCP server 时，还需要用户单独授权实现具体运行层。
