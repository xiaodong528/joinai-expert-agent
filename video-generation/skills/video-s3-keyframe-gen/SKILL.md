---
name: video-s3-keyframe-gen
description: "使用 Seedream txt2img 和 img2img 进行首尾帧锚定链关键帧生成。为每个分镜生成首帧和尾帧，用于 Seedance 首尾帧视频模式。Triggers on keyframe, anchor chain, first frame, last frame."
---

# Stage 3: 关键帧图像生成 (Keyframe Generation)

**用途**

## 依赖

- `~/.config/opencode/skills/video-s3-keyframe-gen/scripts/` 下脚本、模型说明和当前 Stage 输入文件。

## 输入契约

- 见下方 `## 输入/输出契约` 详细说明。

## 输出契约

- 见下方 `## 输入/输出契约` 详细说明。

## 执行流程

1. 读取 `Video-Producer-output/{project_id}` 下当前 Stage 需要的输入。
2. 按下文脚本命令或规则执行当前 Stage。
3. 核对输出文件后再进入验证清单。

使用 Seedream 4.0 为每个分镜生成关键帧 PNG：一张**首帧**（必需）和一张**尾帧**（可选，当分镜脚本中存在 `末帧图提示词` 时生成）。
第 1 个分镜的首帧使用 txt2img 生成。后续分镜的首帧使用 img2img，锚定自**上一个分镜的尾帧**（若无尾帧则使用首帧），形成**首尾帧锚定链**以保持视觉连续性。

## 输入/输出契约

**输入**
- `Video-Producer-output/{project_id}/scripts/storyboard.yaml` — 包含 `分镜列表[]`，每项含：
  - `编号`: 分镜编号（整数）
  - `文生图提示词`: 首帧图像提示词（包含角色 DNA — 完整重复）
  - `末帧图提示词`: 尾帧图像提示词（可选 — 规则同文生图提示词）
  - `风格锁定.统一风格前缀`: Stage 0 冻结
  - `风格锁定.负面提示词`: Stage 0 冻结
- `Video-Producer-output/{project_id}/characters/{name}-ref.png` — 可选，来自 Stage 2

**输出**
- `Video-Producer-output/{project_id}/frames/scene-{01..N}-first.png` — 每个分镜的首帧（始终生成）
- `Video-Producer-output/{project_id}/frames/scene-{01..N}-last.png` — 每个分镜的尾帧（仅当 `末帧图提示词` 存在时生成）

## API 详情

- **模型**: `doubao-seedream-4-0-250828`
- **平台**: 火山引擎
- **端点**: `POST https://ark.cn-beijing.volces.com/api/v3/images/generations`
- **鉴权**: `Authorization: Bearer {ARK_API_KEY}`

### 关键参数

| 参数 | 分镜 1 | 分镜 2+ | 说明 |
|------|--------|---------|------|
| `model` | `doubao-seedream-4-0-250828` | 同上 | 必填 |
| `prompt` | `{style_prefix} {image_prompt}` | 同上 | 包含完整角色 DNA |
| `negative_prompt` | 冻结值 | 冻结值 | 不可修改 |
| `image_urls` | 角色参考图（可选） | `[prev_frame_url]` | 用于连续性锚定 |
| `scale` | `0.7`（锚定时） | `0.3–0.5` | 值越低创意自由度越高 |
| `n` | `1` | `1` | 每个分镜一帧 |

## 脚本

```bash
# 全部场景（串行）
python ~/.config/opencode/skills/video-s3-keyframe-gen/scripts/stage3_keyframe_chain.py \
  --project-id <project_id> \
  --storyboard Video-Producer-output/<project_id>/scripts/storyboard.yaml

# 指定范围（分批并行时使用）
python ~/.config/opencode/skills/video-s3-keyframe-gen/scripts/stage3_keyframe_chain.py \
  --project-id <project_id> \
  --storyboard Video-Producer-output/<project_id>/scripts/storyboard.yaml \
  --start-scene 1 --end-scene 3
```

**参数说明**:
- `--start-scene N`: 从场景 N 开始处理（默认 1）。跳过的场景会读取已有帧作为锚点
- `--end-scene M`: 处理到场景 M 为止（含）。省略则处理到最后一个场景

批内严格串行（首帧锚定链依赖）。输出写入 `Video-Producer-output/{project_id}/frames/scene-{01..N}-first.png` 和 `-last.png`。

## 使用示例

