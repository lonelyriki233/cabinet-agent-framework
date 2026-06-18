# Hermes capability decision

## Current judgment

Hermes already provides enough native ability for these parts:

- continuous execution inside Hermes sessions
- skills preloading
- toolset restriction
- cron scheduling
- kanban coordination
- profiles for isolation
- hooks for guards
- MCP for external typed tools

## Therefore

- Do not add a custom MCP layer unless a real gap appears.
- Do not add cron/kanban/profile wrappers unless the native Hermes path is insufficient.
- Use Hermes-native capabilities first.

## Need to verify in implementation

- Whether the current project can express the continuous dispatcher entirely through Hermes-native prompts + runtime state.
- Whether the dashboard can read local runtime files without any extra model dependency.
- Whether layered vector archive can be implemented as local code and indexed files.

## If Hermes is enough

Then the project only needs:

- prompts/skills/docs
- local runtime state
- dashboard service
- layered archive code
- gates and checks

## If Hermes is not enough

Only then add MCP bridge endpoints.


## Update

At the current stage, Hermes native MCP appears sufficient for this framework. Do not build a custom MCP bridge unless the next implementation step proves a concrete missing capability.
