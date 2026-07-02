from __future__ import annotations

from pathlib import Path
from typing import Any
import json

from .model import ROOT, write_json, write_text, read_json
from .hooks import emit_hook
from .project_harness import (
    HARNESS_DIR,
    get_task,
    register_artifact,
    run_stage_gate,
    list_artifacts,
)
from .context_engine import build_context_pack

PROMPTS_DIR = HARNESS_DIR / "worker_prompts"
EXECUTION_DIR = HARNESS_DIR / "worker_execution"
SUBMISSIONS_DIR = HARNESS_DIR / "worker_submissions"


def _rel(path: Path) -> str:
    try:
        return str(path.relative_to(ROOT))
    except Exception:
        return str(path)


def _rooted(path: str) -> Path:
    p = Path(path)
    return p if p.is_absolute() else ROOT / p


def _safe_context_excerpt(path: str, limit: int = 1200) -> dict[str, Any]:
    p = _rooted(path)
    if not p.exists():
        return {"path": str(p), "exists": False}
    if p.is_dir():
        children = sorted([str(x.relative_to(p)) for x in p.rglob("*") if x.is_file()])[:40]
        return {"path": str(p), "exists": True, "kind": "dir", "files": children}
    try:
        text = p.read_text(encoding="utf-8", errors="replace")[:limit]
        return {"path": str(p), "exists": True, "kind": "file", "excerpt": text}
    except Exception as exc:
        return {"path": str(p), "exists": True, "kind": "file", "error": str(exc)}


def build_harness_worker_prompt(task: dict[str, Any]) -> str:
    context_pack = build_context_pack(task["task_id"])
    required_types = task.get("required_artifact_types") or []
    compact_context = {
        "context_pack_path": str(HARNESS_DIR / "context_packs" / f"{task['task_id']}.json"),
        "project_decisions": context_pack.get("project_decisions", []),
        "allowed_context": context_pack.get("allowed_context", []),
        "related_artifacts": context_pack.get("related_artifacts", []),
        "gate_history": context_pack.get("gate_history", []),
        "recalled_memory": context_pack.get("recalled_memory", []),
        "context_rules": context_pack.get("context_rules", {}),
    }
    return f"""
你是 CAF Agent Project Harness 的 worker：{task.get('worker')}。

你正在执行 HarnessTask，不是自由聊天。

任务ID：{task.get('task_id')}
项目ID：{task.get('project_id')}
阶段：{task.get('stage')}
标题：{task.get('title')}
目标：{task.get('objective')}
依赖：{', '.join(task.get('dependencies', [])) or '无'}
允许路径：{', '.join(task.get('allowed_paths', [])) or '无'}
必需产物类型：{', '.join(required_types) or '无'}
验收标准：{'; '.join(task.get('acceptance_criteria', [])) or '无'}

Context Pack：
{json.dumps(compact_context, ensure_ascii=False, indent=2)}

执行协议：
1. 只读取/修改 allowed_paths 范围内文件。
2. 优先使用 Context Pack 中的 project decisions / gate history / recalled memory。
3. 产出必须是可登记 artifact，不要只口头总结。
4. 完成后提交 JSON manifest，格式：
   {{
     "task_id": "{task.get('task_id')}",
     "status": "done|blocked|failed",
     "artifacts": [
       {{"path": "相对或绝对路径", "type": "docs|code|tests|design|logs|config|decision|review|rollback|other", "status": "ready|validated", "validation_result": {{"status": "pass|fail|unknown", "message": "..."}}}}
     ],
     "blockers": [],
     "notes": "..."
   }}
5. Gate 只相信 Artifact Registry，不相信口头声明。
6. 如果无法完成，明确 blocker，不要伪造产物。
""".strip()


def prepare_harness_worker(task_id: str) -> dict[str, Any]:
    task = get_task(task_id)
    PROMPTS_DIR.mkdir(parents=True, exist_ok=True)
    EXECUTION_DIR.mkdir(parents=True, exist_ok=True)
    prompt = build_harness_worker_prompt(task)
    prompt_path = PROMPTS_DIR / f"{task_id}.md"
    write_text(prompt_path, prompt)
    emit_hook("harness.worker.prepared", "pass", task, {"prompt_path": _rel(prompt_path)})
    artifact = register_artifact(
        project_id=task["project_id"],
        owner_task=task_id,
        path=str(prompt_path),
        artifact_type="logs",
        status="validated",
        validation_result={"status": "pass", "message": "worker prompt prepared"},
    )
    return {"task": task, "prompt_path": str(prompt_path), "prompt_artifact": artifact}


def submit_worker_manifest(manifest_path: str) -> dict[str, Any]:
    path = _rooted(manifest_path)
    manifest = read_json(path)
    if not isinstance(manifest, dict):
        raise ValueError(f"invalid manifest: {manifest_path}")
    task_id = manifest.get("task_id")
    if not task_id:
        raise ValueError("manifest missing task_id")
    task = get_task(task_id)
    registered = []
    for item in manifest.get("artifacts", []):
        registered.append(register_artifact(
            project_id=task["project_id"],
            owner_task=task_id,
            path=item["path"],
            artifact_type=item.get("type", "other"),
            status=item.get("status", "ready"),
            validation_result=item.get("validation_result") or {"status": "unknown", "message": "worker submitted"},
        ))
    record = {
        "task_id": task_id,
        "manifest_path": str(path),
        "status": manifest.get("status", "unknown"),
        "registered_artifacts": [a["artifact_id"] for a in registered],
        "blockers": manifest.get("blockers", []),
        "notes": manifest.get("notes", ""),
    }
    SUBMISSIONS_DIR.mkdir(parents=True, exist_ok=True)
    write_json(SUBMISSIONS_DIR / f"{task_id}.json", record)
    emit_hook("harness.worker.submitted", "pass" if not record["blockers"] else "blocked", task, record)
    return record


def run_harness_worker(task_id: str, mode: str = "prompt") -> dict[str, Any]:
    """Prepare or run a harness worker.

    mode=prompt: generate worker prompt and register it as log artifact.
    mode=local-report: create an execution report artifact only. This verifies runtime plumbing, not domain completion.
    """
    prepared = prepare_harness_worker(task_id)
    task = prepared["task"]
    if mode == "prompt":
        return {"mode": mode, **prepared}
    if mode == "local-report":
        report_path = EXECUTION_DIR / f"{task_id}.execution_report.md"
        existing = list_artifacts(project_id=task["project_id"], owner_task=task_id)
        write_text(report_path, "\n".join([
            f"# Harness Worker Execution Report: {task_id}",
            "",
            f"Project: {task.get('project_id')}",
            f"Worker: {task.get('worker')}",
            f"Stage: {task.get('stage')}",
            "",
            "This report verifies Worker Runtime plumbing only.",
            "Domain artifacts must still be submitted separately and pass gate.",
            "",
            f"Existing registered artifacts: {len(existing)}",
        ]))
        artifact = register_artifact(
            project_id=task["project_id"],
            owner_task=task_id,
            path=str(report_path),
            artifact_type="logs",
            status="validated",
            validation_result={"status": "pass", "message": "local execution report written"},
        )
        emit_hook("harness.worker.local_report", "pass", task, {"report_path": _rel(report_path)})
        return {"mode": mode, **prepared, "execution_report": str(report_path), "report_artifact": artifact}
    raise ValueError("mode must be prompt or local-report")


def run_worker_and_gate(task_id: str, mode: str = "prompt") -> dict[str, Any]:
    worker_result = run_harness_worker(task_id, mode=mode)
    gate = run_stage_gate(task_id)
    return {"worker": worker_result, "gate": gate}
