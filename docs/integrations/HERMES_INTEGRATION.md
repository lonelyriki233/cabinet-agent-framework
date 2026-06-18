# Hermes Integration - 本框架借助的 Hermes 能力

本项目不自造完整 agent 平台，而是把框架层放在项目内，把执行能力交给 Hermes。

## 已接入/预留的 Hermes 能力

| Hermes 能力 | 本框架使用方式 | 作用 |
|---|---|---|
| `AGENTS.md` 自动加载 | 新 Hermes 在本目录启动时读取项目规则 | 保证进入正确角色和边界 |
| `hermes chat -q` | `tick --mode hermes` 调用真实 worker | 把任务包交给真实 agent 执行 |
| `--toolsets` | 按 worker 类型限制工具集 | 降低越权和上下文污染 |
| `--skills` | 按 worker 类型预加载相关 skill | 给 worker 注入专门工作法 |
| `--max-turns` | 每个 worker 设置轮数上限 | 控制成本和失控风险 |
| Hermes skills | 复用 `agent-harness-engineering`、调试/测试/外部审查等技能 | 不重复造轮子 |
| Hermes cron | L3 夜间自治时可定时运行 `tick` | 支持挂机开发 |
| Hermes kanban | 大任务可接入多 worker 看板 | 支持长期任务队列 |
| Hermes MCP | 外部系统用 typed tools 接入 | 避免随意 bash/API 调用 |
| Hermes profiles | 可为长期 worker 创建独立 profile | 隔离身份、记忆和配置 |

## 当前实现状态

已经实现：

- request intake
- Strategy Council 拟议
- Mandate Relay 审权
- task packet 生成
- worker prompt 生成
- worker Hermes 命令生成
- `tick --mode prompt`
- `tick --mode hermes` 真实调用入口
- gates + tests

未在本次自动启动：

- cron 夜间任务
- kanban 看板
- profile 创建
- MCP server 注册

这些不应该由框架自动替用户创建；需要用户明确授权后再接入。

## 真实 worker 命令形态

框架会生成类似命令：

```bash
hermes chat --quiet --max-turns 50 -t web,file,terminal -s agent-harness-engineering -q '<worker prompt>'
```

这不是模拟执行。启动后由 Hermes 本身加载项目 AGENTS.md、skills、tools，并按任务包工作。
