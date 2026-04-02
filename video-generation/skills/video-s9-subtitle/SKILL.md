---
name: video-s9-subtitle
description: "SRT 字幕生成与 FFmpeg 烧录，使用 PingFang SC 字体。Triggers on subtitle, SRT, ASR, burn-in."
---

# Stage 9: 字幕生成与烧录 (Optional, Recommended)

## 用途

从对白生成 SRT 字幕文件，然后使用 FFmpeg 将字幕烧录到最终视频中。支持两种模式：模式 A（基于脚本，推荐）或模式 B（基于 ASR）。

## 脚本

```
.opencode/skills/video-s9-subtitle/scripts/stage9_subtitle.py
```

## 输入/输出契约

| 项目 | 路径 | 说明 |
|------|------|------|
| 输入视频 | `Video-Producer-output/{project_id}/videos/lipsync.mp4`（或 concat-final.mp4） | |
| 分镜脚本 | `Video-Producer-output/{project_id}/scripts/storyboard.yaml` | 包含对白和 TTS 时长 |
| TTS 音频（模式 B） | `Video-Producer-output/{project_id}/audio/tts-{01..N}.mp3` | 用于 ASR 识别 |
| **输出 SRT** | `Video-Producer-output/{project_id}/subtitles/final.srt` | UTF-8 编码 |
| **输出视频** | `Video-Producer-output/{project_id}/videos/final.mp4` | H.264 + AAC，含字幕 |

## 模式 A: 基于脚本（推荐）

直接从 `storyboard.yaml` 中提取对白文本和 TTS 时长，无需调用 API。

```python
import yaml

def generate_srt_from_storyboard(storyboard_path: str) -> list[dict]:
    with open(storyboard_path) as f:
        storyboard = yaml.safe_load(f)

    entries = []
    current_time = 0.0
    for i, scene in enumerate(storyboard["scenes"], 1):
        dialogue = scene.get("台词", scene.get("旁白", "")).strip()
        duration = scene.get("tts_duration", scene.get("duration", 3.0))
        if dialogue:
            entries.append({
                "index": i,
                "start": current_time,
                "end": current_time + duration,
                "text": dialogue,
            })
        current_time += scene.get("duration", duration)
    return entries
```

## 模式 B: 基于 ASR（豆包 ASR 2.0）

当 TTS 时长不可用或需要精确的词级时间戳时使用。

```python
# Submit audio for ASR batch recognition
# API: 火山引擎 豆包 ASR 2.0 (Mode B — long-form batch)
payload = {
    "audio_url": presigned_tts_url,
    "language": "zh",
    "output_format": "word_timestamp",
}
# Returns word-level timestamps → convert to sentence-level SRT entries
```

## SRT 文件格式

```python
def write_srt(entries: list[dict], output_path: str) -> None:
    def fmt_time(seconds: float) -> str:
        h = int(seconds // 3600)
        m = int((seconds % 3600) // 60)
        s = int(seconds % 60)
        ms = int((seconds % 1) * 1000)
        return f"{h:02d}:{m:02d}:{s:02d},{ms:03d}"

    with open(output_path, "w", encoding="utf-8") as f:
        for entry in entries:
            f.write(f"{entry['index']}\n")
            f.write(f"{fmt_time(entry['start'])} --> {fmt_time(entry['end'])}\n")
            f.write(f"{entry['text']}\n\n")
```

## FFmpeg 字幕烧录

```bash
ffmpeg -i input_video.mp4 \
  -vf "subtitles=final.srt:force_style='FontName=PingFang SC,FontSize=24,PrimaryColour=&HFFFFFF,OutlineColour=&H000000,Outline=2,Bold=1'" \
  -c:v libx264 -c:a copy \
  Video-Producer-output/{project_id}/videos/final.mp4
```

### 字幕样式参数

| 参数 | 值 | 说明 |
|------|------|------|
| FontName | `PingFang SC` | macOS/iOS 中文字体 |
| FontSize | `24` | 1080p 下可读 |
| PrimaryColour | `&HFFFFFF` | 白色文字（BGR 十六进制） |
| OutlineColour | `&H000000` | 黑色描边 |
| Outline | `2` | 描边粗细（像素） |
| Bold | `1` | 加粗以提升可读性 |

> 在 Linux 服务器上，将 `PingFang SC` 替换为 `Noto Sans CJK SC`，或通过 `-fontsdir` 嵌入字体。

## 关键参数

| 参数 | 值 |
|------|------|
| 推荐模式 | 模式 A（基于脚本） |
| 时间戳容差 | ± 0.3s |
| SRT 编码 | UTF-8（无 BOM） |
| 输出编码格式 | H.264 + AAC（音频直接拷贝） |

## 验证清单

- [ ] `final.srt` 存在且为有效的 UTF-8 文件
- [ ] SRT 时间戳按时间顺序排列，无重叠
- [ ] 字幕时间戳与实际语音对齐，误差在 ± 0.3s 以内
- [ ] 分镜脚本中所有对白行均已包含在 SRT 中
- [ ] 中文字符在 `final.mp4` 中正确渲染（无豆腐块）
- [ ] 字体（PingFang SC）可用；如不可用已配置回退字体
- [ ] `final.mp4` 时长与输入视频时长匹配，误差在 ± 0.5s 以内
- [ ] 字幕不遮挡人脸（定位在画面下方三分之一区域）

## 错误处理

- 缺少字体：记录警告日志，回退至 `Noto Sans CJK SC` 或默认无衬线字体
- 场景中对白为空：跳过该条目（该场景不生成字幕）
- ASR API 失败（模式 B）：若分镜脚本可用，回退至模式 A
- SRT 时间戳重叠：自动修复，将 `end` 裁剪至下一条目的 `start - 0.05s`
