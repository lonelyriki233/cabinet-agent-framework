"""Tests for SkillForge and Autonomous Worker modules."""

import unittest, json, tempfile, os, shutil
from pathlib import Path


class TestSkillForge(unittest.TestCase):
    def setUp(self):
        from cabinet_framework import model
        # Subclass to override paths
        model.ROOT = Path(tempfile.mkdtemp())
        model.RUNTIME = model.ROOT / "runtime"
        model.TASKS = model.RUNTIME / "tasks"
        model.OUTPUTS = model.RUNTIME / "outputs"
        model.STATE = model.RUNTIME / "state"
        model.SKILLS = model.ROOT / "skills"
        model.MEMORY = model.ROOT / "memory"
        for d in [model.RUNTIME, model.TASKS, model.STATE]:
            d.mkdir(parents=True, exist_ok=True)
        self.model = model

    def tearDown(self):
        shutil.rmtree(self.model.ROOT, ignore_errors=True)

    def test_skill_forge_creates_skill(self):
        from cabinet_framework.skill_forge import SkillForge, list_all_skills
        forge = SkillForge()
        result = forge.forge_skill(
            worker_name="test_worker",
            task_type="music",
            task_title="Chinese-style song",
            request="写一首中国风歌曲"
        )
        self.assertIn("skill_name", result)
        self.assertIn("skill_path", result)
        # File must exist (may be existing or fresh)
        path = Path(result["skill_path"])
        self.assertTrue(path.exists())
        # Verify content has expected structure
        content = path.read_text(encoding="utf-8")
        self.assertIn("version: 1.0.0", content)
        self.assertIn("Auto-forged", content)

    def test_list_skills_empty_before_forge(self):
        from cabinet_framework.skill_forge import list_all_skills
        skills = list_all_skills()
        # No skills forged in fresh state
        forged = [s for s in skills if s.get("forge_version", 0) > 0]
        self.assertEqual(len(forged), 0)

    def test_skill_discovery_needed_true_when_no_skills(self):
        from cabinet_framework.skill_forge import skill_discovery_needed
        self.assertTrue(skill_discovery_needed("my_worker", "planning", "Plan project", "规划一个新项目"))

    def test_skill_discovery_needed_after_creation(self):
        from cabinet_framework.skill_forge import SkillForge, skill_discovery_needed
        forge = SkillForge()
        forge.forge_skill("test_worker", "music", "Test", "写歌")
        # Same type should not need discovery
        self.assertFalse(skill_discovery_needed("test_worker", "music", "Another song", "再写一首歌"))


class TestAutonomousWorker(unittest.TestCase):
    def setUp(self):
        from cabinet_framework import model
        model.ROOT = Path(tempfile.mkdtemp())
        model.RUNTIME = model.ROOT / "runtime"
        model.TASKS = model.RUNTIME / "tasks"
        model.OUTPUTS = model.RUNTIME / "outputs"
        model.REPORTS = model.RUNTIME / "reports"
        model.LOGS = model.RUNTIME / "logs"
        model.STATE = model.RUNTIME / "state"
        model.SKILLS = model.ROOT / "skills"
        model.MEMORY = model.ROOT / "memory"
        model.PROJECTS = model.ROOT / "projects"
        for d in [model.RUNTIME, model.TASKS, model.STATE, model.SKILLS / "worker", model.MEMORY, model.PROJECTS]:
            d.mkdir(parents=True, exist_ok=True)
        self.model = model

    def tearDown(self):
        shutil.rmtree(self.model.ROOT, ignore_errors=True)

    def test_get_autonomous_status(self):
        from cabinet_framework.autonomous_worker import get_autonomous_status
        status = get_autonomous_status()
        self.assertIn("config", status)
        self.assertIn("auto_dispatch", status)
        self.assertIn("installed_worker_skills", status)

    def test_auto_intake_creates_task_and_maybe_skill(self):
        from cabinet_framework.autonomous_worker import auto_intake
        result = auto_intake("测试任务：做一个简单的Python脚本", authority="L2", source="test")
        self.assertIsNotNone(result)
        # Should have stages
        self.assertGreater(len(result.get("stages", [])), 0)
        # Should not error
        self.assertIsNone(result.get("error"))
