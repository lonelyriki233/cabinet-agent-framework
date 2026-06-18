<!-- Managed subproject reference, not framework core. -->

# 从 AI Agent MVP 提取为小说/IP/世界体系创作框架：分析与整改清单

## 1. 提取结论

已从原 `agent_framework_exam` 提取出一个可复用于其他工程的本地运行时框架，并新建目录：

```text
<repo-root>
```

新框架目标不再是 coding harness / 数据平台，而是文本优先的长期创作工程：

```text
OC / IP / 世界观 / 故事集群
  -> 正典档案
  -> 世界体系
  -> 故事矩阵
  -> 角色与关系网
  -> 严格作画体系
  -> AI 配音规格
  -> 谱曲/配乐规格
  -> dashboard / hook / archive / gate 监控
```

## 2. 原 MVP 中已可复用、已部署到新框架的能力

| 原 MVP 能力 | 新框架状态 | 新用途 |
|---|---:|---|
| `Leader Gateway` 请求分类 | 已部署 | 判断正典、世界观、故事集群、角色、作画、配音、音乐等任务类型 |
| `Strategy Council` 参议机制 | 已部署并改名为 Story Council 语义 | 激活 canon / narrative / world / media / risk / evidence councillors |
| `Chief Coordinator` 任务拆解 | 已部署并重写 | 把一个大型 OC/IP 请求拆成正典、世界观、故事、角色、视觉、音频音乐、文档任务 |
| `TaskPacket` 结构化任务包 | 已部署 | 每个创作任务都有 worker、目标、允许路径、禁区、验收标准、required_outputs |
| `worker prompt` 生成 | 已部署并重写 | 强制标注“正典 / 待定 / 废案 / 参考”，并要求自我质疑与后续依赖 |
| `hooks` 生命周期 | 已部署 | task.created / before_run / after_run / archive / audit / stop_gate 仍可用 |
| `dispatcher / heartbeat` | 已部署 | 可 prompt 模式推进创作任务，也可 hermes 模式调用真实 agent 执行 |
| `archive` 分层归档与搜索 | 已部署 | 按 bureau/task_type/task_id 归档创作产物 |
| `dashboard` | 已部署并部分改文案 | 查看 worker、任务、hooks、archive、docs |
| `gates` | 已部署并改结构检查 | 检查目录、禁区文件、任务包 schema |
| `conversation_bridge` | 已部署 | Hermes 对话中的创作请求可进入 runtime 和 dashboard |
| `hermes_bridge` | 已部署 | 后续可让 worker 用 Hermes 执行具体写作/整理任务 |

## 3. 已替换掉的“工程/数据平台”内容

| 原内容 | 新内容 |
|---|---|
| frontend_worker | art_prompt_worker / 视觉体系 worker |
| backend_worker | 已移除 |
| data_perf_worker | 已移除 |
| harness_worker | 已移除为创作框架内部职责，不再当用户 workload worker |
| product/data/service/platform bureaus | canon/world/narrative/character/visual/audio_music/knowledge bureaus |
| 高性能数据平台示例 | OC/IP/世界体系创作请求示例 |
| `perf-platform` CLI | 已移除 |
| Dashboard 数据平台说明 | 改为创作工程说明 |

## 4. 新框架 worker 设计

| Worker | Bureau | 负责内容 |
|---|---|---|
| `canon_archivist_worker` | `canon_bureau` | 正典库、设定冲突、事实源、版本记录 |
| `worldbuilding_worker` | `world_bureau` | 世界观、地理、历史、势力、规则系统 |
| `story_cluster_worker` | `narrative_bureau` | 故事集群、主线支线、篇章结构、事件链 |
| `character_oc_worker` | `character_bureau` | OC、人设、关系网、成长弧线、口吻 |
| `art_prompt_worker` | `visual_bureau` | 严格作画体系、视觉圣经、AI 作画提示词模板 |
| `voice_audio_worker` | `audio_music_bureau` | AI 配音、声线、台词口吻、音频规格 |
| `music_worker` | `audio_music_bureau` | 主题动机、配乐方向、曲式/情绪规格 |
| `research_worker` | `knowledge_bureau` | 参考系、工艺路线、版权/风格边界调研 |
| `documentation_worker` | `knowledge_bureau` | 文档、索引、交付清单、维护报告 |

## 5. 当前还需要整改/增强的功能

### 5.1 文本创作所需的正典数据库还不够强

当前 archive 只是按任务输出归档，适合保存 worker 结果，但还没有真正的“正典条目”模型。

建议新增：

```text
canon/entries/*.json
canon/timeline/*.md
canon/conflicts/*.md
canon/decisions/*.md
```

并增加命令：

```bash
python3 -m cabinet_framework.cli canon-add
python3 -m cabinet_framework.cli canon-check
python3 -m cabinet_framework.cli canon-search
```

### 5.2 严格作画体系需要结构化模板

当前 `art_prompt_worker` 的 prompt 已要求写正向/负向/禁区，但还没有强制 schema。

建议新增：

```text
art_bible/characters/<name>.yaml
art_bible/styles/style_lock.yaml
art_bible/prompts/templates/*.md
art_bible/negative_prompts/*.md
```

重点字段：角色比例、发型、服饰、眼睛、表情、年龄感、禁止项、镜头、光影、色彩、画风锁定、模型/工具参数。

### 5.3 AI 配音与谱曲目前只是文本规格，未接生成工具

当前设计是正确的：先文本规格，再接工具。下一步可分两层：

```text
audio_voice/voice_bible/*.yaml
music/themes/*.musicxml 或 *.md
```

不要直接跳到生成 WAV；先做可复用的 voice bible / music brief。

### 5.4 Dashboard 还沿用原 MVP 的通用布局

虽然文案已改，但 UI 还不是“创作驾驶舱”。建议后续新增页面：

| 页面 | 用途 |
|---|---|
| `/canon` | 正典条目、冲突、待定设定 |
| `/world` | 世界观模块、势力、时间线 |
| `/stories` | 故事集群矩阵、主线/支线状态 |
| `/characters` | OC 卡、人际关系、人物弧线 |
| `/art-bible` | 作画体系、角色视觉锁、prompt 模板 |
| `/audio-music` | 声线、台词口吻、主题动机、配乐规格 |

### 5.5 需要“创作一致性 gate”

当前 gate 只检查结构、禁区、任务包 schema。文本创作还需要：

- canon_gate：新设定是否与已有正典冲突
- oc_voice_gate：角色口吻是否跑偏
- art_consistency_gate：视觉提示词是否违反角色视觉圣经
- story_cluster_gate：新故事是否挂到主线/支线/时代位置
- media_spec_gate：作画/配音/谱曲是否有可执行规格

## 6. 当前可运行命令

```bash
cd <repo-root>
python3 -m cabinet_framework.cli init
python3 -m unittest discover -s tests -v
python3 -m cabinet_framework.cli gate
python3 -m cabinet_framework.cli chat-intake --authority L2 --request "建立我的OC为小说/IP/世界体系，包含故事集群、世界观、角色、严格作画体系、AI配音、谱曲规格"
python3 -m cabinet_framework.cli tasks
python3 -m cabinet_framework.cli dispatch --mode prompt --max-steps 3
python3 -m cabinet_framework.cli dashboard --port 8788
```

## 7. 设计边界

已明确：

- 这是文本性创作框架，不是数据平台。
- 不默认生成图片、音频或音乐。
- 先建立可控的文本规格和正典体系，再接 AI 作画、AI 配音、谱曲工具。
- 框架本体负责拆解、执行、审计、归档和监控；具体故事/角色/图像/音乐是 workload，不是框架本体。
