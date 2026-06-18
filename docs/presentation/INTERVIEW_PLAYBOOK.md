# INTERVIEW_PLAYBOOK.md - 面试打法

## 30 秒开场

我把题目理解为：不是现在做完一个高性能数据分析平台，而是设计一套 AI Coding Harness，让 AI 能在这个复杂项目里长期、自动、可控地工作。

所以我的框架是：领袖负责理解用户和总状态，中书负责拆解和调度，worker 按项目内容长期负责具体模块，skills/hooks/MCP/checks 负责约束和沉淀。

## 面试官问：你的 AI 如何拆任务？

答：看 `TASK_MODEL.md`。领袖先判断任务类型，中书再把目标变成带背景、输入、输出、验收标准、边界的任务包。

## 面试官问：多个 agent 怎么协作？

答：看 `ROLE_SECRETARIAT.md` 和 `REPORT_PROTOCOL.md`。worker 不互相私聊，所有依赖和状态经中书汇总。

## 面试官问：worker 质量谁保证？

答：看 `CHECK_PROTOCOL.md`。worker 自检，中书检查任务目标和状态，领袖检查是否满足用户需求。hooks 做硬性边界检查。

## 面试官问：skills 谁来做？

答：看 `SKILL_POLICY.md`。worker 提出，中书收集，harness_worker 整理，领袖批准。

## 面试官问：MCP 有什么用？

答：看 `MCP_POLICY.md`。MCP 把自由操作变成 typed tools，降低 worker 乱用 bash、乱查数据、乱写状态的风险。

## 面试官问：夜间自动化怎么防失控？

答：看 `NIGHT_WORKFLOW.md`。只推进已授权任务，失败即停，早晨由中书汇总，不碰 secrets/部署/删除/账单。
