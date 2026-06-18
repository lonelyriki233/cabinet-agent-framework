from __future__ import annotations
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Protocol, Callable, Any
import json

@dataclass
class SDKTaskPacket:
    task_id: str
    task_type: str
    worker: str
    objective: str
    context: str
    allowed_paths: list[str]
    forbidden_paths: list[str]
    acceptance_criteria: list[str]
    required_outputs: list[str]
    gates: list[str]
    authority_level: str = "L1"
    status: str = "ready"
    source: str = "sdk"

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

class HostAdapter(Protocol):
    name: str
    def command_for_prompt(self, prompt_path: Path, *, cwd: Path) -> list[str]: ...
    def supports_background(self) -> bool: ...

class WorkerRegistry:
    def __init__(self) -> None:
        self._workers: dict[str, dict[str, Any]] = {}
    def register(self, name: str, *, bureau: str, description: str, handler: Callable | None = None) -> None:
        self._workers[name] = {"bureau": bureau, "description": description, "handler": handler}
    def get(self, name: str) -> dict[str, Any]:
        return self._workers[name]
    def list(self) -> dict[str, dict[str, Any]]:
        return dict(self._workers)

class TaskStore:
    def __init__(self, root: Path) -> None:
        self.root = Path(root)
        self.tasks = self.root / "runtime" / "tasks"
        self.tasks.mkdir(parents=True, exist_ok=True)
    def write(self, packet: SDKTaskPacket | dict[str, Any]) -> Path:
        data = packet.to_dict() if hasattr(packet, "to_dict") else dict(packet)
        if not data.get("task_id"):
            raise ValueError("task_id required")
        path = self.tasks / f"{data['task_id']}.json"
        path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
        return path
    def read(self, task_id: str) -> dict[str, Any]:
        return json.loads((self.tasks / f"{task_id}.json").read_text(encoding="utf-8"))
    def list(self, status: str | None = None) -> list[dict[str, Any]]:
        out=[]
        for p in sorted(self.tasks.glob("*.json")):
            data=json.loads(p.read_text(encoding="utf-8"))
            if status is None or data.get("status")==status:
                out.append(data)
        return out

def load_markdown_skill(path: Path) -> dict[str, str]:
    text = Path(path).read_text(encoding="utf-8")
    title = Path(path).stem
    if text.startswith("---"):
        _, fm, body = text.split("---", 2)
        return {"name": title, "frontmatter": fm.strip(), "body": body.strip()}
    return {"name": title, "frontmatter": "", "body": text.strip()}
