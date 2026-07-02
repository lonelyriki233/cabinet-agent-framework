# Project Harness Core

CAF v1.0 的核心定位是 Agent Project Harness：管理复杂项目从需求到交付的运行闭环。

## 核心对象

- Project：项目级目标、模块、里程碑、风险、决策、验收标准。
- HarnessTask：项目内可执行任务，绑定 stage、worker、依赖、验收标准、必需产物。
- Artifact：任务产物登记记录，包含路径、类型、owner task、hash、验证结果。
- GateResult：阶段门禁审查结果。

## 最小闭环

```text
需求输入
→ 创建 Project
→ 创建 HarnessTask
→ Worker 产出 Artifact
→ Artifact Registry 登记
→ Stage Gate 审查
→ PASS 后进入交付/归档
```

## CLI

```bash
python3 -m cabinet_framework.cli harness-project --name "项目" --objective "目标" --acceptance "验收"
python3 -m cabinet_framework.cli harness-task --project-id <P> --title "任务" --objective "目标" --stage delivery --worker documentation_worker --acceptance "验收" --required-type docs
python3 -m cabinet_framework.cli harness-artifact --project-id <P> --task-id <T> --path <file> --type docs --status validated --validation-status pass
python3 -m cabinet_framework.cli harness-gate --task-id <T>
python3 -m cabinet_framework.cli harness-demo
```

## 文件位置

```text
runtime/project_harness/projects.json
runtime/project_harness/tasks/*.json
runtime/project_harness/artifacts.jsonl
runtime/project_harness/gate_events.jsonl
```
