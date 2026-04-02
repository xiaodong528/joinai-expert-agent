---
name: video-s7-concat
description: "FFmpeg 视频拼接、音频混合与字幕合并。Triggers on video concat, FFmpeg merge, audio mix, subtitle merge."
---

# Stage 7: 视频拼接 + 音频混合 + 字幕合并

## 用途

将所有分镜片段拼接为一个完整视频，混合 TTS 语音和 BGM 背景音乐，合并各场景 SRT 字幕并嵌入到最终视频。生成 `concat-final.mp4`（含视频+音频+字幕）。

## 脚本

```
.opencode/skills/video-s7-concat/scripts/stage7_concat.py
```

## 输入/输出契约

| 项目 | 路径 | 说明 |
|------|------|------|
| 分镜片段 | `output/{project_id}/clips/scene-{01..N}-final.mp4` | 优先使用 `-final`（含旁白+字幕），回退到 `scene-{N}.mp4` |
| TTS 音频（可选） | `output/{project_id}/audio/tts-{01..N}.mp3` | 每个分镜的语音 |
| BGM（可选） | `output/{project_id}/audio/bgm.mp3` | 背景音乐 |
| 场景字幕 | `output/{project_id}/subtitles/scene-{01..N}.srt` | Stage 5 TTS 生成的逐场景字幕 |
| **输出视频** | `output/{project_id}/videos/concat-final.mp4` | H.264 + AAC + mov_text 字幕 |
| **合并字幕** | `output/{project_id}/subtitles/combined.srt` | 全片字幕（时间戳已偏移） |

## 步骤

### 1. 查找片段（优先 -final.mp4）

`find_clips()` 按场景编号排序，每个场景优先使用 `scene-{N}-tts-sub.mp4`（含旁白+字幕+环境音），回退到 `scene-{N}.mp4`（原始片段）。不会同时包含同一场景的两个版本。

> **TTS 重混跳过逻辑**：当所有片段均为 `-tts-sub.mp4`（已由 Stage 5 嵌入 TTS 音频）时，Stage 7 **不再单独混合 TTS 音频**，仅额外添加 BGM。`mix_audio_tracks()` 始终保留视频自带音轨 `[0:a]`（含 TTS + 环境音效）。
>
> **SRT 合并偏移**：`merge_subtitles()` 根据每个片段实际时长（`_get_duration()`）计算时间偏移。场景 1 使用原始时间戳，场景 2 偏移 = 场景 1 时长，场景 3 偏移 = 场景 1 + 场景 2 时长，依此类推。

### 2. 拼接片段

```bash
ffmpeg -f concat -safe 0 -i filelist.txt -c copy concat-raw-silent.mp4
```

### 3. 混合音频轨道（可选）

TTS 音量 1.0 + BGM 音量 0.15：
```bash
ffmpeg -i concat-raw-silent.mp4 -i tts-combined.mp3 -i bgm.mp3 \
  -filter_complex "[1:a]volume=1.0[tts];[2:a]volume=0.15[bgm];[tts][bgm]amix=inputs=2:duration=first[aout]" \
  -map 0:v -map "[aout]" -c:v copy -c:a aac -b:a 192k \
  concat-raw.mp4
```

### 4. 合并字幕

`merge_subtitles()` 读取各场景 `subtitles/scene-{N}.srt`，根据每个片段时长计算时间偏移，合并为 `subtitles/combined.srt`。

### 5. 嵌入字幕到最终视频

```bash
ffmpeg -y -i concat-raw.mp4 -i combined.srt \
  -map 0:v -map 0:a -map 1:s \
  -c:v copy -c:a copy -c:s mov_text \
  concat-final.mp4
```

## 关键参数

| 参数 | 值 | 原因 |
|------|------|------|
| TTS 音量 | `1.0` | 语音必须清晰占主导 |
| BGM 音量 | `0.15` | 背景——不盖过语音 |
| amix `duration` | `first` | 总时长与视频一致 |
| 视频编码 | `copy` | 不重编码 |
| 字幕编码 | `mov_text` | 软字幕，播放器可切换 |

## 验证清单

- [ ] `concat-final.mp4` 可正常播放
- [ ] 包含 video + audio + subtitle 三轨道
- [ ] 总时长等于所有片段之和（±0.5s）
- [ ] `combined.srt` 字幕条目数 = 各场景字幕条目总和
- [ ] 字幕时间戳在场景衔接处正确偏移
- [ ] 视频 H.264，音频 AAC，字幕 mov_text
- [ ] 分镜转场无黑帧间隙
- [ ] BGM 不盖过 TTS 语音

## 错误处理

- 缺少片段文件：中止并报错
- 无字幕文件：跳过字幕合并，输出 `concat-raw.mp4`
- BGM 缺失：记录警告，仅用 TTS 或静音
- TTS 缺失：记录警告，仅用 BGM 或静音
