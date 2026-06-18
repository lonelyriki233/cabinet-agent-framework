# MCP_POLICY.md - MCP 怎么用

MCP 的价值是把自由操作变成稳定 typed tools。

## 应该 MCP 化的东西

- 查询项目状态
- 创建/更新任务
- 查询 benchmark
- 查询日志摘要
- 写入标准报告
- 查询 issue/PR/CI 状态
- 访问外部数据源

## 不该 MCP 化的东西

- 一次性临时脚本
- 尚未稳定的探索动作
- 高风险权限动作

## 谁设计 MCP

harness_worker 提出 schema，中书确认使用场景，领袖批准接入边界。

## 交付说明

MCP 不是“我会接工具”，而是“我把 agent 的自由行为收敛成可审计、可复用、可限制的工具调用”。
