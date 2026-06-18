<!-- Migrated reference. Source: local-hermes-skills/devops/agent-harness-engineering/references/leader-secretariat-worker-runtime-pattern.md. Review and depersonalize before public release if needed. -->

# Leader / Secretariat / Worker Runtime Pattern

Use this reference when an AI Coding assessment is really asking for an AI development framework, not a finished product demo.

## Core correction

Separate:

- the project being built, e.g. a high-performance analytics platform;
- the framework that builds it, i.e. the AI agent operating system.

The assessment should present the second as the primary artifact. The product/demo is only a workload managed by the framework.

## Recommended roles

```text
User
  -> Leader Agent / 领袖
  -> Secretariat Agent / 中书
  -> Domain Workers
  -> Local artifacts + Skills + Hooks + MCP + Reports + Gates
```

### Leader / 领袖

Faces the user. Responsibilities:

- understand the user's demand;
- classify task type: research, architecture, implementation, maintenance, bugfix, report, interview demo;
- read project status before deciding;
- decide whether and how to delegate to the secretariat;
- report concisely to the user with evidence paths and next step.

Pitfall: the leader must not swallow all implementation work just because it can. Its value is task judgment and state awareness.

### Secretariat / 中书

Project-manager and coordination layer. Responsibilities:

- convert leader goals into precise task packets;
- assign domain workers by project content, not generic activity type;
- collect worker updates;
- detect cross-worker dependencies;
- write manager summaries;
- update project status.

Pitfall: workers should not coordinate privately. Cross-worker linkage is routed through the secretariat.

### Workers

Long-lived workers own project domains, including both development and maintenance for that domain:

- frontend worker: UI, interactions, visualization, frontend maintenance;
- backend worker: APIs, services, interface stability, backend maintenance;
- data/perf worker: data processing, downsampling, benchmark, performance budgets;
- research worker: technical research, comparisons, tradeoffs;
- harness worker: prompts, skills, hooks, MCP, gates, runtime.

Pitfall: do not split workers purely by work verb such as “developer” vs “maintainer.” Split by durable domain ownership.

## Required artifacts

A minimal reproducible runtime should include:

```text
AGENTS.md
SOUL.md
TASK.md
README.md
docs/ARCHITECTURE.md
docs/WORKFLOW.md
docs/ROLE_CONTRACTS.md
docs/AI_AUTONOMY_BOUNDARY.md
docs/MEMORY_MODEL.md
docs/SKILLS_POLICY.md
docs/MCP_POLICY.md
docs/INTERVIEW_PLAYBOOK.md
runtime/roles/{leader,secretariat,supervisor_summarizer}.md
runtime/workers/<worker>/{scope.md,memory.md}
runtime/protocols/{task_packet,worker_update,manager_summary,skill_update_request}.template.md
runtime/state/{project_status.md,task_board.md}
harness/prompts/
harness/skills/
harness/hooks/
harness/mcp/
agentctl.py
```

## Minimal proof loop

Provide a small controller or script that proves the framework is not only prose:

```bash
python3 agentctl.py init
python3 agentctl.py demo
python3 agentctl.py status
python3 harness/hooks/run_all_gates.py
python3 harness/mcp/mock_benchmark_tool.py --rows 1000000 --budget 5000
```

The demo should create, at minimum:

- `runtime/tasks/*.md` task packet;
- `runtime/worker_outputs/*.md` output;
- `runtime/worker_updates/*.md` update;
- `runtime/manager_summaries/latest.md` manager summary;
- updated `runtime/state/project_status.md`.

## Interview framing

Say:

> I did not treat the prompt as “finish a BI dashboard.” I treated it as “design the AI development harness that can build, maintain, and govern that dashboard over time.”

Then demonstrate the runtime artifacts and gates before showing any sample product.

## Verbal discipline for this user

For this class of work, answer tersely unless asked to draft a deliverable. Prefer:

- path;
- command;
- PASS/FAIL;
- what changed;
- next concrete action.

Avoid long teacher-style explanations after the user has already corrected the direction.
