from __future__ import annotations

from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any
import json
import re

from .model import ROOT, write_json
from .capability_contracts import (
    MEMORY_OBJECTS,
    EvidenceTrace,
    MemoryObject,
    MemoryKind,
    RecallPolicy,
)
from .project_harness import (
    HARNESS_DIR,
    GATE_EVENTS_FILE,
    get_task,
    load_projects,
    list_artifacts,
    list_harness_tasks,
    read_jsonl,
)

CONTEXT_PACK_DIR = HARNESS_DIR / "context_packs"


@dataclass
class ContextPack:
    task_id: str
    project: dict[str, Any]
    task: dict[str, Any]
    allowed_context: list[dict[str, Any]] = field(default_factory=list)
    project_decisions: list[dict[str, Any]] = field(default_factory=list)
    related_artifacts: list[dict[str, Any]] = field(default_factory=list)
    gate_history: list[dict[str, Any]] = field(default_factory=list)
    blocker_history: list[dict[str, Any]] = field(default_factory=list)
    recalled_memory: list[dict[str, Any]] = field(default_factory=list)
    context_rules: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def _tokenize(text: str) -> set[str]:
    tokens = set(re.findall(r"[A-Za-z0-9_\u4e00-\u9fff]{2,}", text.lower()))
    # Add rough Chinese bi-grams to avoid one long Chinese string becoming one token only.
    compact = re.sub(r"\s+", "", text.lower())
    if re.search(r"[\u4e00-\u9fff]", compact):
        tokens.update(compact[i:i + 2] for i in range(max(0, len(compact) - 1)))
    return tokens


def _safe_excerpt(path: str, limit: int = 900) -> dict[str, Any]:
    p = Path(path)
    if not p.is_absolute():
        p = ROOT / p
    item: dict[str, Any] = {"path": str(p), "exists": p.exists()}
    if not p.exists():
        return item
    if p.is_dir():
        files = []
        for f in sorted(p.rglob("*")):
            if f.is_file():
                try:
                    files.append(str(f.relative_to(p)))
                except Exception:
                    files.append(str(f))
            if len(files) >= 60:
                break
        item.update({"kind": "dir", "files": files})
        return item
    try:
        item.update({"kind": "file", "excerpt": p.read_text(encoding="utf-8", errors="replace")[:limit]})
    except Exception as exc:
        item.update({"kind": "file", "error": str(exc)})
    return item


def read_memory_objects(path: Path | None = None) -> list[dict[str, Any]]:
    memory_path = path or MEMORY_OBJECTS
    if not memory_path.exists():
        return []
    rows: list[dict[str, Any]] = []
    for line in memory_path.read_text(encoding="utf-8").splitlines():
        if line.strip():
            try:
                row = json.loads(line)
                if isinstance(row, dict):
                    rows.append(row)
            except json.JSONDecodeError:
                continue
    return rows


def recall_memory(policy: RecallPolicy) -> list[dict[str, Any]]:
    rows = read_memory_objects()
    query_tokens = _tokenize(policy.query)
    ranked: list[tuple[int, dict[str, Any]]] = []
    for row in rows:
        if policy.allowed_kinds and row.get("kind") not in policy.allowed_kinds:
            continue
        tags = set(row.get("tags") or [])
        if policy.required_tags and not set(policy.required_tags).issubset(tags):
            continue
        if policy.require_evidence and not row.get("evidence"):
            continue
        haystack = " ".join([str(row.get("title", "")), str(row.get("content", "")), " ".join(map(str, tags))])
        score = len(query_tokens & _tokenize(haystack))
        if score > 0 or not query_tokens:
            ranked.append((score, row))
    ranked.sort(key=lambda x: x[0], reverse=True)
    return [r for _, r in ranked[:max(1, policy.max_items)]]


def register_task_memory(*, task_id: str, title: str, content: str, kind: MemoryKind = "case", tags: list[str] | None = None, source: str = "harness_task") -> dict[str, Any]:
    obj = MemoryObject(
        id=f"MO-{task_id}-{slug_title(title)}",
        kind=kind,
        title=title,
        content=content,
        tags=tags or ["caf", "harness", task_id],
        evidence=[EvidenceTrace(source=source, quote=content[:300], confidence=0.8)],
        freshness="current",
    )
    data = obj.to_dict()
    MEMORY_OBJECTS.parent.mkdir(parents=True, exist_ok=True)
    with MEMORY_OBJECTS.open("a", encoding="utf-8") as f:
        f.write(json.dumps(data, ensure_ascii=False) + "\n")
    return data


