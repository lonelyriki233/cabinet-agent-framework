from __future__ import annotations
from dataclasses import dataclass, asdict
from pathlib import Path
import json

from .model import ROOT, write_json

CAPABILITY_DIR = ROOT / "runtime" / "capability"
CAPABILITY_FILE = CAPABILITY_DIR / "audit.json"


@dataclass(frozen=True)
class CapabilityLayer:
    id: str
    name: str
    purpose: str
    current_status: str
    gap: str
    next_build: str

    def to_dict(self):
        return asdict(self)


CAPABILITY_LAYERS: list[CapabilityLayer] = [
    CapabilityLayer(
        "runtime",
        "Agent Harness Runtime",
        "任务进入、拆解、分派、执行、审计、归档。",
        "implemented",
        "已有 task packet / hooks / gates / dashboard / archive，但仍偏文件协议。",
        "保留现有 runtime，作为 CAF Core。",
    ),
    CapabilityLayer(
        "non_parametric_memory",
        "Non-parametric Memory Plane",
        "调动文档、日志、案例库、知识库、图谱、向量索引，不改模型权重。",
        "partial",
        "已有 archive/hash embedding 和 memory 文件；缺统一 memory object schema、recall policy、freshness/conflict 规则。",
        "建立 MemoryObject + RecallPolicy + EvidenceTrace。",
    ),
    CapabilityLayer(
        "parametric_memory",
        "Parametric Memory Plane",
        "把稳定技能沉淀为微调/LoRA/偏好/蒸馏数据，扩充模型能力。",
        "missing",
        "SkillForge 只写 markdown skill，未产出训练样本、偏好对、评测集或模型版本记录。",
        "建立 SkillToDataset 管线：task -> trace -> preference pair -> eval set -> adapter registry。",
    ),
    CapabilityLayer(
        "tool_mcp_device",
        "Tool / MCP / Device Interface",
        "接入 API、数据库、传感器、机器人、VLA、企业系统。",
        "partial",
        "已有 MCP/RAG 文档和 host adapter；缺 typed capability contract、dry-run、simulator、actuator risk level。",
        "建立 ToolContract：observe/decide/act 分级，默认 dry-run，执行器必须授权。",
    ),
    CapabilityLayer(
        "multimodal_vla",
        "Multimodal / VLA Extension Layer",
        "支持视觉、语音、动作、空间状态、机器人/GUI 操作。",
        "missing",
        "当前 worker 主要文本任务；没有 observation/action schema。",
        "建立 ObservationFrame / ActionProposal / SafetyEnvelope。",
    ),
    CapabilityLayer(
        "supervision",
        "Supervision and Accountability",
        "管理监督、责任链、审计、失败复盘、权限分级。",
        "implemented",
        "已有 hooks/gates/mandate/dashboard；需把风险与真实执行器绑定。",
        "加入 actuation gate：涉及设备/资金/外部消息/生产系统必须升级授权。",
    ),
    CapabilityLayer(
        "domain_template",
        "Domain Potential Templates",
        "不是直接面向所有行业，而是提供可迁移模板：服务流、生产流、管理流。",
        "partial",
        "已有 subproject template 概念；缺 entity-economy 三类抽象模板。",
        "建立 service_ops / industrial_ops / management_audit 三个最小模板。",
    ),
]


def current_caf_judgement() -> dict:
    layers = [x.to_dict() for x in CAPABILITY_LAYERS]
    implemented = [x for x in layers if x["current_status"] == "implemented"]
    partial = [x for x in layers if x["current_status"] == "partial"]
    missing = [x for x in layers if x["current_status"] == "missing"]
    return {
        "verdict": "CAF 当前是合格的 agent runtime 雏形，但还不是具备产业潜力的统筹框架。",
        "core_strength": "task lifecycle + hooks/gates + archive + dashboard + skillforge",
        "core_gap": "缺记忆平面、参数化能力沉淀、执行器/设备接口、多模态/VLA action schema。",
        "recommended_direction": "CAF Core: Agent Harness for Real-World Operations Potential",
        "layers": layers,
        "score": {
            "implemented": len(implemented),
            "partial": len(partial),
            "missing": len(missing),
            "total": len(layers),
        },
        "next_three_builds": [
            "MemoryObject + RecallPolicy + EvidenceTrace",
            "ToolContract + ActuationGate + dry-run simulator",
            "SkillToDataset: skill/trace -> preference/eval/fine-tune data",
        ],
    }


def write_capability_audit() -> dict:
    CAPABILITY_DIR.mkdir(parents=True, exist_ok=True)
    data = current_caf_judgement()
    write_json(CAPABILITY_FILE, data)
    return data


def render_text(data: dict | None = None) -> str:
    data = data or current_caf_judgement()
    lines = [
        data["verdict"],
        f"方向: {data['recommended_direction']}",
        f"强项: {data['core_strength']}",
        f"缺口: {data['core_gap']}",
        "",
        "下一步只做三件:",
    ]
    for i, item in enumerate(data["next_three_builds"], 1):
        lines.append(f"{i}. {item}")
    return "\n".join(lines)


if __name__ == "__main__":
    print(render_text(write_capability_audit()))
