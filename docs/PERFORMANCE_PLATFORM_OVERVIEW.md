# 8790 端口页面说明：高性能数据分析平台

## 页面入口

本页面运行在本地 8790 端口：

```text
http://127.0.0.1:8790/
```

启动命令：

```bash
python3 -m cabinet_framework.cli perf-platform --port 8790
```

对应文件：

```text
cabinet_framework/perf_platform.py        后端服务、数据生成、采样、API
web/templates/perf_platform.html        前端页面、轮询、Canvas 渲染
tests/test_perf_platform.py             接口与采样测试
```

## 页面定位

8790 页面是一个高性能数据分析平台的本地原型页面。它用于展示平台在以下场景中的处理能力：

- 大量性能指标展示
- 实时数据刷新
- 多维度指标对比
- 百万级数据曲线渲染
- 接口不稳定时的前端容错
- AI 生成代码后的接口稳定性测试

当前页面使用后端模拟数据，不连接真实生产数据库。它展示的是平台的核心技术路径：后端生成和压缩数据，前端高效展示数据，并在接口失败时保持页面可用。

## 页面整体结构

页面由以下区域组成：

1. 平台标题与能力标签
2. 轮询状态
3. 四个实时指标卡片
4. 百万级数据渲染图
5. 多维度性能指标表
6. 前端性能与图表策略说明
7. 性能预算与稳定性检查表
8. API / 数据结构展示区

## 1. 平台标题与能力标签

页面顶部展示平台名称：

```text
高性能数据分析平台
```

标题下方展示平台能力标签，包括：

- 大量性能指标展示
- 实时数据变化轮询
- 多维度图表对比
- 百万级数据渲染采样
- 接口不稳定时的退避与 fallback
- AI 生成代码后的 contract / smoke 稳定性检查

这些内容来自后端接口：

```text
GET /api/overview
```

后端生成位置：

```text
cabinet_framework/perf_platform.py -> overview_payload()
```

## 2. 轮询状态

页面右上角的“轮询状态”区域展示前端实时请求后端接口的状态。

前端持续请求：

```text
GET /api/live?failure_rate=0.12
```

其中 `failure_rate=0.12` 表示后端有约 12% 概率模拟接口失败。这个设计用于展示接口不稳定时页面如何处理。

前端处理策略：

- 请求成功：刷新页面上的实时指标和多维度表格。
- 请求失败：保留上一次成功返回的数据，不清空页面。
- 连续失败：轮询间隔指数退避，减少无效请求。
- 接口恢复：恢复正常刷新节奏。

相关前端逻辑：

```text
web/templates/perf_platform.html -> poll()
```

## 3. 实时指标卡片

页面上方有四个实时指标卡片：

| 指标 | 含义 | 数据来源 |
|---|---|---|
| 活跃用户 | 模拟当前平台观测到的用户规模 | `/api/live` |
| 写入行/秒 | 模拟数据摄入吞吐量 | `/api/live` |
| API 成功率 | 模拟接口整体成功率 | `/api/live` |
| 前端 FPS | 模拟当前前端渲染帧率 | `/api/live` |

这些指标由后端函数生成：

```text
cabinet_framework/perf_platform.py -> live_metrics()
```

这些数据会随时间变化，用于展示平台的实时刷新能力。

## 4. 百万级数据渲染图

页面中部的“百万级数据渲染结果”是当前页面的核心展示区域。

默认参数：

```text
Raw points: 1000000
Canvas width: 1600
```

前端请求：

```text
GET /api/dense-series?points=1000000&width=1600
```

后端会生成 1,000,000 个原始数据点，但不会把这 1,000,000 个点全部交给浏览器绘制。后端会先进行采样，再把采样结果返回给前端。

当前页面实际展示结果类似：

```text
1,000,000 raw -> 3,200 sampled
```

含义是：

- 后端生成了 1,000,000 个原始点。
- 后端根据 1600 像素画布宽度进行分桶。
- 每个桶保留最小值和最大值。
- 最终返回约 3,200 个采样点。
- 前端使用 Canvas 绘制这 3,200 个点。

后端采样函数：

```text
cabinet_framework/perf_platform.py -> minmax_bucket_sample()
```

前端绘图函数：

```text
web/templates/perf_platform.html -> drawSeries()
```

## 5. 原始数据如何生成

百万级数据点由后端函数生成：

```text
cabinet_framework/perf_platform.py -> generate_point(i, seed)
```

每个点是一个二维点：

```json
[x, y]
```

其中：

- `x` 是点序号。
- `y` 是模拟性能指标值。

`y` 值由以下部分组成：

| 组成 | 作用 |
|---|---|
| baseline | 模拟长期基础趋势 |
| seasonal | 模拟周期性波动 |
| spike | 模拟偶发性能尖峰 |
| micro | 模拟细小噪声 |

生成逻辑使曲线具备趋势、周期、尖峰和噪声，更接近真实性能指标曲线，而不是一条简单随机线。

## 6. 采样运算

当前页面使用的核心运算是：

```text
min/max bucket sampling
```

即按桶保留最大值和最小值的采样。

以默认参数为例：

```text
原始点数：1,000,000
画布宽度：1,600
桶数量：约 1,600
每桶点数：约 625
每桶输出：最小值点 + 最大值点
最终点数：约 3,200
```

