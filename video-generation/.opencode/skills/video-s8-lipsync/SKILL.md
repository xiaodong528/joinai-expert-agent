---
name: video-s8-lipsync
description: "可灵 Lip-Sync API，支持 10 秒分段拆分处理。Triggers on lip sync, Kling, mouth sync."
---

# Stage 8: 对口型处理 (Optional, Async)

**用途**

## 依赖

- `.opencode/skills/video-s8-lipsync/scripts/` 下脚本、模型说明和当前 Stage 输入文件。

## 输入契约

- 见下方 `## 输入/输出契约` 详细说明。

## 输出契约

- 见下方 `## 输入/输出契约` 详细说明。

## 执行流程

1. 读取 `Video-Producer-output/{project_id}` 下当前 Stage 需要的输入。
2. 按下文脚本命令或规则执行当前 Stage。
3. 核对输出文件后再进入验证清单。

使用可灵 Lip-Sync API 对包含面部特写和对白的视频片段进行口型同步处理。超过 10 秒的场景必须先拆分、逐段处理，再重新拼接。

## 脚本

```
.opencode/skills/video-s8-lipsync/scripts/stage8_lipsync.py
```

## 输入/输出契约

| 项目 | 路径 | 说明 |
|------|------|------|
| 输入视频 | `Video-Producer-output/{project_id}/videos/concat-raw.mp4` | 或单场景片段 |
| TTS 音频 | `Video-Producer-output/{project_id}/audio/tts-{01..N}.mp3` | 对白音频 |
| **输出** | `Video-Producer-output/{project_id}/videos/lipsync.mp4` | 口型同步后的视频 |

**仅对以下场景应用**：面部特写镜头 + 有对白台词。跳过远景或无对白场景。

## 认证：可灵 JWT

可灵使用双密钥 JWT 认证方式，与流水线中其他所有 API 不同。

```python
import jwt, time

def generate_kling_token(access_key: str, secret_key: str) -> str:
    payload = {
        "iss": access_key,
        "exp": int(time.time()) + 1800,  # 30 min expiry
        "nbf": int(time.time()) - 5,
    }
    return jwt.encode(payload, secret_key, algorithm="HS256")

headers = {
    "Authorization": f"Bearer {generate_kling_token(KLING_ACCESS_KEY, KLING_SECRET_KEY)}",
    "Content-Type": "application/json",
}
```

环境变量：`KLING_ACCESS_KEY`、`KLING_SECRET_KEY`

## 关键：10 秒分段限制

可灵 Lip-Sync 会拒绝超过 10 秒的片段。需通过拆分-处理-重新拼接的方式解决：

```python
# 1. Check duration
duration = get_video_duration(clip_path)  # via ffprobe

# 2. Split if needed
if duration > 10.0:
    segments = split_video(clip_path, max_duration=10.0)
    tts_segments = split_audio(tts_path, max_duration=10.0)
else:
    segments = [clip_path]
    tts_segments = [tts_path]

# 3. Process each segment
synced_segments = [lipsync_segment(v, a) for v, a in zip(segments, tts_segments)]

# 4. Re-join segments
ffmpeg_concat(synced_segments, output_path)
```

## 异步 API 流程

```
POST api.klingai.com/v1/videos/lip-sync   →  task_id
  poll every 5s (timeout: 10min)
  GET api.klingai.com/v1/videos/lip-sync/{task_id}
    status: submitted | processing | succeed | failed
  download video_url on succeed
```

### 提交请求

```python
payload = {
    "model_name": "kling-v1-6",
    "video_url": presigned_video_url,
    "audio_url": presigned_audio_url,
}
resp = requests.post(
    "https://api.klingai.com/v1/videos/lip-sync",
    json=payload, headers=headers
)
task_id = resp.json()["data"]["task_id"]
```

### 轮询完成

```python
import time

def poll_lipsync(task_id: str, headers: dict, timeout: int = 600) -> str:
    start = time.time()
    while time.time() - start < timeout:
        r = requests.get(
            f"https://api.klingai.com/v1/videos/lip-sync/{task_id}",
            headers=headers
        )
        data = r.json()["data"]
        if data["status"] == "succeed":
            return data["video_url"]
        if data["status"] == "failed":
            raise RuntimeError(f"Lip-sync failed: {data.get('message')}")
        time.sleep(5)
    raise TimeoutError(f"Lip-sync timed out after {timeout}s")
```

## 关键参数

| 参数 | 值 |
|------|-----|
| 模型 | `kling-v1-6` |
| 最大分段时长 | 10s（硬限制） |
| 轮询间隔 | 5s |
| 超时时间 | 10 min (600s) |
| JWT 有效期 | 1800s / 每令牌 |

## 验证清单

- [ ] 源片段 > 10s 时，所有分段均已单独处理
- [ ] 重新拼接后的输出在分段边界处无音视频不同步
- [ ] 全程口型-音频同步延迟 < 200ms
- [ ] 无可见的面部变形或扭曲伪影
- [ ] 输出编码为 H.264 + AAC
- [ ] `lipsync.mp4` 时长与输入视频时长误差 <= 0.5s

## 错误处理

- API 401：重新生成 JWT 令牌（可能已过期）
- 提交了 > 10s 的分段：提交前需预先校验并拆分
- `failed` 状态：记录失败原因，回退使用未经 Lip-Sync 处理的原始片段
- 下载失败：最多重试 3 次，采用指数退避策略
