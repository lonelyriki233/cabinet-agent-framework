# Governance Runtime Framework

本框架只使用工程化命名。

## 正式角色

| 名称 | Agent 框架职责 |
|---|---|
| Final Authority / 用户授权源 | 设定目标、边界、预算、最终否决权 |
| Leader Gateway / 领袖入口 | 理解需求，判断任务类型、风险、是否需要调研 |
| Strategy Council / 策略参议组 | 多视角理解任务、调研、拟议、工程取舍 |
| Chief Coordinator / 首席协调官 | 汇总参议意见，形成可执行任务路线 |
| Mandate Relay / 授权中继层 | 把拟议转成执行命令；在授权范围内自动批准 |
| Domain Bureaus / 领域执行司 | 按项目内容长期负责开发、维护、bugfix |
| Audit Office / 独立监察司 | 审计越权、虚假完成、风险、质量与上下文污染 |
| State Archive / 状态档案 | 保存任务、结果、审计、skill 建议和下一步 |

## 总流程

```text
Final Authority(User)
  ↓ 授权目标、边界、预算
Leader Gateway
  ↓ 识别任务类型、风险、是否需要参议
Strategy Council
  ↓ 多视角拟议：调研、架构、风险、工程取舍
Chief Coordinator
  ↓ 合并为 draft mandate
Mandate Relay
  ↓ 例行任务自动批准；高风险升级用户
Domain Bureaus
  ↓ 开发、维护、调研、测试、报告
Audit Office
  ↑ 反向审计、质疑、阻断、要求返工
State Archive
  ↺ 记录任务、成果、审计、skill 更新，进入下一轮
```

## Domain Bureaus

| 执行司 | 对应项目内容 | 长期责任 |
|---|---|---|
| Product & UX Bureau | 产品需求、页面、交互、展示路径 | 用户体验、界面、面试可见性 |
| Data & Performance Bureau | 数据处理、降采样、benchmark、性能预算 | 大数据和图表密集核心问题 |
| Service & Integration Bureau | API、后端、缓存、fallback、外部系统 | 服务稳定性和接口治理 |
| Platform & Ops Bureau | CI、cron、profile、权限、部署边界 | 挂机开发和运维安全 |
| Verification Bureau | 测试、gates、回归、质量报告 | 验收和停止条件 |
| Knowledge & Skills Bureau | 文档、skills、调研归档、上下文记忆 | 长期维护和自我迭代 |

## Strategy Council

策略参议组是一组可并行/可轮换的思考位：

| Councillor | 关注点 |
|---|---|
| Research Councillor | 外部调研、方案比较、未知问题 |
| Architecture Councillor | 系统边界、模块关系、长期演化 |
| Engineering Councillor | 实现代价、测试、可维护性 |
| Risk Councillor | 权限、成本、越权、失败模式 |
| Interview Councillor | 面试质疑、展示证据是否充分 |

他们产出 draft mandate，不直接改代码。

## Mandate Relay：代理执行权

用户可以授予 Mandate Relay 代理执行权。

### 可自动批准

- 已存在任务队列中的下一步。
- 低风险代码改动。
- 调研任务。
- 文档/报告整理。
- 运行测试、lint、benchmark。
- skill 草案生成。
- 夜间小步推进。

### 必须升级给用户

- secrets/auth/token。
- 生产部署。
- 大规模删除/重写。
- 费用不可控的长任务。
- 主分支合并/公开发布。
- 改变项目方向。
- worker 之间出现关键冲突。

## 持续运转机制

```text
ready proposal
  -> council draft
  -> mandate check
  -> execution order
  -> bureau work
  -> worker update
  -> audit pass/fail
  -> archive update
  -> next ready proposal
```

每一轮必须有：

- 当前任务 ID。
- 授权来源。
- 执行司。
- 产物路径。
- 审计结果。
- 下一步。
- stop condition。
