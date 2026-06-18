# Work Example - 演示用工作流

你可以自己启动，不需要我现在启动。

## 目标

演示一个复杂需求如何经过框架变成可执行 worker 任务。

## 进入目录

```bash
cd <repo-root>
```

## 1. 初始化

```bash
python3 -m cabinet_framework.cli init
```

预期：

```text
afh init: PASS
```

## 2. 输入复杂需求

```bash
python3 -m cabinet_framework.cli intake --authority L2 --request "为高性能数据分析平台设计一个百万级图表渲染能力，需要自动调研技术选型、实现降采样策略、设计 benchmark、补充质量 gate，并给出面试展示证据"
```

你应该看到：

- Leader Gateway 判断任务类型和 worker。
- Strategy Council 启动多视角拟议。
- Mandate Relay 判断 L2 可以低风险推进。
- Chief Coordinator 生成任务包。
- 如果存在不确定性，会先插入 autoresearch 任务。

## 3. 查看任务队列

```bash
python3 -m cabinet_framework.cli tasks
```

## 4. 生成 worker prompt，不启动真实 worker

```bash
python3 -m cabinet_framework.cli tick --mode prompt
```

它会在 `runtime/logs/` 生成 worker prompt。

## 5. 查看真实 Hermes worker 命令

先从 `tasks` 输出中复制一个任务 JSON 路径，例如：

```bash
python3 -m cabinet_framework.cli command --task runtime/tasks/<TASK_ID>.json
```

这会打印真实 Hermes 命令，例如：

```bash
hermes chat --quiet --max-turns 50 -t web,file,terminal -s agent-harness-engineering -q '<worker prompt>'
```

这一步证明：框架不是只能写 MD，而是能把任务交给 Hermes worker。

## 6. 如果你要真实启动 worker

```bash
python3 -m cabinet_framework.cli tick --mode hermes
```

注意：这会真的调用 Hermes worker，让它按任务包工作。

## 7. 运行 gate

```bash
python3 -m cabinet_framework.cli gate
```

## 8. 运行测试

```bash
python3 -m unittest discover -s tests -v
```

## 这个例子证明什么

- 用户需求不是直接扔给一个 worker。
- 框架会先判断、参议、审权、分派。
- autoresearch 会在不确定任务前启动。
- worker 有 allowed_paths / forbidden_paths / acceptance criteria。
- Hermes 是真实执行底座。
- gate 和 tests 是停止条件。
- L2/L3 授权后可以支持自动化/挂机开发。
