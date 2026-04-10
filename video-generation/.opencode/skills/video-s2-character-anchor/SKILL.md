---
name: video-s2-character-anchor
description: "Seedream 4.0 角色一致性锚定，通过 image_urls 参考图实现。Triggers on character anchor, Seedream, consistency."
---

# Stage 2: 角色一致性锚定 (Character Anchor)

**用途**

## 依赖

- `.opencode/skills/video-s2-character-anchor/scripts/` 下脚本、模型说明和当前 Stage 输入文件。

## 输入契约

- 见下方 `## 输入/输出契约` 详细说明。

## 输出契约

- 见下方 `## 输入/输出契约` 详细说明。

## 执行流程

1. 读取 `Video-Producer-output/{project_id}` 下当前 Stage 需要的输入。
2. 按下文脚本命令或规则执行当前 Stage。
3. 核对输出文件后再进入验证清单。

使用 Seedream 4.0 txt2img 配合 `image_urls` 锚定，为每个角色生成参考图像。
本阶段为**可选**——仅在短剧 (drama) 或包含重复出场角色的视频类型中需要。
输出角色参考 PNG 图像，供下游阶段 (3, 4) 在每个 prompt 中通过角色 DNA 卡片引用。

## 输入/输出契约

**输入**
- `story.yaml` — 包含 `characters[]` 数组，每个角色包含：
  - `name`：角色标识
  - `dna`：完整外貌描述（不可缩写）
  - `style_prefix`：在 Stage 0 冻结
  - `negative_prompt`：在 Stage 0 冻结
- 可选：`Video-Producer-output/{project_id}/characters/` 中已有的参考图像（用于迭代优化）

**输出**
- `Video-Producer-output/{project_id}/characters/{name}-ref.png` — 每个角色一张 PNG
- 格式：PNG，分辨率 1920×1080（横屏 16:9）

## API 详情

- **模型**: `doubao-seedream-4-0-250828`
- **平台**: 火山引擎
- **端点**: `POST https://ark.cn-beijing.volces.com/api/v3/images/generations`
- **鉴权**: `Authorization: Bearer {ARK_API_KEY}`

### 关键参数

| 参数 | 值 | 说明 |
|------|-----|------|
| `model` | `doubao-seedream-4-0-250828` | 必填 |
| `prompt` | `{style_prefix} {character_dna}` | 完整 DNA——不可缩写 |
| `negative_prompt` | 冻结的风格锁定值 | 来自 story.yaml |
| `image_urls` | `[existing_ref_url]` | 可选；在迭代优化时增强一致性 |
| `scale` | `0.7` | 提供 image_urls 时的锚定强度 |
| `n` | `1` | 每个角色一张参考图 |

## 脚本

```bash
python .opencode/skills/video-s2-character-anchor/scripts/stage2_seedream.py \
  --project-id <project_id> \
  --story Video-Producer-output/<project_id>/scripts/story.yaml
```

脚本从 `story.yaml` 读取所有角色，为每个角色生成一张参考图像，
并写入 `Video-Producer-output/{project_id}/characters/{name}-ref.png`。

## 使用示例

```python
import requests, os, yaml

ARK_API_KEY = os.environ["ARK_API_KEY"]
ENDPOINT = "https://ark.cn-beijing.volces.com/api/v3/images/generations"

def generate_character_ref(name: str, dna: str, style_prefix: str, negative_prompt: str) -> bytes:
    payload = {
        "model": "doubao-seedream-4-0-250828",
        "prompt": f"{style_prefix} {dna}",
        "negative_prompt": negative_prompt,
        "n": 1,
        "scale": 0.7,
    }
    resp = requests.post(
        ENDPOINT,
        json=payload,
        headers={"Authorization": f"Bearer {ARK_API_KEY}"},
        timeout=60,
    )
    resp.raise_for_status()
    image_url = resp.json()["data"][0]["url"]
    return requests.get(image_url, timeout=60).content
```

## 一致性测试

使用相同角色 DNA 生成 3 张图像并进行对比：

```bash
python .opencode/skills/video-s2-character-anchor/scripts/stage2_seedream.py \
  --project-id test_consistency \
  --name "主角" \
  --n 3
# 然后目视检查：3 张图是否共享面部特征、服装和发色？
```

## 验证清单

- [ ] API 返回 HTTP 200 且 `data[0].url` 已填充
- [ ] 图像 URL 可访问并返回有效 PNG 字节
- [ ] `Video-Producer-output/{project_id}/characters/{name}-ref.png` 已写入磁盘
- [ ] 角色与 DNA 描述一致（面部、服装、发型、风格）
- [ ] 多角色项目中无其他角色的风格渗透
- [ ] 文件大小 > 10 KB（非空白/错误图像）

## 错误处理

- HTTP 4xx/5xx 时：记录完整响应体，附带角色名称上下文抛出异常
- 下载失败时：以 2 秒退避间隔重试最多 3 次
- 若 `image_urls` 锚定导致质量下降：移除锚定，不使用 image_urls 重试

## 备注

- 角色 DNA 必须在每个下游 prompt 中**完整重复**——禁止使用代词或引用
- `scale=0.7` 为推荐锚定强度；较低值 (0.5) 会降低一致性，较高值 (0.9) 可能降低 prompt 还原度
- 若需要 ComfyUI + IP-Adapter 实现更强一致性，本阶段输出的参考图可作为该工作流的种子图像
