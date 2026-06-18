import json
import subprocess
import sys
import unittest
from pathlib import Path

from cabinet_framework.adapters import adapter_names, get_adapter
from cabinet_framework.sdk import SDKTaskPacket, TaskStore, WorkerRegistry, load_markdown_skill

ROOT = Path(__file__).resolve().parents[1]


class TestPhase2Portability(unittest.TestCase):
    def test_adapter_registry_covers_target_hosts(self):
        names = set(adapter_names())
        for name in ['hermes', 'codex', 'claude-code', 'openclaw', 'generic-cli']:
            self.assertIn(name, names)
        self.assertIn('Hermes-native', get_adapter('hermes').notes)

    def test_sdk_task_store_round_trip(self):
        store = TaskStore(ROOT)
        packet = SDKTaskPacket(
            task_id='T-sdk-test', task_type='sdk_adapter', worker='sdk_adapter_worker',
            objective='round trip', context='unit test', allowed_paths=['runtime/outputs/'],
            forbidden_paths=['.env'], acceptance_criteria=['readable'],
            required_outputs=['runtime/outputs/T-sdk-test.md'], gates=['schema_gate']
        )
        path = store.write(packet)
        self.assertTrue(path.exists())
        data = store.read('T-sdk-test')
        self.assertEqual(data['worker'], 'sdk_adapter_worker')
        path.unlink()

    def test_worker_registry_and_skill_loader(self):
        registry = WorkerRegistry()
        registry.register('demo_worker', bureau='works_ministry', description='demo')
        self.assertEqual(registry.get('demo_worker')['bureau'], 'works_ministry')
        skill = load_markdown_skill(ROOT / 'skills/worker/portable-worker-contract.md')
        self.assertIn('输入', skill['body'])

    def test_required_phase2_files_exist(self):
        required = [
            'adapters/hermes.md', 'adapters/codex.md', 'adapters/claude-code.md', 'adapters/openclaw.md',
            'context_units/templates/role.md', 'context_units/templates/handoff.md',
            'mcp/vector_index_schema.json', 'headless/runner.example.json',
            'templates/data_platform/README.md', 'templates/story_world/README.md',
            'docs/presentation/GITHUB_READY_CHECKLIST.md',
        ]
        for rel in required:
            self.assertTrue((ROOT / rel).exists(), rel)

    def test_keyword_index_script_runs(self):
        result = subprocess.run(
            [sys.executable, 'scripts/build_keyword_index.py'], cwd=ROOT,
            text=True, capture_output=True, timeout=60
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        out = ROOT / 'runtime/rag/keyword_index.jsonl'
        self.assertTrue(out.exists())
        first = json.loads(out.read_text(encoding='utf-8').splitlines()[0])
        self.assertIn('path', first)


if __name__ == '__main__':
    unittest.main()
