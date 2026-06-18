from __future__ import annotations
import shlex, shutil, subprocess
from pathlib import Path
from .model import ROOT, LOGS, read_json, write_json, write_text

WORKER_RUNTIME = {
    "frontend_worker": {
        "toolsets": "terminal,file,browser",
        "skills": "html5-game-worker,requesting-code-review",
        "max_turns": "60",
    },
    "backend_worker": {
        "toolsets": "terminal,file,web",
        "skills": "systematic-debugging,test-driven-development",
        "max_turns": "70",
    },
    "data_perf_worker": {
        "toolsets": "terminal,file",
        "skills": "test-driven-development,systematic-debugging",
        "max_turns": "70",
    },
    "research_worker": {
        "toolsets": "web,file,terminal",
        "skills": "agent-harness-engineering",
        "max_turns": "50",
    },
    "harness_worker": {
        "toolsets": "terminal,file,cronjob",
        "skills": "agent-harness-engineering,hermes-agent",
        "max_turns": "80",
    },
    "documentation_worker": {
        "toolsets": "file,terminal",
        "skills": "agent-harness-engineering",
        "max_turns": "50",
    },
}


def runtime_for_worker(worker: str) -> dict:
    return WORKER_RUNTIME.get(worker, {"toolsets": "file,terminal", "skills": "agent-harness-engineering", "max_turns": "50"})


def build_hermes_command(prompt: str, worker: str, authority_level: str = "L1", dry: bool = False) -> list[str]:
    cfg = runtime_for_worker(worker)
    # L1 only creates prompt. L2/L3 may run local writes. We still avoid --yolo by default.
    cmd = [
        "hermes", "chat",
        "--quiet",
        "--max-turns", cfg["max_turns"],
        "-t", cfg["toolsets"],
        "-s", cfg["skills"],
        "-q", prompt,
    ]
    return cmd


def shell_command_for_prompt(prompt: str, worker: str, authority_level: str = "L1") -> str:
    return " ".join(shlex.quote(x) for x in build_hermes_command(prompt, worker, authority_level))


def execute_hermes_worker(task_path: Path, prompt: str, authority_level: str = "L2") -> tuple[int, Path, str]:
    task = read_json(task_path)
    worker = task.get("worker", "unknown")
    log = LOGS / f"{task['task_id']}.hermes.log"
    if not shutil.which("hermes"):
        write_text(log, "BLOCKED: hermes command not found\n")
        return 127, log, "hermes command not found"
    cmd = build_hermes_command(prompt, worker, authority_level)
    run = subprocess.run(cmd, cwd=ROOT, text=True, capture_output=True, timeout=900)
    write_text(log, "COMMAND\n" + " ".join(shlex.quote(x) for x in cmd) + "\n\nSTDOUT\n" + run.stdout + "\nSTDERR\n" + run.stderr)
    return run.returncode, log, "ok" if run.returncode == 0 else f"hermes exit {run.returncode}"
