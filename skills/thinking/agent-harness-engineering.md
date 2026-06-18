<!-- Migrated reference. Source: local-hermes-skills/devops/agent-harness-engineering/SKILL.md. Review and depersonalize before public release if needed. -->

---
name: agent-harness-engineering
description: >-
  Use when designing, auditing, or implementing an AI agent harness: project memory files, skill packs, subagents, hooks, MCP/tool boundaries, headless/CI execution, structured outputs, cost controls, and operational governance. Derived from the local Claude Code harness source corpus and adapted for Hermes/Codex workflows.
version: 1.0.0
author: Hermes Agent
license: MIT
metadata:
  hermes:
    tags: [agent-harness, skills, subagents, hooks, mcp, ci, governance, claude-code, codex, hermes]
    related_skills: [hermes-agent, codex, claude-code, hermes-agent-skill-authoring, native-mcp, github-pr-workflow, requesting-code-review, subagent-driven-development, webhook-subscriptions]
---

# Agent Harness Engineering

## Overview

Use this skill when the task is not merely “run an agent”, but to build the surrounding harness that makes agents reliable: memory files, skills, subagents, hooks/gates, MCP tools, CI/headless runs, structured output contracts, cost limits, audit logs, and governance rules.

This skill was inherited from the local source corpus:

`private-source-corpus/claude-code-harness-practice`

Treat that directory as the raw reference library. This Hermes skill is the operational compression of that corpus, adapted to our deployed Hermes/Codex environment.

## When to Use

- Designing a new agent workflow, worker lane, or project-level agent runtime.
- Turning Claude Code/Codex/Hermes usage patterns into reusable skills or project protocols.
- Adding safety gates around tool use, shell commands, file access, secrets, tests, or cost.
- Building headless/CI agent jobs that must emit structured results and be auditable.
- Deciding whether a capability belongs in memory, skill docs, subagents, hooks, MCP tools, or CI automation.
- Reviewing an agent setup for over-broad permissions, poor context hygiene, weak output contracts, or lack of observability.

Do not use for ordinary one-shot coding unless the request includes harness design, skills, subagents, hooks, MCP, CI, or governance.

## Core Architecture: Seven Layers

1. Memory layer
   - Persist stable project conventions in `AGENTS.md`, `CLAUDE.md`, `USER.md`, `MEMORY.md`, or project docs.
   - Keep rules searchable and overrideable. Avoid turning memory files into raw task dumps.
   - Put current task progress in session/todo/kanban, not long-term memory.

2. Skill layer
   - A mature skill is not just a prompt. It should have a trigger description, allowed workflow, references, commands/scripts, output contract, pitfalls, and verification.
   - Description is the router: write it from the user/task trigger perspective, not as an implementation detail.
   - Use progressive disclosure: main `SKILL.md` holds the playbook; large examples live in `references/`; deterministic helpers live in `scripts/`.

3. Subagent layer
   - Use subagents as module boundaries: reviewer, tester, bug locator, bug fixer, security scanner, data collector.
   - Give each subagent a narrow job, explicit inputs, expected output schema, and tool constraints.
   - Prefer main-agent orchestration + focused workers over one giant context that does everything.

4. Hook / gate layer
   - PreToolUse-style gates: block dangerous commands, protect secrets, prevent writes outside scope.
   - PostToolUse-style gates: audit logs, format after edits, lint feedback, collect metrics.
   - Stop gates: run tests or quality checks before an autonomous run claims completion.
   - Subagent start/stop gates: inject required context and verify worker output quality.

5. MCP / external tool layer
   - Wrap databases, APIs, services, and filesystem-sensitive operations as typed tools instead of allowing free-form Bash.
   - Prefer least privilege and typed schemas. Make invalid operations impossible or explicit.
   - For Hermes, use the `native-mcp` skill and `hermes mcp add/test/configure` commands.

6. Headless / CI / SDK layer
   - In CI, constrain tools, turns, budget, model, output format, and target paths.
   - Emit JSON/structured output when downstream steps need to parse results.
   - Keep session continuation deliberate: use resume/session IDs only when state continuity is required.

7. Operations / governance layer
   - Observe: debug logs, stream JSON, audit logs, token/cost tracking, status reports.
   - Control: permission allowlists, ignore files, path filters, concurrency limits, fallback models/credentials.
   - Govern: review memory/skill sprawl, version skill changes, separate local private skills from shareable exports.

## Deployment Mapping in Our Current Hermes Environment

