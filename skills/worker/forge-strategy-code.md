---
name: forge-strategy-code
description: Auto-forged code skill for strategy tasks (cabinet_strategy_worker)
version: 1.0.0
author: SkillForge (Cabinet Agent Framework)
forge:
  domain: code
  task_type: strategy
  worker: cabinet_strategy_worker
  source_request: |
    帮我分析这个代码项目结构
  adjacent_skills: 0
  iteration_count: 0
  auto_created: true
---

# forge-strategy-code

## Overview

Auto-forged skill for domain **code** via cabinet_strategy_worker.
Created from user request: "帮我分析这个代码项目结构"


## Input

- Task packet from framework dispatch
- User request context
- Existing project memory and state

## Process

1. Analyze the incoming task context
2. Map to code domain operations
3. Execute with worker guidelines and gate constraints
4. Output structured results

## Output

- Task outputs in `runtime/outputs/`
- Updated state and memory
- Audit entries

## Quality Gates

- [ ] Output exists and is parseable
- [ ] Acceptance criteria met
- [ ] No forbidden paths touched
- [ ] Source attribution clear

## Pitfalls

- Initial version: may need calibration
- User feedback loop: expect iterations
