---
name: video-s6-bgm
description: "MiniMax Music 2.5+ 背景音乐生成（纯 instrumental）。Triggers on BGM, background music, MiniMax."
---

# Stage 6: BGM 与音效（背景音乐，可选/推荐）

**用途**

## 依赖

- `.opencode/skills/video-s6-bgm/scripts/` 下脚本、模型说明和当前 Stage 输入文件。

## 输入契约

- 见下方 `## 输入/输出契约` 详细说明。

## 输出契约

- 见下方 `## 输入/输出契约` 详细说明。

## 执行流程

1. 读取 `Video-Producer-output/{project_id}` 下当前 Stage 需要的输入。
2. 按下文脚本命令或规则执行当前 Stage。
3. 核对输出文件后再进入验证清单。

使用 MiniMax Music 2.5+ 为完整视频生成 instrumental 背景音乐。
此阶段**可选但推荐**用于所有视频类型。
与 Stage 4 和 Stage 5 并行运行（GasTown Wave 3）。
输出必须为 instrumental（无人声），且时长需覆盖视频总时长。

## 输入/输出契约

**输入**
- `Video-Producer-output/{project_id}/scripts/story.yaml` — 包含：
  - `mood`：情绪基调（如 `epic`、`melancholic`、`upbeat`、`mysterious`）
  - `style`：音乐风格描述（如 `orchestral`、`electronic`、`folk`）
  - `total_duration`：预估视频总时长（秒），为所有场景时长之和

**输出**
- `Video-Producer-output/{project_id}/audio/bgm.mp3` — 单条 instrumental 音轨
- 时长必须 ≥ `total_duration`（Stage 7 裁剪至精确长度，不做填充）

## API 详情

- **模型**: `music-2.5+`
- **平台**: MiniMax
- **端点**: `POST https://api.minimaxi.com/v1/music_generation`
- **认证**: `Authorization: Bearer {MINIMAX_API_KEY}`

### 关键参数

| 参数 | 值 | 说明 |
|------|-----|------|
| `model` | `music-2.5+` | 必填 |
| `prompt` | mood + style 描述 | 见下方提示词模板 |
| `is_instrumental` | `true` | **必须为 true** — 不允许含人声 |
| `lyrics_optimizer` | `true` | 跳过歌词，纯器乐模式 |
| `refer_duration` | `total_duration + 30` | 额外缓冲；Stage 7 裁剪至精确长度 |
| `output_format` | `"url"` | 响应返回音频下载 URL |
| `audio_setting` | `{ sample_rate: 44100, bitrate: 256000, format: "mp3" }` | 音频质量参数 |

### 同步模式（output_format=url）

MiniMax Music API 使用 `output_format: "url"` 时为**同步模式**——音频 URL 直接在响应中返回（非异步轮询）：

```
POST /v1/music_generation → { "data": { "audio": "https://...mp3", "status": 2 } }
```

响应中 `data.audio` 为 OSS 音频下载 URL（`data.status: 2` 表示成功），直接下载保存。
生成耗时较长（30s-300s），**超时建议 ≥ 300s**（脚本默认 600s）。

## 脚本

```bash
python .opencode/skills/video-s6-bgm/scripts/stage6_bgm.py \
  --project-id <project_id> \
  --prompt "orchestral instrumental, epic atmosphere" \
  --duration-hint 120
```

## 使用示例

```python
import os, requests

MINIMAX_API_KEY = os.environ["MINIMAX_API_KEY"]
BASE_URL = "https://api.minimaxi.com/v1"
HEADERS = {"Authorization": f"Bearer {MINIMAX_API_KEY}", "Content-Type": "application/json"}

def generate_bgm(prompt: str, refer_duration: int = 60) -> str:
    """同步调用 MiniMax Music API（output_format=url），返回音频下载 URL。"""
    resp = requests.post(
        f"{BASE_URL}/music_generation",
        json={
            "model": "music-2.5+",
            "prompt": prompt,
            "is_instrumental": True,
            "lyrics_optimizer": True,
            "refer_duration": refer_duration,
            "audio_setting": {"sample_rate": 44100, "bitrate": 256000, "format": "mp3"},
            "output_format": "url",
        },
        headers=HEADERS,
        timeout=600,
    )
    resp.raise_for_status()
    audio_url = resp.json()["data"]["audio"]  # OSS URL
    return audio_url  # 下载: requests.get(audio_url).content
```

## 提示词模板

```
{style} instrumental background music, {mood} atmosphere,
suitable for {video_type}, no vocals, no lyrics,
smooth loop-friendly structure
```

示例：
- `orchestral instrumental background music, epic and heroic atmosphere, suitable for 短剧, no vocals`
- `electronic instrumental background music, mysterious and tense atmosphere, suitable for 宣传片, no vocals`
- `folk instrumental background music, warm and nostalgic atmosphere, suitable for 创意短视频, no vocals`

## 验证清单

- [ ] `Video-Producer-output/{project_id}/audio/bgm.mp3` 存在且可播放
- [ ] 文件大小 > 500 KB（非空白/错误文件）
- [ ] **无人声** — 试听前 30 秒和最后 30 秒以验证
- [ ] 时长 ≥ 视频总时长（通过 `ffprobe -show_entries format=duration` 验证）
- [ ] 音乐风格与 story.yaml 中指定的 mood/genre 匹配
- [ ] 音频无突兀切断或刺耳过渡

## 时长验证

```bash
ffprobe -v error -show_entries format=duration -of csv=p=0 \
  Video-Producer-output/<project_id>/audio/bgm.mp3
# Output should be >= total_video_duration
```

## 错误处理

- HTTP 4xx/5xx：记录完整响应体，10 秒后重试一次
- `base_resp.status_code != 0`：记录 `status_msg` 错误详情，使用简化 prompt 重试
- 超时（600s）：记录已用时间，检查网络连接后重试
- 时长不足：将 `refer_duration` 增加 60 秒后重新提交

## 备注

- `is_instrumental=true` **强制要求** — BGM 中的人声会与 Stage 5 的 TTS 音频冲突
- 请求时长 = `total_duration + 30s` 缓冲；Stage 7 使用 FFmpeg `-t` 参数裁剪至精确长度
- Stage 7 中 BGM 以较低音量混合（推荐：BGM -12dB，TTS 0dB）
- 每个项目仅一条 BGM 音轨 — 此阶段运行一次（1 个 Polecat），非逐场景运行
- 备选方案：MiniMax 配额耗尽时使用 Mureka API