Already covered by deployed skills/tools:

- Agent execution: `claude-code`, `codex`, `hermes-agent`, `opencode`.
- Hermes configuration/auth/provider pools: `hermes-agent`, `hermes-agent-operations`.
- Skill authoring/export conventions: `hermes-agent-skill-authoring`.
- MCP configuration: `native-mcp`.
- GitHub/PR/code-review work: `github-pr-workflow`, `github-code-review`, `requesting-code-review`.
- Worker orchestration: `subagent-driven-development`, `kanban-orchestrator`, `kanban-worker`, `kanban-codex-lane`.
- Debug/test disciplines: `systematic-debugging`, `test-driven-development`, `python-debugpy`, `node-inspect-debugger`.
- Webhook/cron-style event entrypoints: `webhook-subscriptions`, Hermes cron tooling.

Gaps this skill fills:

- A single harness-level design checklist spanning memory + skills + subagents + hooks + tools + CI.
- Translating Claude Code harness examples into Hermes/Codex-native patterns.
- Dedicated hook/gate thinking: dangerous command interception, sensitive-file protection, audit logs, format/lint/test gates, and worker output verification.
- Headless/CI agent governance: structured output, cost/turn limits, path filters, concurrency, and auditability.
- Capability placement decisions: what belongs in memory, a skill, a subagent, an MCP tool, a hook, a cron job, or a CI workflow.

## Capability Placement Heuristic

Use this routing table before adding new machinery:

| Need | Put it in |
|---|---|
| Stable project facts, conventions, user preferences | Memory / project docs |
| Reusable human-readable procedure | Skill `SKILL.md` |
| Large examples, checklists, policy docs | Skill `references/` |
| Deterministic repeatable action | Skill `scripts/` or project script |
| Narrow reasoning task with isolated context | Subagent / delegate_task / Codex lane |
| Typed access to external system | MCP tool or Hermes tool |
| Safety check before/after tool use | Hook/gate or approval policy |
| Scheduled or event-driven autonomous run | Cron/webhook/CI |
| Cross-agent durable task queue | Kanban |

## Harness Design Procedure

1. Identify the work unit
   - What is the user-visible outcome?
   - What files/systems may be touched?
   - What must be read-only vs writable?
   - What output must downstream humans/tools consume?

2. Define the context contract
   - Required inputs.
   - Project memory files to load.
   - Source paths and search strategy.
   - Forbidden assumptions.
   - Output schema or checklist.

3. Choose the right execution primitive
   - One-shot Hermes/Codex: bounded implementation task.
   - `delegate_task`: parallel reasoning/inspection with no durable lifetime.
   - Background process: long bounded build/test with completion notification.
   - Cron/webhook/CI: durable autonomous trigger.
   - Kanban: multi-worker durable collaboration.
   - MCP/tool: repeated typed external operation.

4. Constrain tools and permissions
   - Default to read-only for review/analysis.
   - Allow writes only in the intended workspace.
   - Allow shell commands by pattern when possible, not as blanket Bash.
   - For secrets/private files, deny by path and extension.

5. Add gates
   - Before execution: path/scope/command safety.
   - During execution: streaming logs or progress capture for long runs.
   - After edits: format/lint/tests or domain validator.
   - Before completion: verify output contract and cite real tool results.

6. Make it reusable
   - If repeated or complex, turn the harness into a skill.
   - If deterministic, add scripts/templates/references.
   - If shareable, export a depersonalized pack rather than modifying active local skills.

## Hook / Gate Patterns

Translate Claude Code hook ideas into Hermes-appropriate mechanisms:

- Dangerous command blocking
  - Prefer Hermes approvals and explicit terminal discipline.
  - For project automation, add script-level deny patterns for `rm -rf`, destructive git resets, disk formatting, credential exfiltration, etc.

- Sensitive file protection
  - Deny writes or reads for `.env`, private keys, auth files, token dumps, browser profile stores, and credential exports unless the user explicitly asks.
  - If a credential file must be inspected, summarize schema and status without printing secrets.

- Audit logs
  - Record actor, timestamp, command/action, target path, exit status, and relevant metadata.
  - Never log raw secrets.

- Format/lint feedback loop
  - Run formatters after writes when the project has a known formatter.
  - Run linters/tests in foreground with real output, or background with notify-on-complete.

- Stop quality gate
  - Autonomous workers should not claim success until tests/validators pass or blockers are explicit.

## Headless / CI Pattern

