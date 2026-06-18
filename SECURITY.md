# Security Policy

## Supported scope

This repository is a local agent-framework runtime. It creates task packets, prompts, logs, archives and dashboard views. It is not a hardened multi-tenant service.

## Reporting issues

Open a private advisory or contact the maintainer before publishing details if you find:

- credential leakage
- path traversal
- unsafe command execution
- dashboard exposure of private data
- prompt templates that instruct agents to exfiltrate data

## Secret handling rules

- Never commit `.env`, `auth.json`, credentials, API keys, OAuth tokens or private keys.
- Keep generated runtime logs out of git.
- Redact sensitive values as `[REDACTED]` in reports.
- Host adapters must pass task packets and allowed paths, not broad filesystem access.
