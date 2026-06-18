<!-- Migrated reference. Source: local-hermes-skills/software-development/html5-game-worker/references/worker-vs-think-skill.md. Review and depersonalize before public release if needed. -->

# Worker vs Think Skill for HTML5 Game Projects

Use this note when the user objects that a "worker" has turned into a planning memo.

## Durable lesson

For this task class, "worker" means a real local source project that can be called and extended, similar to keeping a framework source tree locally and then creating game instances on top of it.

## Expected shape

- framework/project root exists locally;
- `src/` contains separated modules such as `kernel/`, `sim/`, `render/`, `ui/`, `data/`, `styles/`;
- one public entry module exports the supported API;
- examples live under `examples/` and import the framework rather than re-embedding all logic;
- verification includes syntax check, local server, browser-open test, and an interaction proof.

## Bad pattern

- long architecture explanation;
- no reusable source tree;
- only a single throwaway demo file;
- calling a doctrine/skill document itself the worker.

## Good pattern

1. Name the framework/worker.
2. Create the source tree.
3. Establish the public entry module and exports.
4. Port the first demo into `examples/` using that API.
5. Verify that the example actually runs.
6. Only then discuss deeper abstractions or future engine features.
