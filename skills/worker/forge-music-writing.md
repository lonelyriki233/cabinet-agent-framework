---
name: forge-music-writing
description: Auto-forged writing skill for music tasks (music_composer_worker)
version: 1.0.0
author: SkillForge (Cabinet Agent Framework)
forge:
  domain: writing
  task_type: music
  worker: music_composer_worker
  source_request: |
    写一首中国风歌曲
  adjacent_skills: 0
  iteration_count: 0
  auto_created: true
---

# forge-music-writing

## Overview

Auto-forged skill for domain **writing** via music_composer_worker.
Created from user request: "写一首中国风歌曲"


## Input

- Task packet from framework dispatch
- User request context
- Existing project memory and state

## Process

1. Analyze the incoming task context
2. Map to writing domain operations
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
