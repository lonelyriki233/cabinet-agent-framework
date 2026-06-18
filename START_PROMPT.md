# Start Prompt

你正在 Cabinet Agent Framework 项目中工作。

先判断请求属于：strategy、memory、thinking_skill、worker_skill、context_unit、hooks、mcp_rag、headless、sdk_adapter、dashboard、domain_template、docs、research。

原则：
1. 宿主无关优先：不要把 Hermes-only 机制写成框架必需能力。
2. 标注来源：Hermes 机制必须写清 Hermes-native / portable abstraction / adapter implementation。
3. thinking skill 与 worker skill 分离。
4. 记忆按内阁-六部归档。
5. 所有扩展点尊重后来者智慧，不写死唯一模型、唯一工具、唯一领域。
6. 真实验证优先，不报告未运行结果。
