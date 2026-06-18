# Cabinet Agent Framework

Portable cabinet-style multi-agent runtime for Hermes, Codex, Claude Code, OpenClaw/OpenCode and generic CLI agents.

## Quick Start

```bash
git clone <your-repo-url>
cd cabinet_agent_framework
python3 -m cabinet_framework.cli init
python3 -m unittest discover -s tests -v
python3 -m cabinet_framework.cli gate
python3 -m cabinet_framework.cli chat-intake --authority L2 --request "建设跨 Hermes/Codex/Claude Code/OpenClaw 的 agent 框架，包含记忆、skills、上下文、hooks、MCP、headless、SDK、dashboard、子工程模板"
python3 -m cabinet_framework.cli dashboard --host 127.0.0.1 --port 8788
```

30-second demo:

```bash
python3 examples/demo_30s.py
```

## What This Is

Cabinet Agent Framework 是一个项目级 agent operating system。它把数据平台 MVP、小说/OC/IP MVP 这类项目视为 managed subprojects，而不是框架本体。

主流程：

```text
User / Host Agent
  -> Conversation Bridge
  -> Leader Gateway
  -> Strategy Council
  -> Chief Coordinator
  -> Mandate Relay
  -> Cabinet + Six Ministries
  -> Domain Workers
  -> Hooks / Gates
  -> Archive / Memory / RAG
  -> Dashboard Supervision
```

## Core Requirements Covered

| Requirement | Current implementation |
|---|---|
| 兼容性 | 文件/JSON/Markdown/CLI 为核心协议；Hermes/Codex/Claude Code/OpenClaw 放在 adapters 文档与宿主适配层 |
| 扩展性 | worker、bureau、content section、subproject templates 均可追加 |
| 移植性 | 项目根目录包含 AGENTS.md、README、docs、skills、memory、runtime；复制到项目即可读 |
| 后续可拓展 | 不把部门、任务域、模型、工具写死为唯一答案；保留 SDK/MCP/hook/template 扩展点 |
| 记忆系统 | `memory/` 下内阁 + 吏户礼兵刑工分层 |
| Skills | `skills/thinking/` 与 `skills/worker/` 分离；已迁移核心参考并标注来源 |
| 上下文单元 | `context_units/` 目录和 docs/core/CONTEXT_UNITS.md |
| Hooks | `cabinet_framework/hooks.py` + runtime hook logs + docs/ops/HOOKS_LIFECYCLE.md |
| MCP/RAG | `mcp/` + integrations/MCP_RAG.md，V1 保留 typed tool / vector index 接口 |
| Headless | `dispatcher.py`、tick/dispatch、ops/HEADLESS.md |
| Agent SDK | `sdk/AGENT_SDK.md`，Python modules expose task/worker/runtime primitives |
| Dashboard | Vue3 dashboard，监督而非会话入口 |

## Where Hermes Is Used

Hermes-native path:

- `cabinet_framework/hermes_bridge.py`
- Hermes skills/cron/gateway/delegation/MCP/toolsets 的概念参考

Portable abstraction:

- TaskPacket JSON
- memory/skills/context_units/hooks/mcp/adapters/templates directories
- CLI commands via `cabinet_framework.cli`

Attribution rule: any Hermes-native mechanism must be described as Hermes-based or Hermes-inspired, not claimed as original framework invention.

## Does / Does Not

| Does | Does Not Yet |
|---|---|
| Create task packets from chat-intake | Fully run every host agent adapter automatically |
| Persist lifecycle hooks | Ship production vector DB by default |
| Separate thinking and worker skills | Guarantee small models perform well without evaluation |
| Provide cabinet-six-ministries memory layout | Replace Hermes/Codex/Claude Code native capabilities |
| Show dashboard supervision | Use dashboard as a chat interface |
| Define subproject templates | Finish all domain-specific templates in V1 |

## Key Directories

```text
cabinet_framework/     Python runtime
memory/                Cabinet + six ministries memory
skills/thinking/       high-level AI thinking skills
skills/worker/         executable worker skills
context_units/         multi-agent context packets
hooks/                 project hook policies/extensions
mcp/                   MCP/RAG interface notes
headless/              autonomous/headless operations notes
adapters/              host adapters: Hermes/Codex/Claude/OpenClaw
templates/             subproject templates
projects/              managed subprojects references
runtime/               generated tasks/logs/hooks/archive
web/templates/         Vue3 dashboard
```

## GitHub / Release Files

| File | Purpose |
|---|---|
| `.github/workflows/ci.yml` | Runs tests, keyword index, public audit and gate on GitHub Actions |
| `examples/demo_30s.py` | Clean local smoke demo |
| `scripts/public_audit.py` | Checks public-safe files for local absolute paths and secret-like strings |
| `scripts/package_release.py` | Runs verification and creates a clean ZIP under `dist/` |
| `CONTRIBUTING.md` | Contribution and design rules |
| `SECURITY.md` | Secret-handling and security reporting policy |
| `docs/presentation/GITHUB_READY_CHECKLIST.md` | Manual release checklist |

## Tech Stack

| Layer | Technology |
|---|---|
| Runtime | Python 3.10+ standard library |
| Dashboard | Flask if installed + Vue3 CDN template; CLI/runtime remain pure Python |
| Data format | JSON task packets, Markdown skills/memory/docs, JSONL hook/RAG records |
| CI | GitHub Actions / unittest |
| Host adapters | Thin CLI adapter layer, no hard-coded model provider |

