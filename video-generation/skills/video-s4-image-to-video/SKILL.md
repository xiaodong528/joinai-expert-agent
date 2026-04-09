---
name: video-s4-image-to-video
description: "Seedance 1.5 Pro 异步图生视频，支持首尾帧模式，默认时长 12 秒。Triggers on image to video, Seedance, video generation."
---

# Stage 4: 图生视频 (Image-to-Video, Async)

**用途**

## 依赖

- `~/.config/opencode/skills/video-s4-image-to-video/scripts/` 下脚本、模型说明和当前 Stage 输入文件。

## 输入契约

- 见下方 `## 输入/输出契约` 详细说明。

## 输出契约

- 见下方 `## 输入/输出契约` 详细说明。

## 执行流程

1. 读取 `Video-Producer-output/{project_id}` 下当前 Stage 需要的输入。
2. 按下文脚本命令或规则执行当前 Stage。
3. 核对输出文件后再进入验证清单。

使用 Seedance 1.5 Pro 将每张关键帧 PNG 转换为短视频片段。
本阶段为**异步模式**：提交任务、轮询直至完成、然后下载 MP4。
所有场景并行执行（GasTown 中的 Wave 3）。

## 输入/输出契约

**输入**
- `Video-Producer-output/{project_id}/frames/scene-{01..N}-first.png` — Stage 3 生成的首帧关键帧（必需）
- `Video-Producer-output/{project_id}/frames/scene-{01..N}-last.png` — Stage 3 生成的尾帧关键帧（可选，启用首尾帧模式）
- `Video-Producer-output/{project_id}/frames/scene-{01..N}.png` — 旧版单帧格式（向后兼容回退）
- `Video-Producer-output/{project_id}/scripts/storyboard.yaml` — 包含每个场景的：
  - `图生视频提示词`：运动描述 + 镜头运动
  - `generate_audio`：`true` 或 `false`（项目级决策）

**输出**
- `Video-Producer-output/{project_id}/clips/scene-{01..N}.mp4` — 每个场景一个 MP4
- 分辨率：>= 720p；默认时长：**12 秒**（通过 `duration` 参数控制）

## API 详情

- **模型**: `doubao-seedance-1-5-pro-251215`
- **平台**: 火山方舟
- **SDK**: `volcenginesdkarkruntime`（PyPI: `volcengine-python-sdk[ark]`）
- **认证**: `ARK_API_KEY` 环境变量

### 关键参数

| 参数 | 值 | 说明 |
|------|-----|------|
| `model` | `doubao-seedance-1-5-pro-251215` | 必需 |
| `content[0]` | `image_url` + `role: "first_frame"` | 必需 — 首帧（base64 data URI） |
| `content[1]` | `image_url` + `role: "last_frame"` | **可选** — 尾帧，启用首尾帧模式 |
| `content[-1]` | `text` — 视频提示词 | 运动 + 镜头描述 |
| `duration` | `4-12`（整数，默认 5） | 视频时长（秒），推荐 12 |
| `generate_audio` | `true` / `false` | **关键决策点** — 见备注 |
| `resolution` | `720p`（默认） | 1080p 可能不可用 |
| `ratio` | `adaptive`（默认） | 图生视频自动匹配首帧比例 |

### SDK API (volcenginesdkarkruntime v5+)

```python
# Submit: client.video_generation.create()
# Poll:   client.video_generation.get(task_id=...)
# Result: result.video_url (when status == "succeeded")
```

### 异步模式

```
submit → task_id
poll every 5s → status: pending / processing / succeeded / failed
on succeeded → download video_url → save MP4
timeout: 5 minutes
```

## 脚本

```bash
python ~/.config/opencode/skills/video-s4-image-to-video/scripts/stage4_seedance.py \
  --project-id <project_id> \
  --storyboard Video-Producer-output/<project_id>/scripts/storyboard.yaml
```

所有场景并发提交；轮询在共享的 5 分钟超时内并行运行。

## 使用示例

```python
import os, time
from volcenginesdkarkruntime import Ark

client = Ark(api_key=os.environ["ARK_API_KEY"])

def submit_video_task(image_url: str, prompt: str, duration: int, generate_audio: bool) -> str:
    resp = client.video_generation.create(
        model="doubao-seedance-1-5-pro-251215",
        content=[
            {"type": "image_url", "image_url": {"url": image_url}},
            {"type": "text", "text": prompt},
        ],
        duration=duration,
        generate_audio=generate_audio,
    )
    return resp.id  # task_id

def poll_video_task(task_id: str, timeout: int = 300) -> str:
    deadline = time.time() + timeout
    while time.time() < deadline:
        result = client.video_generation.get(task_id=task_id)
        if result.status == "succeeded":
            return result.video_url
        if result.status == "failed":
            raise RuntimeError(f"Video generation failed: task_id={task_id}")
        time.sleep(5)
    raise TimeoutError(f"Task {task_id} timed out after {timeout}s")
```

## 严格并行调度模式（必须遵守）

**Stage 4 必须使用多子智能体并行模式，禁止顺序处理。** 每个场景由**独立的子智能体**执行，主智能体**同时**派发 N 个子智能体，每个处理一个场景：

```bash
# 必须同时启动所有场景的子智能体（并行，非顺序）：
# 子智能体 1: 处理场景 1
python ~/.config/opencode/skills/video-s4-image-to-video/scripts/stage4_seedance.py \
  --project-id {id} --scene 1

# 子智能体 2: 处理场景 2
python ~/.config/opencode/skills/video-s4-image-to-video/scripts/stage4_seedance.py \
  --project-id {id} --scene 2

# ... 子智能体 N: 处理场景 N（全部同时启动）
python ~/.config/opencode/skills/video-s4-image-to-video/scripts/stage4_seedance.py \
  --project-id {id} --scene {N}
```

每个子智能体内部独立完成提交→轮询→下载流程。禁止使用单智能体顺序处理，必须为每个场景单独派发子智能体以实现最大并行度。

## 验证清单

- [ ] 所有 `scene-{01..N}.mp4` 文件存在于 `Video-Producer-output/{project_id}/clips/` 目录中
- [ ] 每个片段时长与分镜目标误差在 ±1s 以内
- [ ] 分辨率 >= 720p（使用 `ffprobe -v error -select_streams v:0 -show_entries stream=width,height` 验证）
- [ ] 每个片段首尾 0.5s 内无闪烁或视觉伪影
- [ ] 每个片段的首帧与对应的关键帧 PNG 匹配
- [ ] 若 `generate_audio=true`：音轨存在且各片段间音色一致

## 错误处理

- 任务状态为 `failed` 时：记录 API 返回的完整错误信息，使用相同参数重试一次
- 超时时：记录 scene_id，标记为失败，继续处理其他场景
- 下载出错时：最多重试 3 次，采用指数退避策略
- 允许部分失败 — Stage 7 会跳过缺失的片段

## 备注

- **`generate_audio` 策略**：始终启用 `generate_audio=true`，让 Seedance 生成环境音效（脚步声、雨声、门声等）。为防止人物音色不一致，**图生视频提示词末尾必须包含 "ambient sounds only, no character speech or dialogue audio"**。角色语音由 Stage 5 TTS 独立添加，保证跨片段音色一致。
- **回退方案**：当 Seedance 配额耗尽时，可通过 DashScope（`DASHSCOPE_API_KEY`）使用 `wan2.2-kf2v-flash`
- 每个场景任务具有幂等性 — 可安全重试；输出按场景编号命名，不会产生冲突
- `volcenginesdkarkruntime` 在 Python 3.14+ 上的 Pydantic V1 兼容性警告可安全忽略
