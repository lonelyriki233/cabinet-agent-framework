# AI Agent 开发框架 MVP 中文介绍与验证手册

## 1. 一句话介绍

这个 MVP 是一个可运行的 AI Agent 开发框架。它把 AI coding 从随意的 vibe coding，组织成“对话进入、需求判断、策略参议、任务拆解、授权执行、领域 worker、独立审计、状态归档、实时监控”的工程化流程。

## 2. 演示前准备

```bash
cd <repo-root>
python3 scripts/reset_runtime.py
python3 -m cabinet_framework.cli init
python3 -m unittest discover -s tests -v
python3 -m cabinet_framework.cli gate
```

预期：测试 OK，gate PASS。

## 3. 启动实时监控

```bash
python3 -m cabinet_framework.cli dashboard --host 127.0.0.1 --port 8787
```

浏览器打开：

```text
http://127.0.0.1:8787/
```

页面现在重点展示：

- 层级职责：每一层做什么、产物是什么。
- Agent 名单：有哪些 worker、属于哪个 bureau、当前任务数。
- 任务与报告：每个任务由谁做，报告、prompt、log、audit、archive 在哪里。
- 状态档案：按 bureau/task_type/task_id 分层归档和检索。
- 文档索引：项目文档已收束到 docs/。

## 4. 功能验证清单

### 4.1 对话任务进入 runtime

```bash
python3 -m cabinet_framework.cli chat-intake --authority L2 --request "设计一个大数据图表渲染方案，需要调研技术选型、性能取舍和维护策略"
python3 -m cabinet_framework.cli tasks
```

验证点：dashboard 的“任务与报告”出现新任务。

### 4.2 Leader Gateway 需求判断

```bash
python3 -m cabinet_framework.cli intake --authority L2 --request "修复图表渲染 bug"
```

验证点：输出中有任务类型、主 worker、autoresearch、风险等级。

### 4.3 Strategy Council 按需参议，避免内耗

```bash
python3 -m cabinet_framework.cli intake --authority L2 --request "设计 agent harness 框架，需要调研、自动化开发和权限边界"
```

验证点：输出 active_councillors 和 principal_contradiction。简单任务不会全量激活所有参议位。

### 4.4 Mandate Relay 授权中继

```bash
python3 -m cabinet_framework.cli intake --authority L2 --request "删除 auth token 并生产部署"
```

验证点：高风险任务会被阻断或要求用户授权。

### 4.5 Chief Coordinator 任务拆解

```bash
python3 -m cabinet_framework.cli tasks
python3 - <<'PY'
from cabinet_framework.model import TASKS
p = sorted(TASKS.glob('*.json'))[0]
print(p)
print(p.read_text(encoding='utf-8'))
PY
```

验证点：任务包包含 worker、objective、allowed_paths、forbidden_paths、acceptance_criteria、required_outputs、gates。

### 4.6 Worker prompt 精确生成

```bash
python3 -m cabinet_framework.cli prompt --task runtime/tasks/<TASK_ID>.json
```

验证点：prompt 包含允许路径、禁止路径、验收标准、必须输出、自我质疑、skill_update_suggestion。

### 4.7 持续调度

```bash
python3 -m cabinet_framework.cli dispatch --mode prompt --max-steps 50
```

如果现场允许真实 Hermes 执行：

```bash
python3 -m cabinet_framework.cli dispatch --mode hermes --max-steps 50
```

验证点：ready 队列被持续推进，不是只执行一个任务就停止。

### 4.8 Hermes 真实执行入口

```bash
python3 -m cabinet_framework.cli command --task runtime/tasks/<TASK_ID>.json
```

验证点：能看到 `hermes chat --quiet --max-turns ... -t ... -s ... -q ...`，说明框架把真实执行交给 Hermes worker。

### 4.9 Gate / Audit

```bash
python3 -m cabinet_framework.cli gate
```

验证点：structure_gate、forbidden_path_gate、task_packet_schema_gate PASS。

### 4.10 分层状态档案

```bash
python3 -m cabinet_framework.cli archive-tree
python3 -m cabinet_framework.cli archive-search --query "性能 图表 降采样" --top-k 5
```

验证点：档案按 `runtime/archive/<bureau>/<task_type>/<task_id>/` 分层，不是扁平 RAG。

## 5. 和 vibe coding 的区别

vibe coding 是“用户说一句，AI 写一段”。本 MVP 的区别是：

- 任务先进 runtime。
- 需求先分类和审权。
- worker 有边界和验收标准。
- 每个任务有报告路径。
- 有 gate 和 audit。
- 有分层 archive。
- 有 dashboard 实时监督。
- 可以持续 dispatch。

## 6. 收尾话术

这个 MVP 的重点不是做一个业务页面，而是证明 AI coding 可以被工程化治理。用户任务进入 runtime 后，会经过需求判断、策略参议、任务拆解、授权执行、领域 worker、独立审计和状态归档，最后在 dashboard 中实时监督。这样 AI 不再只是一次性聊天写代码，而是可持续、可审计、可维护的 agent framework。
