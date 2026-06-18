# Headless Mode

昼夜运行要求：
- 队列推进：只处理 ready 任务。
- 心跳：写入 runtime/state 与 dashboard。
- stop gate：连续失败、越权、缺少输出、成本超限时停止。
- 人工接管：blocked 状态明确写原因。

Dashboard 只监督，不承载会话。
