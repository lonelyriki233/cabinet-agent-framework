from __future__ import annotations

from dataclasses import dataclass, asdict, field
from pathlib import Path
from typing import Literal, Any
from datetime import datetime
import hashlib
import json
import re

from .model import ROOT, RUNTIME, write_json, read_json

HARNESS_DIR = RUNTIME / "project_harness"
PROJECTS_FILE = HARNESS_DIR / "projects.json"
ARTIFACTS_FILE = HARNESS_DIR / "artifacts.jsonl"
GATE_EVENTS_FILE = HARNESS_DIR / "gate_events.jsonl"

ProjectStatus = Literal["planned", "active", "blocked", "completed", "archived"]
TaskStage = Literal["intake", "design", "implementation", "test", "review", "delivery", "archive"]
ArtifactType = Literal["code", "docs", "tests", "design", "logs", "config", "decision", "review", "rollback", "other"]
ArtifactStatus = Literal["draft", "ready", "validated", "rejected", "archived"]
GateStatus = Literal["pass", "fail", "warn"]


STAGE_GATES: dict[str, list[str]] = {
    "intake": ["objective_present", "acceptance_present"],
    "design": ["design_artifact_registered", "acceptance_present"],
    "implementation": ["artifact_registered", "owner_task_present"],
    "test": ["test_artifact_registered", "validation_present"],
    "review": ["review_artifact_registered", "validation_present"],
    "delivery": ["all_required_artifacts_validated"],
    "archive": ["delivery_passed", "artifacts_archivable"],
}


def now() -> str:
    return datetime.now().strftime("%Y%m%dT%H%M%S")


def slug(text: str) -> str:
    value = re.sub(r"[^a-zA-Z0-9\u4e00-\u9fff_-]+", "-", text).strip("-")
    return value[:48] or "item"


def ensure_harness() -> None:
    HARNESS_DIR.mkdir(parents=True, exist_ok=True)
    if not PROJECTS_FILE.exists():
        write_json(PROJECTS_FILE, {"projects": {}})
    if not ARTIFACTS_FILE.exists():
        ARTIFACTS_FILE.write_text("", encoding="utf-8")
    if not GATE_EVENTS_FILE.exists():
        GATE_EVENTS_FILE.write_text("", encoding="utf-8")