这种采样方式的目的：

1. 减少浏览器需要绘制的数据点数量。
2. 保留性能尖峰，避免异常被平均值抹平。
3. 让百万级曲线能在浏览器中快速展示。
4. 避免创建大量 DOM 或 SVG 节点。

当前页面使用 Canvas 绘图，不使用 SVG 绘制百万点。

## 7. 多维度性能指标表

页面右侧的“多维度性能指标”表格展示不同维度下的性能数据。

当前维度包括：

- 华东
- 华北
- 华南
- 海外
- 移动端
- 桌面端

每个维度展示：

| 字段 | 含义 |
|---|---|
| QPS | 模拟每秒请求量 |
| P95 | 模拟 P95 响应延迟 |
| 错误率 | 模拟接口错误比例 |
| 渲染 ms | 模拟该维度下的前端渲染耗时 |

数据来源：

```text
GET /api/live
```

后端生成位置：

```text
cabinet_framework/perf_platform.py -> live_metrics()
```

该表用于展示平台按区域、端类型或业务维度进行横向性能对比的能力。

## 8. 前端性能与图表策略说明

页面中的“前端性能 / 图表策略”区域列出当前页面采用的关键策略：

| 策略 | 当前实现 |
|---|---|
| 密集序列使用 Canvas | `drawSeries()` |
| 不创建百万级 DOM/SVG 节点 | 后端先采样，前端只画采样点 |
| 服务端 min/max bucket 采样 | `minmax_bucket_sample()` |
| 实时数据和历史密集数据分离 | `/api/live` 与 `/api/dense-series` 分离 |
| 批量绘制 | `requestAnimationFrame()` |
| 接口失败保留页面数据 | `lastGood` 快照 |

## 9. 性能预算与稳定性检查表

页面中的“性能预算与稳定性检查”表展示当前平台的工程约束。

| 项目 | 目标 | 当前策略 |
|---|---|---|
| 首屏可交互 | < 2.5s | 静态壳 + 异步取数 |
| 实时轮询 | 1s-5s adaptive | 指数退避 + last-good fallback |
| 百万点渲染 | 浏览器只绘制采样后点位 | server min/max bucket + canvas |
| 图表帧率 | >= 45fps under sampled view | requestAnimationFrame + 分层 canvas |
| AI 生成代码稳定性 | 每次变更跑 smoke + API contract | unittest + JSON schema-ish checks |

这些预算来自：

```text
cabinet_framework/perf_platform.py -> BUDGETS
```

## 10. API / 数据结构展示区

页面底部展示 `/api/overview` 返回的 JSON 内容。

当前数据结构包括：

```text
MetricPoint: metric, dimension, ts, value
DenseSeries: raw points stay server-side; client receives min/max buckets
LiveSnapshot: summary + dimension table + chart deltas
```

这一区域用于展示前后端约定的数据模型。

## 11. 当前 API

### `/api/overview`

用途：返回平台能力、性能预算和数据模型。

### `/api/live`

用途：返回实时指标和多维度表格数据。

参数：

```text
failure_rate    模拟接口失败率，范围 0.0 到 0.9
seed            可选，用于固定模拟数据
```

### `/api/dense-series`

用途：返回采样后的密集曲线数据。

参数：

```text
points          原始点数，最大 1000000
width           画布宽度，用于决定采样桶数量
seed            可选，用于固定模拟数据
```

## 12. 当前已经验证的内容

测试文件：

```text
tests/test_perf_platform.py
```

测试覆盖：

- 1,000,000 原始点会被压缩到可渲染规模。
- `/api/overview` 返回平台信息。
- `/api/live` 返回实时指标结构。
- `/api/dense-series` 返回采样数据结构。
- overview 中包含 AI 生成代码稳定性说明。

运行命令：

```bash
python3 -m unittest discover -s tests -v
```

已验证过的接口结果包括：

```text
/api/dense-series?points=1000000&width=1600
raw_points: 1000000
sampled_points: 3200
strategy: server-side min/max bucket sampling
```

## 13. 当前版本边界

当前 8790 页面是本地原型，已经实现核心展示链路，但还没有接入生产级能力。

已经实现：

- 本地页面展示
- 本地 API
- 实时指标轮询
- 接口失败模拟
- last-good fallback
- 指数退避
- 百万点数据生成
- min/max bucket 采样
- Canvas 绘制
- API contract 测试

尚未实现：

- 真实数据库接入
- 真实业务指标接入
- 用户权限系统
- 持久化查询
- 图表缩放与框选
- 多图联动
- WebSocket / SSE 推送
- 正式 benchmark 报告
- 生产部署配置

## 14. 当前页面总结

8790 页面展示的是一个高性能数据分析平台的核心技术链路：

```text
后端生成模拟性能数据
后端对百万级曲线做 min/max bucket 采样
前端轮询实时指标
前端用 Canvas 绘制采样曲线
接口失败时前端使用 last-good fallback 和指数退避
测试保证 API contract 和采样逻辑稳定
```

当前页面最重要的展示点是：

```text
1,000,000 原始点不会直接进入浏览器渲染，而是在后端采样为约 3,200 个点，再由 Canvas 绘制。
```
