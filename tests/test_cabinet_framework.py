import json
import unittest

from cabinet_framework.conversation_bridge import register_conversation_request
from cabinet_framework.dashboard import _state_data, app
from cabinet_framework.worker import build_worker_prompt


def call_app(path):
    captured = {}
    def start_response(status, headers):
        captured['status'] = status
        captured['headers'] = headers
    body = b''.join(app({'PATH_INFO': path, 'QUERY_STRING': ''}, start_response)).decode('utf-8')
    return captured['status'], body


class TestCabinetFramework(unittest.TestCase):
    def test_full_framework_request_decomposes(self):
        result = register_conversation_request(
            '建设跨 Hermes/Codex/Claude Code/OpenClaw 的 agent 框架，包含记忆、skills、上下文、hooks、MCP、headless、SDK、dashboard、子工程模板',
            authority='L2', source='test'
        )
        self.assertGreaterEqual(len(result['created_tasks']), 10)
        workers = {t['worker'] for t in result['created_tasks']}
        self.assertIn('memory_steward_worker', workers)
        self.assertIn('thinking_skill_curator_worker', workers)
        self.assertIn('worker_skill_builder_worker', workers)
        self.assertIn('sdk_adapter_worker', workers)
        self.assertIn('dashboard_worker', workers)

    def test_state_exposes_core_sections(self):
        data = _state_data()
        self.assertEqual(data['framework_identity']['name'], 'Cabinet Agent Framework')
        content = data['module_content']
        for key in ['memory','skills-core','skills-worker','context-units','hooks-runtime','mcp-rag','headless','sdk-adapters','templates']:
            self.assertIn(key, content)
        self.assertGreaterEqual(content['memory']['file_count'], 7)
        self.assertGreaterEqual(content['skills-core']['file_count'], 3)

    def test_dashboard_routes_and_content_api(self):
        for path in ['/overview','/memory','/skills-core','/skills-worker','/context-units','/hooks-runtime','/mcp-rag','/headless','/sdk-adapters','/templates','/agents']:
            status, body = call_app(path)
            self.assertTrue(status.startswith('200'), (path, status))
            self.assertIn('Cabinet Agent Framework', body)
        status, body = call_app('/api/content')
        self.assertTrue(status.startswith('200'))
        self.assertIn('skills-core', json.loads(body))

    def test_worker_prompt_enforces_portability_and_attribution(self):
        task = {
            'task_id':'T-test', 'worker':'sdk_adapter_worker', 'task_type':'sdk_adapter',
            'objective':'设计 Hermes/Codex/Claude Code/OpenClaw 适配层', 'context':'兼容性要求',
            'allowed_paths':['adapters/'], 'forbidden_paths':['.env'],
            'acceptance_criteria':['区分宿主'], 'required_outputs':['runtime/outputs/T-test.md']
        }
        prompt = build_worker_prompt(task)
        self.assertIn('Hermes 机制可以借鉴/适配，但必须标注来源', prompt)
        self.assertIn('thinking skill', prompt)
        self.assertIn('内阁-六部', prompt)


if __name__ == '__main__':
    unittest.main()
