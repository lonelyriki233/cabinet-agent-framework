# SELF_ITERATION_PROTOCOL.md - 自我迭代协议

## 目的

让框架越用越强，而不是每次从零解释。

## 触发条件

- 同类错误重复出现。
- worker 发现稳定流程。
- hooks/checks 发现常见漏项。
- 中书反复补充同类上下文。
- 领袖发现用户多次纠正同类问题。

## 流程

1. worker 在更新日志中提出 skill_update_request。
2. 中书收集并合并同类请求。
3. harness_worker 写 skill 草案或协议补丁。
4. 领袖判断是否进入长期框架。
5. 下次任务加载新 skill。
6. 中书观察错误是否减少。

## 禁止

- 把一次性任务日志写成 skill。
- 把用户临时偏好写成永久硬规则。
- 没有验证方式的 skill 不进入长期框架。
