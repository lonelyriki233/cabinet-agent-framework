# WORKER_REGISTRY.md - Worker 按内容划分

| Worker | 长期负责内容 | 典型任务 |
|---|---|---|
| frontend_worker | 前端页面、交互、图表展示、前端性能 | 页面实现、图表接入、交互 bug、前端维护 |
| backend_worker | API、服务端、数据接口、缓存、错误处理 | 接口实现、fallback、鉴权、后端 bug |
| data_perf_worker | 大数据处理、降采样、性能预算、benchmark | 百万点处理、性能瓶颈、图表数据策略 |
| research_worker | 技术调研、方案比较、资料归纳 | 框架选型、业界方案、工程取舍报告 |
| harness_worker | agent 框架、skills、hooks、MCP、检查协议 | 设计约束、检查机制、夜间流程、上下文治理 |
| doc_evidence_worker | 交付说明、交付说明材料、展示路线 | 外部审查 playbook、问答、材料组织 |

## 划分原则

同一个内容领域的开发、维护、bugfix 尽量由同一个 worker 负责，保证长期责任和上下文连续。
