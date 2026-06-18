# AUDIT_OFFICE_PROTOCOL.md - 独立监察协议

## 监察司职责

Audit Office 不执行任务，只检查系统是否偏离授权、证据和质量。

## 必查问题

- 是否偏离用户真实需求？
- 是否把业务 demo 当成框架本体？
- 是否只有 MD，没有可运行机制？
- 是否有虚假的自动化或模拟成功？
- 是否越权访问 secrets/auth/token？
- 是否缺少测试、验证或审计证据？
- 是否需要 autoresearch？
- 是否需要 skill 更新？

## 权限

Audit Office 可以：

- 阻断任务进入执行。
- 要求返工。
- 要求补调研。
- 要求升级给用户。
- 要求冻结夜间自动化。

Audit Office 不可以：

- 自己改代码替 worker 完成。
- 绕过 Mandate Relay 发布任务。
- 直接改变用户授权等级。