def slug_title(text: str) -> str:
    value = re.sub(r"[^a-zA-Z0-9\u4e00-\u9fff_-]+", "-", text).strip("-")
    return value[:32] or "memory"


def build_context_pack(task_id: str, *, max_memory: int = 5, max_artifacts: int = 12, max_gates: int = 10) -> dict[str, Any]:
    task = get_task(task_id)
    projects = load_projects().get("projects", {})
    project = projects.get(task.get("project_id"), {})
    allowed_context = [_safe_excerpt(p) for p in task.get("allowed_paths", [])]
    project_id = task.get("project_id")
    artifacts = list_artifacts(project_id=project_id)[:]
    related_artifacts = [a for a in artifacts if a.get("owner_task") == task_id]
    if len(related_artifacts) < max_artifacts:
        related_artifacts.extend([a for a in artifacts if a.get("owner_task") != task_id][: max_artifacts - len(related_artifacts)])
    gate_events = [g for g in read_jsonl(GATE_EVENTS_FILE) if g.get("project_id") == project_id or g.get("task_id") == task_id]
    try:
        from .lifecycle_gate import list_blockers, blocker_events
        blocker_history = [b for b in blocker_events() if b.get("project_id") == project_id or b.get("task_id") == task_id or b.get("rework_task_id") == task_id]
        active_blockers = list_blockers(project_id=project_id)
    except Exception:
        blocker_history = []
        active_blockers = []
    query = " ".join([task.get("title", ""), task.get("objective", ""), task.get("worker", ""), task.get("stage", "")])
    memory = recall_memory(RecallPolicy(query=query, max_items=max_memory, require_evidence=False))
    pack = ContextPack(
        task_id=task_id,
        project=project,
        task=task,
        allowed_context=allowed_context,
        project_decisions=project.get("decisions", [])[-8:],
        related_artifacts=related_artifacts[:max_artifacts],
        gate_history=gate_events[-max_gates:],
        blocker_history=blocker_history[-max_gates:],
        recalled_memory=memory,
        context_rules={
            "allowed_paths_only": True,
            "no_secret_dumping": True,
            "artifact_required": True,
            "gate_is_source_of_completion_truth": True,
            "active_blockers": active_blockers,
        },
    ).to_dict()
    CONTEXT_PACK_DIR.mkdir(parents=True, exist_ok=True)
    write_json(CONTEXT_PACK_DIR / f"{task_id}.json", pack)
    return pack


def context_summary(task_id: str) -> dict[str, Any]:
    pack = build_context_pack(task_id)
    return {
        "task_id": task_id,
        "project_id": pack.get("project", {}).get("project_id"),
        "allowed_context": len(pack.get("allowed_context", [])),
        "project_decisions": len(pack.get("project_decisions", [])),
        "related_artifacts": len(pack.get("related_artifacts", [])),
        "gate_history": len(pack.get("gate_history", [])),
        "blocker_history": len(pack.get("blocker_history", [])),
        "active_blockers": len(pack.get("context_rules", {}).get("active_blockers", [])),
        "recalled_memory": len(pack.get("recalled_memory", [])),
        "context_pack_path": str(CONTEXT_PACK_DIR / f"{task_id}.json"),
    }


def project_context_index(project_id: str) -> dict[str, Any]:
    projects = load_projects().get("projects", {})
    tasks = list_harness_tasks(project_id)
    artifacts = list_artifacts(project_id=project_id)
    gates = [g for g in read_jsonl(GATE_EVENTS_FILE) if g.get("project_id") == project_id]
    try:
        from .lifecycle_gate import list_blockers, blocker_events
        blockers = list_blockers(project_id=project_id)
        blocker_history = [b for b in blocker_events() if b.get("project_id") == project_id]
    except Exception:
        blockers = []
        blocker_history = []
    return {
        "project": projects.get(project_id, {}),
        "tasks": tasks,
        "artifacts": artifacts,
        "gate_events": gates,
        "blockers": blockers,
        "blocker_history": blocker_history,
        "counts": {
            "tasks": len(tasks),
            "artifacts": len(artifacts),
            "gate_events": len(gates),
            "blockers": len(blockers),
        },
    }
