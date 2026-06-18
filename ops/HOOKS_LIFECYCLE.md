# Hooks Lifecycle

生命周期：task.created -> task.before_run -> task.after_run -> archive.before_index -> archive.after_index -> audit.written -> dispatcher.stop_gate。

所有 hook 需要机器可读日志，不能只写政策文档。
