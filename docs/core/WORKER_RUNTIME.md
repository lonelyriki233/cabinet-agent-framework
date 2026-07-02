# Worker Runtime

CAF v1.0 中 worker 的标准协议已经接入 `HarnessTask`。

实现位置：

```text
cabinet_framework/worker_runtime.py
```

## 协议

1. 接收 HarnessTask。
2. 读取 allowed_paths 生成安全上下文摘要。
3. 生成 worker prompt。
4. 将 prompt 登记为 logs artifact。
5. worker 执行后提交 JSON manifest。
6. manifest 中的产物进入 Artifact Registry。
7. Gate System 根据 Artifact Registry 判定 PASS/FAIL。

## Worker Manifest

```json
{
  "task_id": "HT-...",
  "status": "done|blocked|failed",
  "artifacts": [
    {
      "path": "path/to/file.md",
      "type": "docs|code|tests|design|logs|config|decision|review|rollback|other",
      "status": "ready|validated",
      "validation_result": {"status": "pass|fail|unknown", "message": "..."}
    }
  ],
  "blockers": [],
  "notes": "..."
}
```

## CLI

```bash
python3 -m cabinet_framework.cli harness-run --task-id <T> --mode prompt
python3 -m cabinet_framework.cli harness-run --task-id <T> --mode local-report
python3 -m cabinet_framework.cli harness-submit --manifest manifest.json
python3 -m cabinet_framework.cli harness-run-gate --task-id <T> --mode local-report
```

## 注意

`local-report` 只验证 Worker Runtime 管道，不伪造领域产物。若任务要求 docs/code/tests 等领域产物，仍需 worker 提交 manifest 后才能通过 gate。
