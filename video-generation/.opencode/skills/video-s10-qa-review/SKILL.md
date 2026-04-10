---
name: video-s10-qa-review
description: "ffprobe 技术 QA 检查与结构化 JSON 报告生成。Triggers on QA review, ffprobe, quality check."
---

# Stage 10: 质量审查

**用途**

## 依赖

- `.opencode/skills/video-s10-qa-review/scripts/` 下脚本、模型说明和当前 Stage 输入文件。

## 输入契约

- 见下方 `## 输入/输出契约` 详细说明。

## 输出契约

- 见下方 `## 输入/输出契约` 详细说明。

## 执行流程

1. 读取 `Video-Producer-output/{project_id}` 下当前 Stage 需要的输入。
2. 按下文脚本命令或规则执行当前 Stage。
3. 核对输出文件后再进入验证清单。

通过 `ffprobe` 运行自动化技术检查，并对最终视频进行 LLM 辅助内容审查。生成结构化 JSON 报告，为每个检查点提供 PASS/WARN/FAIL 状态。

## 脚本

```
.opencode/skills/video-s10-qa-review/scripts/stage10_qa.py
```

## 输入/输出契约

| 项目 | 路径 | 说明 |
|------|------|------|
| 最终视频 | `Video-Producer-output/{project_id}/videos/final.mp4` | 主要输入 |
| 分镜脚本 | `Video-Producer-output/{project_id}/scripts/storyboard.yaml` | 用于字幕检查的预期对白 |
| SRT 文件 | `Video-Producer-output/{project_id}/subtitles/drama.srt` | 可选 - 用于字幕准确性检查 |
| **输出** | `Video-Producer-output/{project_id}/qa-report.json` | 结构化 QA 结果 |

## 自动化检查 (ffprobe)

```python
import subprocess, json

def run_ffprobe(video_path: str) -> dict:
    cmd = [
        "ffprobe", "-v", "quiet",
        "-print_format", "json",
        "-show_streams", "-show_format",
        video_path
    ]
    result = subprocess.run(cmd, capture_output=True, text=True, check=True)
    return json.loads(result.stdout)

def check_black_frames(video_path: str) -> list[float]:
    """Returns timestamps of detected black frames."""
    cmd = [
        "ffprobe", "-f", "lavfi",
        "-i", f"movie={video_path},blackdetect=d=0.1:pix_th=0.10",
        "-show_entries", "tags=lavfi.black_start,lavfi.black_end",
        "-of", "json", "-v", "quiet"
    ]
    result = subprocess.run(cmd, capture_output=True, text=True)
    # parse black_start entries from output
    return parse_black_frame_timestamps(result.stdout)
```

## 9 项 QA 检查清单

| # | 检查项 | 工具 | 通过标准 |
|---|--------|------|----------|
| 1 | 分辨率 | ffprobe | >= 720p (width >= 1280 或 height >= 720) |
| 2 | 时长 | ffprobe | >= 10s 且与预期值误差 <= 2s |
| 3 | Codec | ffprobe | 视频: H.264, 音频: AAC |
| 4 | 无黑帧 | ffprobe blackdetect | 无 > 0.1s 的黑帧事件 |
| 5 | 角色一致性 | LLM (帧采样) | 各场景中角色外观保持一致 |
| 6 | 时序连贯性 | LLM (帧采样) | 场景转换流畅，无突兀跳跃 |
| 7 | 口型同步质量 | LLM (帧采样) | 唇部动作与语音节奏明显匹配 |
| 8 | 字幕准确性 | LLM + SRT | 文字与对白匹配率 >= 95% |
| 9 | 音频平衡 | ffprobe + LLM | 人声清晰可辨，BGM 不喧宾夺主 |

## QA 报告格式

```json
{
  "project_id": "proj_abc123",
  "video_path": "Video-Producer-output/proj_abc123/videos/final.mp4",
  "generated_at": "2026-03-21T10:00:00Z",
  "overall": "pass",
  "checks": {
    "resolution": {
      "status": "pass",
      "value": "1920x1080",
      "expected": ">= 1280x720"
    },
    "duration": {
      "status": "pass",
      "value": 47.3,
      "expected": "45.0 ± 2s"
    },
    "codec": {
      "status": "pass",
      "value": {"video": "h264", "audio": "aac"}
    },
    "no_black_frames": {
      "status": "warn",
      "value": [{"start": 12.3, "end": 12.5}],
      "note": "1 black frame event at transition"
    },
    "character_consistency": {
      "status": "pass",
      "llm_summary": "Character appearance consistent across all 5 scenes"
    },
    "temporal_coherence": {
      "status": "pass",
      "llm_summary": "Scene transitions smooth, narrative progression coherent"
    },
    "lipsync_quality": {
      "status": "pass",
      "llm_summary": "Lip movements match speech within acceptable range"
    },
    "subtitle_accuracy": {
      "status": "pass",
      "match_rate": 0.98
    },
    "audio_balance": {
      "status": "pass",
      "llm_summary": "Voice dominant, BGM at appropriate background level"
    }
  }
}
```

## 总体状态逻辑

```python
def compute_overall(checks: dict) -> str:
    statuses = [c["status"] for c in checks.values()]
    if "fail" in statuses:
        return "fail"
    if "warn" in statuses:
        return "warn"
    return "pass"
```

## LLM 审查: 帧采样

```python
def sample_frames(video_path: str, count: int = 5) -> list[str]:
    """Extract N evenly-spaced frames as base64 PNG for LLM review."""
    duration = get_duration(video_path)
    timestamps = [duration * i / (count - 1) for i in range(count)]
    frames = []
    for ts in timestamps:
        cmd = ["ffmpeg", "-ss", str(ts), "-i", video_path,
               "-frames:v", "1", "-f", "image2pipe", "-vcodec", "png", "pipe:1"]
        result = subprocess.run(cmd, capture_output=True)
        frames.append(base64.b64encode(result.stdout).decode())
    return frames
```

## 验证清单

- [ ] `qa-report.json` 是有效 JSON 且包含全部 9 项检查
- [ ] `overall` 字段正确反映最差检查状态
- [ ] ffprobe 检查完成且无子进程错误
- [ ] LLM 帧采样覆盖视频的开头、中间和结尾
- [ ] 报告包含 `generated_at` ISO 时间戳
- [ ] 任何 `fail` 或 `warn` 状态均包含可读的 `note` 或 `llm_summary`

## 错误处理

- ffprobe 未找到: 抛出 `EnvironmentError` 并附安装说明
- LLM API 调用失败: 将 LLM 依赖的检查项标记为 `status: "skipped"`，继续执行
- 视频文件缺失: 中止并给出明确错误信息，不生成不完整的报告
- 黑帧检测解析错误: 记录警告日志，将该检查项标记为 `warn`
