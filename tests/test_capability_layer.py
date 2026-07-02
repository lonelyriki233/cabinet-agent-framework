import json
import unittest
from pathlib import Path

from cabinet_framework.capability import current_caf_judgement
from cabinet_framework.capability_contracts import (
    MemoryObject,
    EvidenceTrace,
    ToolContract,
    register_memory_object,
    register_tool_contract,
    export_parametric_example,
)


class TestCapabilityLayer(unittest.TestCase):
    def test_capability_audit_has_required_gaps(self):
        data = current_caf_judgement()
        self.assertIn("产业潜力", data["verdict"])
        ids = [x["id"] for x in data["layers"]]
        self.assertIn("non_parametric_memory", ids)
        self.assertIn("parametric_memory", ids)
        self.assertIn("multimodal_vla", ids)

    def test_memory_tool_and_parametric_exports(self):
        mem = register_memory_object(MemoryObject(
            id="test-memory-object",
            kind="case",
            title="测试案例",
            content="一次可复用的 agent 任务轨迹",
            tags=["test"],
            evidence=[EvidenceTrace(source="unit-test", quote="evidence")],
        ))
        self.assertEqual(mem["kind"], "case")
        self.assertEqual(mem["evidence"][0]["source"], "unit-test")

        contract = register_tool_contract(ToolContract(
            name="test_actuator",
            purpose="测试执行器合约",
            risk_level="dry_run",
            input_schema={"x": "string"},
            output_schema={"ok": "boolean"},
            side_effects=["external_change"],
            requires_authority="L3",
        ))
        self.assertEqual(contract["risk_level"], "dry_run")
        self.assertEqual(contract["requires_authority"], "L3")

        ex = export_parametric_example(
            task_id="task-test",
            instruction="如何处理一个任务",
            good_output="先识别边界，再执行，再验证。",
            bad_output="直接执行。",
            feedback="需要先判断风险。",
        )
        self.assertEqual(ex["status"], "candidate")
        self.assertIn("验证", ex["chosen"])


if __name__ == "__main__":
    unittest.main()