def append_jsonl(path: Path, row: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as f:
        f.write(json.dumps(row, ensure_ascii=False) + "\n")


def read_jsonl(path: Path) -> list[dict[str, Any]]:
    if not path.exists():
        return []
    rows = []
    for line in path.read_text(encoding="utf-8").splitlines():
        if line.strip():
            rows.append(json.loads(line))
    return rows


def file_hash(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


@dataclass
class HarnessProject:
    project_id: str
    name: str
    objective: str
    status: ProjectStatus = "active"
    modules: list[dict[str, Any]] = field(default_factory=list)
    milestones: list[dict[str, Any]] = field(default_factory=list)
    risks: list[dict[str, Any]] = field(default_factory=list)
    decisions: list[dict[str, Any]] = field(default_factory=list)
    acceptance_criteria: list[str] = field(default_factory=list)
    created_at: str = field(default_factory=now)
    updated_at: str = field(default_factory=now)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class HarnessTask:
    task_id: str
    project_id: str
    title: str
    objective: str
    stage: TaskStage
    worker: str
    acceptance_criteria: list[str]
    dependencies: list[str] = field(default_factory=list)
    allowed_paths: list[str] = field(default_factory=list)
    required_artifact_types: list[str] = field(default_factory=list)
    source_task_id: str | None = None
    source: str | None = None
    authority_level: str | None = None
    status: str = "ready"
    created_at: str = field(default_factory=now)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class ArtifactRecord:
    artifact_id: str
    project_id: str
    owner_task: str
    path: str
    type: ArtifactType
    status: ArtifactStatus
    sha256: str | None
    validation_result: dict[str, Any]
    related_decisions: list[str] = field(default_factory=list)
    created_at: str = field(default_factory=now)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class GateResult:
    gate_id: str
    project_id: str
    task_id: str
    stage: TaskStage
    status: GateStatus
    messages: list[str]
    checked_at: str = field(default_factory=now)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def load_projects() -> dict[str, Any]:
    ensure_harness()
    data = read_json(PROJECTS_FILE, {"projects": {}})
    return data if isinstance(data, dict) else {"projects": {}}


def save_projects(data: dict[str, Any]) -> None:
    ensure_harness()
    write_json(PROJECTS_FILE, data)


def create_project(name: str, objective: str, acceptance_criteria: list[str] | None = None) -> dict[str, Any]:
    ensure_harness()
    pid = f"P-{now()}-{slug(name)}"
    project = HarnessProject(
        project_id=pid,
        name=name,
        objective=objective,
        acceptance_criteria=acceptance_criteria or [],
    )
    data = load_projects()
    data["projects"][pid] = project.to_dict()
    save_projects(data)
    return project.to_dict()


def add_module(project_id: str, name: str, purpose: str) -> dict[str, Any]:
    data = load_projects()
    project = data["projects"][project_id]
    module = {"module_id": f"M-{slug(name)}", "name": name, "purpose": purpose, "created_at": now()}
    project.setdefault("modules", []).append(module)
    project["updated_at"] = now()
    save_projects(data)
    return module


def add_decision(project_id: str, title: str, rationale: str, consequences: list[str] | None = None) -> dict[str, Any]:
    data = load_projects()
    project = data["projects"][project_id]
    decision = {
        "decision_id": f"D-{now()}-{slug(title)}",
        "title": title,
        "rationale": rationale,
        "consequences": consequences or [],
        "created_at": now(),
    }
    project.setdefault("decisions", []).append(decision)
    project["updated_at"] = now()
    save_projects(data)
    return decision


def create_harness_task(
    project_id: str,
    title: str,
    objective: str,
    stage: TaskStage,
    worker: str,
    acceptance_criteria: list[str],
    required_artifact_types: list[str] | None = None,
    dependencies: list[str] | None = None,
    allowed_paths: list[str] | None = None,
    source_task_id: str | None = None,
    source: str | None = None,
    authority_level: str | None = None,
) -> dict[str, Any]:
    ensure_harness()
    task = HarnessTask(
        task_id=f"HT-{now()}-{slug(title)}",
        project_id=project_id,
        title=title,
        objective=objective,
        stage=stage,
        worker=worker,
        acceptance_criteria=acceptance_criteria,
        dependencies=dependencies or [],
        allowed_paths=allowed_paths or ["."],
        required_artifact_types=required_artifact_types or [],
        source_task_id=source_task_id,
        source=source,
        authority_level=authority_level,
    )
    task_path = HARNESS_DIR / "tasks" / f"{task.task_id}.json"
    write_json(task_path, task.to_dict())
    return task.to_dict()


def list_harness_tasks(project_id: str | None = None) -> list[dict[str, Any]]:
    ensure_harness()
    task_dir = HARNESS_DIR / "tasks"
    if not task_dir.exists():
        return []
    tasks = []
    for p in sorted(task_dir.glob("*.json")):
        item = read_json(p)
        if isinstance(item, dict):
            tasks.append(item)
    if project_id:
        tasks = [t for t in tasks if t.get("project_id") == project_id]
    return tasks


def get_task(task_id: str) -> dict[str, Any]:
    path = HARNESS_DIR / "tasks" / f"{task_id}.json"
    data = read_json(path)
    if not data:
        raise FileNotFoundError(task_id)
    return data


def register_artifact(
    project_id: str,
    owner_task: str,
    path: str,
    artifact_type: ArtifactType,
    status: ArtifactStatus = "ready",
    validation_result: dict[str, Any] | None = None,
    related_decisions: list[str] | None = None,
) -> dict[str, Any]:
    ensure_harness()
    p = Path(path)
    if not p.is_absolute():
        p = ROOT / p
    sha = file_hash(p) if p.exists() and p.is_file() else None
    record = ArtifactRecord(
        artifact_id=f"A-{now()}-{slug(p.name)}",
        project_id=project_id,
        owner_task=owner_task,
        path=str(p),
        type=artifact_type,
        status=status,
        sha256=sha,
        validation_result=validation_result or {"status": "unknown", "message": "not validated"},
        related_decisions=related_decisions or [],
    )
    append_jsonl(ARTIFACTS_FILE, record.to_dict())
    return record.to_dict()


def list_artifacts(project_id: str | None = None, owner_task: str | None = None) -> list[dict[str, Any]]:
    rows = read_jsonl(ARTIFACTS_FILE)
    if project_id:
        rows = [r for r in rows if r.get("project_id") == project_id]
    if owner_task:
        rows = [r for r in rows if r.get("owner_task") == owner_task]
    return rows


def run_stage_gate(task_id: str) -> dict[str, Any]:
    ensure_harness()
    task = get_task(task_id)
    project_id = task["project_id"]
    stage = task["stage"]
    artifacts = list_artifacts(project_id=project_id, owner_task=task_id)
    messages: list[str] = []
    status: GateStatus = "pass"

    def fail(msg: str) -> None:
        nonlocal status
        status = "fail"
        messages.append("FAIL: " + msg)

    def ok(msg: str) -> None:
        messages.append("PASS: " + msg)

    if not task.get("objective"):
        fail("task objective is missing")
    else:
        ok("task objective present")
    if not task.get("acceptance_criteria"):
        fail("acceptance criteria missing")
    else:
        ok("acceptance criteria present")

    required = set(task.get("required_artifact_types") or [])
    existing_types = {a.get("type") for a in artifacts}
    for t in sorted(required):
        if t not in existing_types:
            fail(f"required artifact type missing: {t}")
        else:
            ok(f"required artifact type present: {t}")

    if stage in ["implementation", "test", "review", "delivery", "archive"] and not artifacts:
        fail("no artifacts registered for task")
    elif artifacts:
        ok(f"registered artifacts: {len(artifacts)}")

    if stage in ["test", "review", "delivery", "archive"]:
        bad = [a for a in artifacts if a.get("validation_result", {}).get("status") not in ["pass", "ok"]]
        if bad:
            fail(f"artifacts without passing validation: {len(bad)}")
        else:
            ok("artifact validation passed")

    if stage == "delivery":
        not_validated = [a for a in artifacts if a.get("status") != "validated"]
        if not_validated:
            fail(f"delivery requires validated artifacts: {len(not_validated)} not validated")
        else:
            ok("all delivery artifacts validated")

    result = GateResult(
        gate_id=f"G-{now()}-{task_id}",
        project_id=project_id,
        task_id=task_id,
        stage=stage,
        status=status,
        messages=messages,
    ).to_dict()
    append_jsonl(GATE_EVENTS_FILE, result)
    return result


def harness_status() -> dict[str, Any]:
    ensure_harness()
    projects = load_projects().get("projects", {})
    tasks = list_harness_tasks()
    artifacts = list_artifacts()
    gate_events = read_jsonl(GATE_EVENTS_FILE)
    return {
        "projects": len(projects),
        "tasks": len(tasks),
        "artifacts": len(artifacts),
        "gate_events": len(gate_events),
        "active_projects": [p for p in projects.values() if p.get("status") == "active"],
        "last_gate": gate_events[-1] if gate_events else None,
    }


def run_demo_loop() -> dict[str, Any]:
    project = create_project(
        "CAF v1.0 Harness Demo",
        "验证需求→任务→artifact→gate→archive 的最小闭环",
        ["能创建项目", "能创建任务", "能注册artifact", "gate能阻止缺失产物", "gate能通过合格产物"],
    )
    task = create_harness_task(
        project_id=project["project_id"],
        title="实现最小闭环说明",
        objective="产出一份最小闭环说明文档并通过 gate",
        stage="delivery",
        worker="documentation_worker",
        acceptance_criteria=["文档存在", "artifact 已注册", "validation 通过"],
        required_artifact_types=["docs"],
        allowed_paths=["runtime/project_harness/demo"],
    )
    demo_path = HARNESS_DIR / "demo" / "minimal_loop.md"
    demo_path.parent.mkdir(parents=True, exist_ok=True)
    demo_path.write_text(
        "# CAF v1.0 Minimal Loop\n\n需求输入 → 项目拆解 → 任务生成 → Artifact 注册 → Gate 审查 → 通过归档。\n",
        encoding="utf-8",
    )
    artifact = register_artifact(
        project_id=project["project_id"],
        owner_task=task["task_id"],
        path=str(demo_path),
        artifact_type="docs",
        status="validated",
        validation_result={"status": "pass", "message": "demo artifact exists"},
    )
    gate = run_stage_gate(task["task_id"])
    return {"project": project, "task": task, "artifact": artifact, "gate": gate}
