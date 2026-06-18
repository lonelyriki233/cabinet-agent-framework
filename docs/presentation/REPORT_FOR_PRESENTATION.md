# Cabinet Agent Framework MVP 汇报稿

## 一句话定位

我做的不是一个固定业务页面，而是一个能持续驱动 AI 开发项目的最小治理型开发框架。

它把用户需求转成可执行任务，把任务交给不同领域的 worker，并用授权、审计、状态和 skill 机制保证自动化开发可控、可迭代、可维护。

## 核心架构

```text
Final Authority(User)
  -> Leader Gateway
  -> Strategy Council
  -> Chief Coordinator
  -> Mandate Relay
  -> Domain Bureaus
  -> Audit Office
  -> State Archive
```

## 各层职责

| 层 | 作用 |
|---|---|
| Final Authority | 用户授权源：目标、禁区、预算、最终否决权 |
| Leader Gateway | 理解用户需求，判断任务类型、风险、是否需要调研 |
| Strategy Council | 多视角参议：调研、架构、工程、风险、展示证据 |
| Chief Coordinator | 把拟议结果合并成可执行任务包 |
| Mandate Relay | 检查授权等级，把任务转成执行命令或升级给用户 |
| Domain Bureaus | 领域 worker：产品、数据性能、服务集成、平台运维、验证、知识技能 |
| Audit Office | 独立审计：防止越权、假完成、证据不足和上下文污染 |
| State Archive | 保存任务、结果、审计、skill 建议，进入下一轮迭代 |

## 为什么这不是普通 prompt

普通 prompt 是一次性命令。

本框架是一个循环：

```text
需求进入 -> 判断 -> 参议 -> 审权 -> 分派 -> 执行 -> 审计 -> 归档 -> 下一轮
```

所以它支持：

- 自动调研
- 自动拆解
- 领域 worker 长期负责
- 挂机式小步推进
- 自我质疑
- skill 迭代
- hooks/gates 检查
- 状态沉淀

## 借助 Hermes 的能力

本项目没有重复造完整 agent 平台，而是把 Hermes 当执行底座：

| Hermes 能力 | 用途 |
|---|---|
| AGENTS.md 自动加载 | 固化项目规则和 agent 行为边界 |
| Skills | 给不同 worker 注入可复用工作法 |
| Toolsets | 限制 worker 可用工具，降低越权风险 |
| `hermes chat -q` | 真实启动 worker 任务 |
| Cron | 可作为夜间自动 tick 的调度器 |
| Kanban | 可承接长期多 worker 任务队列 |
| MCP | 将外部系统封装为 typed tools |
| Profiles | 为长期 worker 隔离上下文和身份 |

## 当前 MVP 已实现什么

代码层：

- `cabinet_framework/leader.py`：需求分类和风险判断
- `cabinet_framework/governance.py`：参议、授权中继、领域映射
- `cabinet_framework/secretariat.py`：任务包生成和状态汇总
- `cabinet_framework/worker.py`：worker prompt、tick、Hermes 执行入口
- `cabinet_framework/hermes_bridge.py`：按 worker 生成 Hermes 命令
- `cabinet_framework/gates.py`：结构、禁区、任务包检查
- `tests/test_mvp.py`：最小测试集

协议层：

- `GOVERNANCE_RUNTIME_FRAMEWORK.md`
- `MANDATE_FLOW.md`
- `AUTO_RESEARCH_PROTOCOL.md`
- `AUDIT_OFFICE_PROTOCOL.md`
- `HERMES_INTEGRATION.md`

## 授权后能否自动工作

可以，但必须按授权等级。

| 等级 | 能力 |
|---|---|
| L0 | 只建议，不执行 |
| L1 | 生成任务包和 worker prompt |
| L2 | 可运行低风险 worker、本地写文件、跑检查 |
| L3 | 可夜间连续 tick，但每轮必须过 gate |
| L4 | 可准备 PR/release 材料，但不能公开发布 |

当用户授予 L2/L3 后，Mandate Relay 可以自动批准低风险任务并推进开发。

但以下必须升级给用户：

- 密钥、账号、token
- 生产部署
- 大规模删除或重写
- 公开发布
- 主分支合并
- 不可控费用
- 改变项目方向

## 面试展示重点

不要说“我做了一个 dashboard”。

应该说：

> 我做了一个 AI Coding Harness。它解决的是如何让 AI 在复杂项目中持续、自动、可控地调研、开发、检查和维护。

展示顺序：

1. 展示架构图。
2. 输入一个复杂开发需求。
3. 展示 Leader Gateway 判断。
4. 展示 Strategy Council 拟议。
5. 展示 Mandate Relay 审权。
6. 展示 Chief Coordinator 生成任务包。
7. 展示 worker prompt / Hermes worker 命令。
8. 展示 gate 和测试。
9. 说明如果授权 L3，可以接 Hermes cron 进行夜间小步推进。