For agent runs in CI or scripts:

1. Restrict scope with path filters and event triggers.
2. Set max turns / timeouts / budget caps.
3. Use structured JSON output when downstream scripts parse results.
4. Capture logs and cost/usage metadata.
5. Use least-privilege tokens and avoid hardcoded secrets.
6. Cancel superseded runs for the same PR/branch.
7. Separate fast cheap checks from deeper expensive reviews.
8. Make failures explicit: no fabricated results, no silent pass.

## Skill Extraction Checklist

When converting a source folder or repeated workflow into skills:

- [ ] Identify reusable capability classes, not just filenames.
- [ ] Mark what is already covered by existing skills.
- [ ] Create only the missing umbrella or gap skills; avoid duplicates.
- [ ] Include trigger conditions in `description`.
- [ ] Include exact commands only when verified for Hermes/Codex, not blindly copied from Claude Code.
- [ ] Preserve source path/reference notes when local and private; remove them for shareable export.
- [ ] Add pitfalls and verification.
- [ ] Validate frontmatter and file placement.

## Common Pitfalls

1. Copying Claude Code commands directly into Hermes/Codex workflows.
   - Translate concepts first. Hermes uses its own tools, auth pool, cron, gateway, kanban, and skills.

2. Treating skills as long prompts only.
   - A real work skill should accumulate scripts, validators, references, and output contracts.

3. Over-broad Bash permissions.
   - Prefer typed tools, allowlists, or narrowly scoped terminal commands.

4. No stop gate.
   - Autonomous completion without tests/validators produces plausible but untrusted results.

5. Logging secrets during debugging.
   - Inspect schema/status, not raw tokens.

6. Duplicating deployed skills.
   - If an existing skill already owns the workflow, patch that skill or reference it instead of creating a near-duplicate.

## Assessment / Take-home Deliverable Pattern

When the user is answering an AI Coding / agent-engineering assessment, do not over-index on a polished demo. Build a main solution document plus a small harness scaffold that proves the process is concrete. The evaluator should see task packets, prompt layering, skills, hooks/gates, MCP/tool boundaries, docs/context governance, self-check, night-run automation, rollback, failure reports, and domain-specific budgets. Use the provided rubric as a revision gate: if self-check exposes a weak item, patch the deliverable and rerun the check before reporting completion.

**Product-first pitfall:** Do not leave the user with only documents and scaffold files when the prompt asks for an MVP or system. Create a visible product entry point early — e.g. `product_demo/index.html`, a minimal runnable app, CLI demo, or scripted walkthrough — and verify it by actually serving/running/opening it. The main document should link to this product entry near the top. For this user's assessment work, avoid long explanatory progress reports before the product exists; report tersely with concrete paths, commands, and verification output.

**Interview-demo evidence pitfall:** If the assessment will be defended live, do not present raw test output (`7 pass`, TAP logs, CI green) as the business demo. Tests are verification, not a human-readable demonstration. Add a `demo` command or scripted walkthrough that prints the scenario, input scale, bottleneck, tradeoff, and result in interviewer-legible terms, then run tests and harness gates after it. See `references/interview-demo-evidence-pattern.md`.

**Framework-over-product correction:** For AI Coding / harness assessments, separate “the project being built” from “the framework for building the project.” If the prompt is evaluating AI engineering ability, do not over-focus on the sample dashboard/app. Build and present the agent operating system: leader/supervisor role, project-manager/secretariat role, domain workers, task packets, worker updates, manager summaries, status memory, skills, hooks, MCP/typed tools, gates, and interview playbook. The sample product should be explicitly labeled as an example workload managed by the harness, not the center of the answer. See `references/leader-secretariat-worker-runtime-pattern.md`.

**Protocol-only-docs pitfall:** Do not stop at Markdown role descriptions and policies when the assessment asks for an MVP or “最小可用系统.” Protocol docs are necessary but not sufficient. Add a small executable or platform-native harness layer that proves routing and governance: request intake, leader classification, strategy/council deliberation if needed, authorization relay, task packet creation, worker prompt/run entrypoint, one-task `tick` for autonomous/overnight operation, gates, and tests. Keep this layer honest: if it only generates prompts, label it prompt-generation; if it invokes a real agent, show the exact worker entrypoint. Do not write fake demo scripts that simulate agent success and present them as autonomous development. See `references/agent-framework-mvp-vs-md-pattern.md`.

