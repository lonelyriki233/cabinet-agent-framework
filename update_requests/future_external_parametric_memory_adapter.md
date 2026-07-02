# CAF 远期设想：外置专业参数化记忆适配器

时间：2026-06-29
状态：只归档，不进入当前实现计划

## 设想来源

当前使用的大模型是付费在线 AI 资源，中间层不可见，不能直接插入传统意义上的模型内部 adapter。

因此这里讨论的不是：

```text
LLM hidden state adapter
```

而是一个外置于大模型 API 之外、接入 agent 工程流程的专业知识参数化记忆组件。

## 暂定名称

```text
External Parametric Memory Adapter
外置专业参数化记忆适配器
```

也可以称为：

```text
Domain Memory Sidecar
Professional Knowledge Adapter
```

## 核心想法

流程不是修改大模型内部，而是：

```text
付费在线大模型 API
→ CAF/agent 工程约束其输出结构化内容
→ 结构化输出进入外置专业知识 adapter
→ adapter 做专业校验、补强、规范化、风险判断
→ 结果反馈给 CAF gate / rework / artifact 流程
```

## 它不是 Prompt

Prompt 是临时上下文注入。

这个设想希望形成更稳定的专业知识能力：

- 使用结构化运行轨迹
- 使用专业规则和案例
- 可能使用小模型 / adapter / ranker / judge
- 输出可审计 verdict
- 接入 CAF gate

## 可能位置

未来可放在 CAF 流程中：

```text
Worker Output
→ Artifact Candidate
→ External Parametric Memory Adapter
→ Domain Verdict
→ Gate System
→ Pass / Rework
```

## 可能输入

```text
request
project context
task context
worker output
artifact candidate
gate history
memory objects
domain rules
domain cases
human feedback
```

## 可能输出

```json
{
  "status": "pass | warn | fail",
  "domain": "software | industrial | retail | robotics_vla | other",
  "score": 0.0,
  "missing_knowledge": [],
  "violated_rules": [],
  "recommended_rework": [],
  "enriched_output": {},
  "evidence": []
}
```

## 适用价值

它可能用于弥补在线大模型在专业领域里的不足：

- 专业术语不稳定
- 行业规则漏掉
- 输出格式不统一
- 专业判断浅
- 幻觉检测
- 案例经验复用
- 低成本二次审查
- 领域风格统一
- 领域知识压缩

## 可行路线

不直接从训练开始，而是分层推进：

### 1. 规则 + Schema Adapter

- JSON schema
- domain rules
- threshold checks
- forbidden action checks

### 2. 检索式专业记忆

- MemoryObject
- domain cases
- artifact history
- gate failure history
- vector / keyword recall

### 3. 小模型 Judge / Ranker

小模型不负责长文本生成，只负责：

- 专业评分
- 风险判断
- 缺漏识别
- rework 建议

### 4. 小模型 Rewrite / Normalizer

用于：

- 专业术语规范化
- 领域格式重写
- 约束补全

### 5. 参数化 Adapter / LoRA

在 CAF 产生足够高质量轨迹后，再考虑训练。

## 与 CAF 的关系

这个设想依赖 CAF 先成型。

CAF 必须先稳定产生：

```text
task
worker output
artifact
gate result
rework history
human feedback
final accepted artifact
```

这些才是未来训练/构建专业 adapter 的数据基础。

## 当前决策

现在不做。

当前 CAF 优先级仍然是：

```text
1. Gate / Hook / Lifecycle 合并
2. Blocker / Rework 自动返工闭环
3. Archive / Learning 自动沉淀
4. 真实 Agent Worker Lane
5. Tool / MCP Contract 加硬
```

本文件只作为远期架构备忘，避免当前开发偏离 CAF v1.0 主线。
