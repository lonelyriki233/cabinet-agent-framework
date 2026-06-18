# Contributing

## Development loop

```bash
python3 -m cabinet_framework.cli init
python3 -m unittest discover -s tests -v
python3 scripts/build_keyword_index.py
python3 -m cabinet_framework.cli gate
```

## Design rules

1. Keep the core portable: task packets, Markdown/JSON memory, skills, hooks and dashboard should work without Hermes.
2. Put host-specific behavior in `adapters/` or `cabinet_framework/adapters.py`.
3. Attribute Hermes-derived behavior in `integrations/HERMES_ATTRIBUTION.md`.
4. Separate thinking skills from worker skills.
5. Do not hard-code one model, one vector database, one host CLI, or one project domain.
6. Add tests for every new protocol or adapter surface.

## Pull request checklist

- [ ] Tests pass.
- [ ] `caf gate` passes.
- [ ] No secrets or local absolute paths.
- [ ] Runtime cache is not committed.
- [ ] README/docs updated when behavior changes.