**Arbitrary-runtime pitfall:** Do not add Python/Node/controller code merely because a skill contains a controller pattern. The runtime layer must prove the user's actual agent framework: authorization, routing, state, audit, and worker dispatch. If the user wants a Hermes-native harness, prefer project prompts, profiles/cron/kanban, task queues, and gates over a bespoke controller. If a controller is used, it must be meaningful and tested, not a toy script.

**Governance-runtime pattern:** For class-level AI Coding harness designs, a robust public-safe organization model is `Final Authority -> Leader Gateway -> Strategy Council -> Chief Coordinator -> Mandate Relay -> Domain Bureaus -> Audit Office -> State Archive`. Use this to express user authorization, multi-perspective deliberation, delegated approval, durable content-domain workers, independent audit, and state feedback without relying on historical role names in the evaluator-facing material. See `references/governance-runtime-harness-pattern.md`. 

**User-legibility / verbosity pitfall:** When the user is asking for diagnosis, comparison, or next action in a harness assessment, keep the response terse and evidence-first. Do the file/tool work first, then report paths, commands, PASS/FAIL, and the immediate next step. Do not turn every answer into a long teacher-style explanation unless the user explicitly asks for a document, code, or creative prose.

**Workflow-correction pitfall:** When a user provides a harness workflow file with required directories and commands, execute that file literally before expanding prose. Create/patch the requested `product_demo`, `harness/{prompts,skills,hooks,mcp,reports}`, and `deliverables` assets, then run the required commands (typically `npm test` and `npm run harness:check`) and fix failures until they pass or a blocker is explicit. Do not immediately deploy a larger engineering project and do not continue broad concept-document writing.

**Command-router / worker-packet pattern:** When the user wants to say a short phrase like “美化页面” and have the project agent automatically work, add a project-level command router (`AGENT_COMMANDS.md`) and patch `AGENTS.md` to read it. For medium-grain UI/frontend tasks, prefer one accountable worker agent plus work skills, worker packets, checklists, and hooks/gates over many real subagents. Use real subagents only for escalation: independent second opinion, parallel multi-page audit, large redesign, polluted context, or explicit user request. See `references/ui-worker-command-routing-pattern.md`.

**Conversation-runtime dashboard pitfall:** If the framework includes a dashboard, normal Hermes chat tasks must enter the same runtime queue the dashboard reads. Add a conversation bridge (`chat-intake` / `register_conversation_request`) and project rule requiring actionable chat requests to be registered before execution. Do not force the user to manually create CLI tasks for ordinary agent work. Also keep external assessment/interview context out of runtime prompts and worker personas; store presentation material separately so the MVP agents simply work. See `references/conversation-runtime-dashboard-harness-pattern.md`.

**Dashboard observability / docs-sprawl pitfall:** A harness dashboard must answer operational questions, not just show raw counters: what each layer does, which agents/workers exist, which bureau owns each task, what each agent did, and exactly where reports/logs/prompts/audits/archive entries live. If the user cannot trace “who did what and where is the report,” upgrade `/api/state` and the dashboard template before writing more explanatory docs. Keep the root directory small (`README.md`, `AGENTS.md`, `SOUL.md`, `USER_INTENT.md`, `START_PROMPT.md`) and move protocol/reference/presentation docs under grouped `docs/` folders with `docs/README.md` as the index. See `references/dashboard-observability-docs-consolidation-pattern.md`.

See `references/assessment-deliverable-harness-pattern.md` for the compact workflow and recommended file shape. See `references/assessment-node-harness-mvp-pattern.md` for a concrete Node/HTML product_demo + harness/hooks pattern and pitfalls found during execution.

See `references/assessment-deliverable-harness-pattern.md` for the compact workflow and recommended file shape. See `references/assessment-node-harness-mvp-pattern.md` for a concrete Node/HTML product_demo + harness/hooks pattern and pitfalls found during execution. See `references/ui-beautification-harness-pattern.md` for applying the same harness discipline to page polish/design-improvement work.

## Verification Checklist

- [ ] The harness has a clear work unit and output contract.
- [ ] Context source files and memory layers are explicit.
- [ ] Execution primitive matches task lifetime and isolation needs.
- [ ] Permissions are least-privilege.
- [ ] Safety, audit, and quality gates are present.
- [ ] Real tests/validators or explicit blockers back the result.
- [ ] For assessments, a rubric/self-check pass was used to revise the artifact, not just rubber-stamp it.
- [ ] Reusable lessons are saved as skill updates, not stale memory.