```python
import requests, os

ARK_API_KEY = os.environ["ARK_API_KEY"]
ENDPOINT = "https://ark.cn-beijing.volces.com/api/v3/images/generations"

def generate_keyframe(
    prompt: str,
    negative_prompt: str,
    anchor_url: str | None = None,
    scale: float = 0.4,
) -> bytes:
    payload = {
        "model": "doubao-seedream-4-0-250828",
        "prompt": prompt,
        "negative_prompt": negative_prompt,
        "n": 1,
    }
    if anchor_url:
        payload["image_urls"] = [anchor_url]
        payload["scale"] = scale

    resp = requests.post(
        ENDPOINT,
        json=payload,
        headers={"Authorization": f"Bearer {ARK_API_KEY}"},
        timeout=60,
    )
    resp.raise_for_status()
    image_url = resp.json()["data"][0]["url"]
    return requests.get(image_url, timeout=60).content


# Chain: scene 1 = txt2img, scene N = img2img with previous
prev_frame_url = None
for scene in scenes:
    img_bytes = generate_keyframe(
        prompt=f"{scene['style_prefix']} {scene['image_prompt']}",
        negative_prompt=scene["negative_prompt"],
        anchor_url=prev_frame_url,
        scale=0.4,
    )
    path = f"Video-Producer-output/{project_id}/frames/scene-{scene['scene_id']}.png"
    Path(path).write_bytes(img_bytes)
    prev_frame_url = upload_to_accessible_url(path)  # for next scene's anchor
```

## 锚定链机制（首帧 + 尾帧）

```
Scene 01 首帧 → txt2img (no anchor)                           → scene-01-first.png
Scene 01 尾帧 → img2img(anchor=scene-01-first, s=0.4)         → scene-01-last.png  (if 末帧图提示词 exists)
Scene 02 首帧 → img2img(anchor=scene-01-last, s=0.4)          → scene-02-first.png  ← anchored from LAST frame
Scene 02 尾帧 → img2img(anchor=scene-02-first, s=0.4)         → scene-02-last.png  (if 末帧图提示词 exists)
...
Scene N  首帧 → img2img(anchor=scene-(N-1)-last, s=0.4)       → scene-N-first.png
Scene N  尾帧 → img2img(anchor=scene-N-first, s=0.4)          → scene-N-last.png
```

**回退机制**（无 `末帧图提示词` 时）：该分镜仅生成 `-first.png`，下一个分镜从该首帧锚定 — 与原始单帧行为一致。

- `scale` 范围 `0.3–0.5`：值越低保留锚定图越多（连续性越高），值越高允许更大偏离（更贴近提示词）
- 锚定来源为**上一个分镜的尾帧**（若无尾帧则为首帧）— 随分镜数量增加，漂移会逐渐累积

## 验证清单

- [ ] 所有 `scene-{01..N}-first.png` 文件存在于 `Video-Producer-output/{project_id}/frames/` 中
- [ ] 每个包含 `末帧图提示词` 的分镜均存在对应的 `scene-{01..N}-last.png`
- [ ] 分辨率为 1920x1080（16:9）
- [ ] 相邻帧视觉上连贯一致（角色相同、光照方向一致）
- [ ] 无空白/损坏图片（每个文件大小 > 50 KB）
- [ ] 每帧（首帧和尾帧）中的角色外观均匹配 DNA 描述
- [ ] 风格前缀在所有帧中视觉上保持一致
- [ ] 尾帧相对于首帧呈现合理的场景结束状态

## 错误处理

- HTTP 错误时：记录 scene_id 及完整响应，继续处理剩余分镜（不中断锚定链）
- 锚定图上传失败时：该分镜回退为 txt2img，记录警告
- 视觉连贯性不达标时：将 `scale` 降低 0.1 并重新生成该分镜

## 分批并行调度（GasTown Wave 2）

锚定链要求批内严格串行，但可通过分批实现批间并行。主智能体将 N 个场景分为 M 批，每批派发一个子智能体：

```bash
# 子智能体 1: 场景 1-3（批内串行）
python ~/.config/opencode/skills/video-s3-keyframe-gen/scripts/stage3_keyframe_chain.py \
  --project-id {id} --storyboard ... --start-scene 1 --end-scene 3

# 子智能体 2: 场景 4-6（需等待子智能体 1 完成场景 3 的尾帧/首帧）
python ~/.config/opencode/skills/video-s3-keyframe-gen/scripts/stage3_keyframe_chain.py \
  --project-id {id} --storyboard ... --start-scene 4 --end-scene 6

# 子智能体 3: 场景 7-10
python ~/.config/opencode/skills/video-s3-keyframe-gen/scripts/stage3_keyframe_chain.py \
  --project-id {id} --storyboard ... --start-scene 7
```

**注意**：批 2 的 `--start-scene 4` 会自动读取场景 3 已有帧作为锚点，因此批 2 必须在批 1 完成后才能启动。如果批间无依赖（独立锚点），可完全并行。

## 备注

- **串行依赖**：分镜 N 需要分镜 N-1 完成后才能开始 — 同批次内无法并行
- **批间并行**：不同批次可由独立子智能体执行，但后续批次需等待前一批次完成以获取锚点帧
- 角色 DNA 必须在每个 `image_prompt` 中**完整重复** — 不可缩写
- `image_urls` 需要可公开访问的 URL；本地生成的 PNG 需先上传至对象存储后才能作为锚定图使用
