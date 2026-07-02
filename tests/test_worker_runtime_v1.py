import tempfile
import unittest
from pathlib import Path

from cabinet_framework import project_harness as ph
from cabinet_framework import worker_runtime as wr


class TestHarnessWorkerRuntime(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        base = Path(self.tmp.name) / "runtime" / "project_harness"
        self.old_ph = (ph.HARNESS_DIR, ph.PROJECTS_FILE, ph.ARTIFACTS_FILE, ph.GATE_EVENTS_FILE)
        ph.HARNESS_DIR = base
        ph.PROJECTS_FILE = base / "projects.json"
        ph.ARTIFACTS_FILE = base / "artifacts.jsonl"
        ph.GATE_EVENTS_FILE = base / "gate_events.jsonl"
        self.old_wr = (wr.PROMPTS_DIR, wr.EXECUTION_DIR, wr.SUBMISSIONS_DIR)
        wr.PROMPTS_DIR = base / "worker_prompts"
        wr.EXECUTION_DIR = base / "worker_execution"
        wr.SUBMISSIONS_DIR = base / "worker_submissions"

    def tearDown(self):
        ph.HARNESS_DIR, ph.PROJECTS_FILE, ph.ARTIFACTS_FILE, ph.GATE_EVENTS_FILE = self.old_ph
        wr.PROMPTS_DIR, wr.EXECUTION_DIR, wr.SUBMISSIONS_DIR = self.old_wr
        self.tmp.cleanup()

    def make_task(self, required_types=None):
        project = ph.create_project("worker-demo", "verify worker runtime", ["done"])
        task = ph.create_harness_task(
            project_id=project["project_id"],
            title="worker task",
            objective="prepare worker prompt",
            stage="delivery",
            worker="documentation_worker",
            acceptance_criteria=["artifact registered"],
            required_artifact_types=required_types or ["docs"],
        )
        return project, task

    def test_prepare_worker_registers_prompt_log_artifact(self):
        _, task = self.make_task(required_types=["logs"])
        result = wr.run_harness_worker(task["task_id"], mode="prompt")
        self.assertTrue(Path(result["prompt_path"]).exists())
        artifacts = ph.list_artifacts(owner_task=task["task_id"])
        self.assertEqual(len(artifacts), 1)
        self.assertEqual(artifacts[0]["type"], "logs")

    def test_submit_manifest_registers_worker_artifact_and_gate_passes(self):
        _, task = self.make_task(required_types=["docs"])
        output = Path(self.tmp.name) / "result.md"
        output.write_text("# result", encoding="utf-8")
        manifest = Path(self.tmp.name) / "manifest.json"
        manifest.write_text(
            '{"task_id":"%s","status":"done","artifacts":[{"path":"%s","type":"docs","status":"validated","validation_result":{"status":"pass","message":"ok"}}]}'
            % (task["task_id"], str(output)),
            encoding="utf-8",
        )
        submitted = wr.submit_worker_manifest(str(manifest))
        self.assertEqual(submitted["status"], "done")
        gate = ph.run_stage_gate(task["task_id"])
        self.assertEqual(gate["status"], "pass")

    def test_run_and_gate_fails_until_domain_artifact_submitted(self):
        _, task = self.make_task(required_types=["docs"])
        result = wr.run_worker_and_gate(task["task_id"], mode="local-report")
        self.assertEqual(result["gate"]["status"], "fail")
        self.assertTrue(any("required artifact type missing: docs" in m for m in result["gate"]["messages"]))


if __name__ == "__main__":
    unittest.main()
