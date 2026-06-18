# Portable Worker Contract

输入：task_packet.json + role.md + allowed_paths。

步骤：
1. 读任务包。
2. 只在 allowed_paths 写文件。
3. 产出 required_outputs。
4. 按 acceptance_criteria 自检。
5. 写 self_critique 和 blockers。

输出：Markdown 或 JSON，必须可被其他宿主读取。
