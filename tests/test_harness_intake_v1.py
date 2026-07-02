import tempfile
import unittest
from pathlib import Path

from cabinet_framework import project_harness as ph
from cabinet_framework import harness_intake as hi


class TestHarnessIntakeV1(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        base = Path(self.tmp.name) / "runtime" / "project_harness"
        self.old_ph = (ph.HARNESS_DIR, ph.PROJECTS_FILE, ph.ARTIFACTS_FILE, ph.GATE_EVENTS_FILE)
        ph.HARNESS_DIR = base
        ph.PROJECTS_FILE = base / "projects.json"
        ph.ARTIFACTS_FILE = base / "artifacts.jsonl"
        ph.GATE_EVENTS_FILE = base / "gate_events.jsonl"

    def tearDown(self):
        ph.HARNESS_DIR, ph.PROJECTS_FILE, ph.ARTIFACTS_FILE, ph.GATE_EVENTS_FILE = self.old_ph
        self.tmp.cleanup()

    def test_request_to_harness_creates_project_and_harness_tasks(self):
        result = hi.request_to_harness(
            "完善 CAF worker runtime 和 gate 闭环",
            authority="L2",
            source="unit_test",
            persist_runtime_tasks=False,
        )
        self.assertIsNotNone(result["project"])
        self.assertGreaterEqual(len(result["harness_tasks"]), 1)
        task = result["harness_tasks"][0]
        self.assertEqual(task["project_id"], result["project"]["project_id"])
        self.assertEqual(task["source"], "unit_test")
        self.assertTrue(task["required_artifact_types"])

    def test_harness_tasks_are_visible_in_registry(self):
        result = hi.request_to_harness("写一个 docs 说明", persist_runtime_tasks=False)
        tasks = ph.list_harness_tasks(result["project"]["project_id"])
        self.assertEqual(len(tasks), len(result["harness_tasks"]))


if __name__ == "__main__":
    unittest.main()
