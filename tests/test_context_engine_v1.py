import tempfile
import unittest
from pathlib import Path

from cabinet_framework import project_harness as ph
from cabinet_framework import context_engine as ce
from cabinet_framework import worker_runtime as wr


class TestContextMemoryEngineV1(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        root = Path(self.tmp.name)
        base = root / "runtime" / "project_harness"
        self.old_ph = (ph.HARNESS_DIR, ph.PROJECTS_FILE, ph.ARTIFACTS_FILE, ph.GATE_EVENTS_FILE)
        self.old_ce = (ce.HARNESS_DIR, ce.CONTEXT_PACK_DIR, ce.GATE_EVENTS_FILE, ce.MEMORY_OBJECTS)
        self.old_wr = (wr.HARNESS_DIR, wr.PROMPTS_DIR, wr.EXECUTION_DIR, wr.SUBMISSIONS_DIR)
        ph.HARNESS_DIR = base
        ph.PROJECTS_FILE = base / "projects.json"
        ph.ARTIFACTS_FILE = base / "artifacts.jsonl"
        ph.GATE_EVENTS_FILE = base / "gate_events.jsonl"
        ce.HARNESS_DIR = base
        ce.CONTEXT_PACK_DIR = base / "context_packs"
        ce.GATE_EVENTS_FILE = ph.GATE_EVENTS_FILE
        ce.MEMORY_OBJECTS = root / "runtime" / "memory_objects.jsonl"
        wr.HARNESS_DIR = base
        wr.PROMPTS_DIR = base / "worker_prompts"
        wr.EXECUTION_DIR = base / "worker_execution"
        wr.SUBMISSIONS_DIR = base / "worker_submissions"

    def tearDown(self):
        ph.HARNESS_DIR, ph.PROJECTS_FILE, ph.ARTIFACTS_FILE, ph.GATE_EVENTS_FILE = self.old_ph
        ce.HARNESS_DIR, ce.CONTEXT_PACK_DIR, ce.GATE_EVENTS_FILE, ce.MEMORY_OBJECTS = self.old_ce
        wr.HARNESS_DIR, wr.PROMPTS_DIR, wr.EXECUTION_DIR, wr.SUBMISSIONS_DIR = self.old_wr
        self.tmp.cleanup()

    def _sample_task(self):
        project = ph.create_project("Context Demo", "验证 context pack", ["能召回记忆", "能写 context pack"])
        task = ph.create_harness_task(
            project_id=project["project_id"],
            title="完善 worker runtime context",
            objective="让 worker prompt 包含 context pack",
            stage="implementation",
            worker="context_worker",
            acceptance_criteria=["context pack exists"],
            required_artifact_types=["code"],
            allowed_paths=["docs/core"],
        )
        ph.add_decision(project["project_id"], "使用 context pack", "worker 需要结构化上下文", ["prompt 变长但可审计"])
        return project, task

    def test_context_pack_contains_project_task_decision_and_memory(self):
        project, task = self._sample_task()
        ce.register_task_memory(
            task_id=task["task_id"],
            title="worker runtime context lesson",
            content="worker runtime 必须使用 context pack 召回 gate history 和 artifact registry",
            tags=["worker", "context"],
        )
        pack = ce.build_context_pack(task["task_id"])
        self.assertEqual(pack["project"]["project_id"], project["project_id"])
        self.assertEqual(pack["task"]["task_id"], task["task_id"])
        self.assertEqual(len(pack["project_decisions"]), 1)
        self.assertGreaterEqual(len(pack["recalled_memory"]), 1)
        self.assertTrue((ce.CONTEXT_PACK_DIR / f"{task['task_id']}.json").exists())

    def test_worker_prompt_uses_context_pack(self):
        _, task = self._sample_task()
        result = wr.prepare_harness_worker(task["task_id"])
        prompt_text = Path(result["prompt_path"]).read_text(encoding="utf-8")
        self.assertIn("Context Pack", prompt_text)
        self.assertIn("context_pack_path", prompt_text)
        self.assertTrue((ce.CONTEXT_PACK_DIR / f"{task['task_id']}.json").exists())


if __name__ == "__main__":
    unittest.main()
