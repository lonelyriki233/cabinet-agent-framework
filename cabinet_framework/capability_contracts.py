from __future__ import annotations
from dataclasses import dataclass, asdict, field
from pathlib import Path
from typing import Literal, Any
import json

from .model import ROOT, now

MemoryKind = Literal["document", "case", "log", "skill", "graph", "tool_trace", "human_feedback"]
RiskLevel = Literal["observe", "suggest", "dry_run", "act"]

MEMORY_OBJECTS = ROOT / "runtime" / "memory_objects.jsonl"
TOOL_CONTRACTS = ROOT / "runtime" / "tool_contracts.jsonl"
PARAM_DATASET = ROOT / "runtime" / "parametric_memory" / "training_examples.jsonl"


@dataclass
class EvidenceTrace:
    source: str
    quote: str = ""
    confidence: float = 0.5
    created_at: str = field(default_factory=now)

    def to_dict(self):
        return asdict(self)


@dataclass
class MemoryObject:
    id: str
    kind: MemoryKind
    title: str
    content: str
    tags: list[str] = field(default_factory=list)
    evidence: list[EvidenceTrace] = field(default_factory=list)
    freshness: str = "unknown"
    conflicts_with: list[str] = field(default_factory=list)
    created_at: str = field(default_factory=now)

    def to_dict(self):
        data = asdict(self)
        data["evidence"] = [e.to_dict() if hasattr(e, "to_dict") else e for e in self.evidence]
        return data


@dataclass
class RecallPolicy:
    query: str
    allowed_kinds: list[MemoryKind] = field(default_factory=list)
    required_tags: list[str] = field(default_factory=list)
    max_items: int = 5
    require_evidence: bool = False


@dataclass
class ToolContract:
    name: str
    purpose: str
    risk_level: RiskLevel
    input_schema: dict[str, Any]
    output_schema: dict[str, Any]
    side_effects: list[str] = field(default_factory=list)
    requires_authority: str = "L1"
    dry_run_available: bool = True

    def to_dict(self):
        return asdict(self)


def append_jsonl(path: Path, data: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as f:
        f.write(json.dumps(data, ensure_ascii=False) + "\n")


def register_memory_object(obj: MemoryObject) -> dict:
    append_jsonl(MEMORY_OBJECTS, obj.to_dict())
    return obj.to_dict()


def register_tool_contract(contract: ToolContract) -> dict:
    append_jsonl(TOOL_CONTRACTS, contract.to_dict())
    return contract.to_dict()


def export_parametric_example(*, task_id: str, instruction: str, good_output: str, bad_output: str = "", feedback: str = "", source: str = "runtime_trace") -> dict:
    """Export stable task traces into future fine-tune / LoRA / preference data.
    Does not train a model; it creates auditable training candidates.
    """
    ex = {
        "task_id": task_id,
        "source": source,
        "instruction": instruction,
        "chosen": good_output,
        "rejected": bad_output,
        "feedback": feedback,
        "created_at": now(),
        "status": "candidate",
    }
    append_jsonl(PARAM_DATASET, ex)
    return ex


def default_contracts() -> list[ToolContract]:
    return [
        ToolContract(
            name="enterprise_api_read",
            purpose="读取企业系统/API/数据库中的授权数据。",
            risk_level="observe",
            input_schema={"endpoint": "string", "query": "object"},
            output_schema={"records": "array", "trace_id": "string"},
            side_effects=[],
            requires_authority="L1",
        ),
        ToolContract(
            name="external_action_proposal",
            purpose="生成外部动作提案，如发消息、改工单、控制设备；默认不执行。",
            risk_level="dry_run",
            input_schema={"goal": "string", "action": "object", "target": "string"},
            output_schema={"proposal": "object", "risk": "string", "needs_approval": "boolean"},
            side_effects=["external_system_change"],
            requires_authority="L3",
        ),
        ToolContract(
            name="vla_action_frame",
            purpose="承载视觉-语言-动作模型的观测帧与动作候选；必须经过安全包络。",
            risk_level="suggest",
            input_schema={"observation": "object", "instruction": "string"},
            output_schema={"action_candidates": "array", "safety_envelope": "object"},
            side_effects=["physical_or_gui_action_if_executed"],
            requires_authority="L4",
            dry_run_available=True,
        ),
    ]


def install_default_contracts() -> list[dict]:
    return [register_tool_contract(c) for c in default_contracts()]
