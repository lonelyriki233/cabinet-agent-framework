import tempfile
import unittest
from pathlib import Path

from cabinet_framework import project_harness as ph
from cabinet_framework import lifecycle_gate as lg
from cabinet_framework import context_engine as ce


class TestLifecycleGateV1(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        root = Path(self.tmp.name)
        base = root / "runtime" / "project_harness"
        self.old_ph = (ph.HARNESS_DIR, ph.PROJECTS_FILE, ph.ARTIFACTS_FILE, ph.GATE_EVENTS_FILE, ph.ROOT)
        self.old_lg = (lg.HARNESS_DIR, lg.BLOCKERS_FILE, lg.TRANSITIONS_FILE, lg.emit_hook)
        self.old_ce = ce.MEMORY_OBJECTS
        ph.ROOT = root
        ph.HARNESS_DIR = base
        ph.PROJECTS_FILE = base / "projects.json"
        ph.ARTIFACTS_FILE = base / "artifacts.jsonl"
        ph.GATE_EVENTS_FILE = base / "gate_events.jsonl"
        lg.HARNESS_DIR = base
        lg.BLOCKERS_FILE = base / "blockers.jsonl"
        lg.TRANSITIONS_FILE = base / "stage_transitions.jsonl"
        lg.emit_hook = lambda *args, **kwargs: {"event": args[0] if args else "test"}
        ce.MEMORY_OBJECTS = root / "runtime" / "memory_objects.jsonl"

    def tearDown(self):
        ph.HARNESS_DIR, ph.PROJECTS_FILE, ph.ARTIFACTS_FILE, ph.GATE_EVENTS_FILE, ph.ROOT = self.old_ph
        lg.HARNESS_DIR, lg.BLOCKERS_FILE, lg.TRANSITIONS_FILE, lg.emit_hook = self.old_lg
        ce.MEMORY_OBJECTS = self.old_ce
        self.tmp.cleanup()

    def _task(self):
        project = ph.create_project("Lifecycle Gate Demo", "验证 stage gate 生命周期", ["gate controls transition"])
        task = ph.create_harness_task(
            project_id=project["project_id"],
            title="实现 lifecycle gate",
            objective="只有 gate pass 才允许推进阶段",
            stage="implementation",
            worker="framework_worker",
            acceptance_criteria=["gate pass advances", "gate fail creates blocker"],
            required_artifact_types=["code"],
            allowed_paths=["outputs"],
        )
        return project, task

    def test_gate_fail_blocks_transition_and_creates_rework_task(self):
        _, task = self._task()
        result = lg.advance_task_stage(task["task_id"], target_stage="test")
        self.assertEqual(result["status"], "blocked")
        self.assertEqual(result["task"]["status"], "blocked")
        self.assertEqual(result["gate"]["status"], "fail")
        self.assertIsNotNone(result["blocker"]["blocker_id"])
        self.assertIsNotNone(result["rework_task"]["task_id"])
        self.assertEqual(result["rework_task"]["source"], "lifecycle_gate_rework")
        self.assertEqual(lg.get_task(task["task_id"])["stage"], "implementation")
        blockers = lg.list_blockers(task_id=task["task_id"])
        self.assertGreaterEqual(len(blockers), 1)

    def test_gate_pass_advances_stage(self):
        _, task = self._task()
        artifact_path = Path(ph.ROOT) / "outputs" / "impl.py"
        artifact_path.parent.mkdir(parents=True, exist_ok=True)
        artifact_path.write_text("print('ok')\n", encoding="utf-8")
        ph.register_artifact(
            project_id=task["project_id"],
            owner_task=task["task_id"],
            path=str(artifact_path),
            artifact_type="code",
            status="validated",
            validation_result={"status": "pass", "message": "test artifact"},
        )
        result = lg.advance_task_stage(task["task_id"], target_stage="test")
        self.assertEqual(result["status"], "advanced")
        self.assertEqual(result["gate"]["status"], "pass")
        updated = lg.get_task(task["task_id"])
        self.assertEqual(updated["stage"], "test")
        self.assertEqual(updated["status"], "ready")
        self.assertEqual(result["transition"]["status"], "advanced")

    def test_rework_pass_auto_resolves_blocker_and_records_memory(self):
        _, task = self._task()
        blocked = lg.advance_task_stage(task["task_id"], target_stage="test")
        self.assertEqual(blocked["status"], "blocked")
        blocker_id = blocked["blocker"]["blocker_id"]
        rework = blocked["rework_task"]

        rework_artifact = Path(ph.ROOT) / "outputs" / "rework_impl.py"
        rework_artifact.parent.mkdir(parents=True, exist_ok=True)
        rework_artifact.write_text("print('reworked')\n", encoding="utf-8")
        ph.register_artifact(
            project_id=rework["project_id"],
            owner_task=rework["task_id"],
            path=str(rework_artifact),
            artifact_type="code",
            status="validated",
            validation_result={"status": "pass", "message": "rework artifact"},
        )

        advanced = lg.advance_task_stage(rework["task_id"], target_stage="test")
        self.assertEqual(advanced["status"], "advanced")
        self.assertEqual(len(advanced["resolved_blockers"]), 1)
        self.assertEqual(advanced["resolved_blockers"][0]["blocker_id"], blocker_id)
        self.assertEqual(lg.list_blockers(task_id=task["task_id"])[0]["status"], "resolved")
        self.assertEqual(lg.get_task(task["task_id"])["status"], "ready")

        memories = ce.read_memory_objects(ce.MEMORY_OBJECTS)
        titles = [m.get("title", "") for m in memories]
        self.assertTrue(any("Gate failure" in t for t in titles))
        self.assertTrue(any("Resolved blocker" in t for t in titles))


if __name__ == "__main__":
    unittest.main()
