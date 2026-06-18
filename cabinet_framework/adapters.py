from __future__ import annotations
from dataclasses import dataclass
from pathlib import Path

@dataclass(frozen=True)
class CLIHostAdapter:
    name: str
    executable: str
    prompt_flag: str | None
    notes: str
    background: bool = False

    def command_for_prompt(self, prompt_path: Path, *, cwd: Path) -> list[str]:
        prompt_path = Path(prompt_path)
        if self.prompt_flag:
            return [self.executable, self.prompt_flag, prompt_path.read_text(encoding="utf-8")]
        return [self.executable, str(prompt_path)]

    def supports_background(self) -> bool:
        return self.background

ADAPTERS = {
    "hermes": CLIHostAdapter("hermes", "hermes", "chat -q", "Hermes-native path; uses Hermes tools/skills/cron when available.", True),
    "codex": CLIHostAdapter("codex", "codex", None, "Generic Codex CLI/ACP path; exact command may vary by installation."),
    "claude-code": CLIHostAdapter("claude-code", "claude", None, "Claude Code path; reads CLAUDE.md/AGENTS.md style project instructions."),
    "openclaw": CLIHostAdapter("openclaw", "openclaw", None, "OpenClaw/OpenCode-compatible CLI path; keep adapter thin."),
    "generic-cli": CLIHostAdapter("generic-cli", "sh", None, "Fallback: print prompt path and let the host agent read the task packet."),
}

def adapter_names() -> list[str]:
    return sorted(ADAPTERS)

def get_adapter(name: str) -> CLIHostAdapter:
    if name not in ADAPTERS:
        raise KeyError(f"unknown adapter: {name}")
    return ADAPTERS[name]
