import tempfile
import unittest
from pathlib import Path

from cabinet_framework import project_harness as ph


class TestProjectHarnessV1(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.old = (ph.HARNESS_DIR, ph.PROJECTS_FILE, ph.ARTIFACTS_FILE, ph.GATE_EVENTS_FILE)
        base = Path(self.tmp.name) / "runtime" / "project_harness"
        ph.HARNESS_DIR = base
        ph.PROJECTS_FILE = base / "projects.json"
        ph.ARTIFACTS_FILE = base / "artifacts.jsonl"
        ph.GATE_EVENTS_FILE = base / "gate_events.jsonl"

    def tearDown(self):
        ph.HARNESS_DIR, ph.PROJECTS_FILE, ph.ARTIFACTS_FILE, ph.GATE_EVENTS_FILE = self.old
        self.tmp.cleanup()

    def test_gate_fails_without_required_artifact(self):
        project = ph.create_project("demo", "objective", ["done"])
        task = ph.create_harness_task(
            project_id=project["project_id"],
            title="delivery",
            objective="deliver docs",
            stage="delivery",
            worker="documentation_worker",
            acceptance_criteria=["docs exist"],
            required_artifact_types=["docs"],
        )
        gate = ph.run_stage_gate(task["task_id"])
        self.assertEqual(gate["status"], "fail")
        self.assertTrue(any("required artifact type missing" in m for m in gate["messages"]))

    def test_minimal_loop_passes_with_validated_artifact(self):
        project = ph.create_project("demo", "objective", ["done"])
        task = ph.create_harness_task(
            project_id=project["project_id"],
            title="delivery",
            objective="deliver docs",
            stage="delivery",
            worker="documentation_worker",
            acceptance_criteria=["docs exist"],
            required_artifact_types=["docs"],
        )
        artifact_file = Path(self.tmp.name) / "artifact.md"
        artifact_file.write_text("ok", encoding="utf-8")
        ph.register_artifact(
            project_id=project["project_id"],
            owner_task=task["task_id"],
            path=str(artifact_file),
            artifact_type="docs",
            status="validated",
            validation_result={"status": "pass"},
        )
        gate = ph.run_stage_gate(task["task_id"])
        self.assertEqual(gate["status"], "pass")
        self.assertEqual(ph.harness_status()["projects"], 1)
        self.assertEqual(ph.harness_status()["artifacts"], 1)

    def test_demo_loop_passes(self):
        result = ph.run_demo_loop()
        self.assertEqual(result["gate"]["status"], "pass")


if __name__ == "__main__":
    unittest.main()
