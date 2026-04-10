"""
Stage 9: 字幕生成 + FFmpeg 字幕烧录

支持两种字幕生成模式:
  Mode A (script): 从 storyboard.yaml 中的台词/旁白 + TTS 时长直接生成 SRT（默认）
  Mode B (asr):    调用豆包 ASR 2.0 接口进行语音识别，获取词级时间戳后生成 SRT（TODO）

用法:
    python scripts/stage9_subtitle.py --project-id test-001
    python scripts/stage9_subtitle.py --project-id test-001 --mode script
    python scripts/stage9_subtitle.py --project-id test-001 --storyboard output/test-001/scripts/storyboard.yaml
    python scripts/stage9_subtitle.py --project-id test-001 --font "Noto Sans CJK SC"
"""

import argparse
import os
import subprocess
import sys
from pathlib import Path

try:
    import yaml
except ImportError:
    yaml = None  # type: ignore[assignment]

from api_client import APIClient


# ── SRT 辅助函数 ────────────────────────────────────────────────────────────────

def seconds_to_srt_timestamp(seconds: float) -> str:
    """将秒数转换为 SRT 时间戳格式 HH:MM:SS,mmm。"""
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    secs = int(seconds % 60)
    millis = int(round((seconds - int(seconds)) * 1000))
    return f"{hours:02d}:{minutes:02d}:{secs:02d},{millis:03d}"


def build_srt(entries: list[dict]) -> str:
    """
    从字幕条目列表生成 SRT 格式字符串。

    每条 entry 格式: {"start": float, "end": float, "text": str}
    """
    lines = []
    for i, entry in enumerate(entries, start=1):
        lines.append(str(i))
        lines.append(
            f"{seconds_to_srt_timestamp(entry['start'])} --> "
            f"{seconds_to_srt_timestamp(entry['end'])}"
        )
        lines.append(entry["text"].strip())
        lines.append("")
    return "\n".join(lines)


# ── Mode A: 从 storyboard.yaml 生成字幕 ─────────────────────────────────────────

def load_storyboard(storyboard_path: str) -> list[dict]:
    """
    加载 storyboard.yaml，返回场景列表。

    期望 YAML 结构（两种常见格式均兼容）:

    格式 1 — 顶层 scenes 列表:
        scenes:
          - scene_id: 1
            dialogue: "台词内容"   # 或 narration / lines / text
            duration: 4.5         # 秒，可选

    格式 2 — 直接为列表:
        - scene_id: 1
          dialogue: "台词内容"
          duration: 4.5
    """
    if yaml is None:
        raise ImportError("PyYAML is required for Mode A. Install with: pip install pyyaml")

    with open(storyboard_path, "r", encoding="utf-8") as f:
        data = yaml.safe_load(f)

    if isinstance(data, dict):
        scenes = None
        for key in ("scenes", "分镜列表", "分镜", "storyboard"):
            if key in data and isinstance(data[key], list):
                scenes = data[key]
                break
        if scenes is None:
            scenes = []
    elif isinstance(data, list):
        scenes = data
    else:
        raise ValueError(f"Unexpected storyboard format in {storyboard_path}")

    return scenes


def extract_dialogue(scene: dict) -> str:
    """从场景 dict 中提取台词文本，兼容多种字段名。"""
    for field in ("台词", "旁白", "dialogue", "narration", "lines", "text"):
        value = scene.get(field, "")
        if value:
            return str(value).strip()
    return ""


def extract_duration(scene: dict, index: int, audio_dir: str | None = None) -> float:
    """
    从场景获取时长（秒）。

    优先级:
    1. TTS 音频实际时长（ffprobe）— 最准确，与视频对齐
    2. scene["duration"] / scene["时长"] 字段 — 回退
    3. 默认 4.0 秒
    """
    # 优先用 TTS 音频实际时长（与视频片段时长一致）
    if audio_dir:
        scene_id = scene.get("scene_id", scene.get("编号", index))
        tts_path = os.path.join(audio_dir, f"tts-{str(scene_id).zfill(2)}.mp3")
        if os.path.exists(tts_path):
            try:
                cmd = [
                    "ffprobe", "-v", "quiet",
                    "-show_entries", "format=duration",
                    "-of", "csv=p=0",
                    tts_path,
                ]
                result = subprocess.run(cmd, capture_output=True, text=True, check=True)
                return float(result.stdout.strip())
            except (subprocess.CalledProcessError, ValueError):
                pass

    # 回退到 storyboard 时长字段
    for key in ("duration", "时长"):
        if key in scene:
            raw = str(scene[key]).strip()
            if raw.endswith("秒"):
                raw = raw[:-1]
            try:
                return float(raw)
            except ValueError:
                pass

    return 4.0  # 默认时长


def generate_srt_from_script(
    storyboard_path: str,
    audio_dir: str | None = None,
    gap: float = 0.1,
) -> list[dict]:
    """
    Mode A: 从 storyboard.yaml 直接生成字幕条目列表。

    Args:
        storyboard_path: storyboard.yaml 路径
        audio_dir: TTS 音频目录（用于读取实际时长）
        gap: 字幕条目间隔（秒）

    Returns:
        字幕条目列表，每项 {"start": float, "end": float, "text": str}
    """
    scenes = load_storyboard(storyboard_path)
    entries = []
    cursor = 0.0

    for i, scene in enumerate(scenes, start=1):
        text = extract_dialogue(scene)
        if not text:
            # 无台词的场景仍计算时长以保持时间轴对齐
            duration = extract_duration(scene, i, audio_dir)
            cursor += duration
            continue

        duration = extract_duration(scene, i, audio_dir)
        entries.append({
            "start": cursor,
            "end": cursor + duration - gap,
            "text": text,
        })
        cursor += duration

    return entries


# ── Mode B: ASR（TODO） ──────────────────────────────────────────────────────────

def generate_srt_from_asr(
    video_path: str,
    audio_dir: str,
    project_dir: str,
) -> list[dict]:
    """
    Mode B: 调用豆包 ASR 2.0 接口进行语音识别生成字幕（待实现）。

    TODO:
    1. 提取视频音轨为 WAV/MP3
    2. POST 到豆包 ASR 2.0 批量识别接口
    3. 解析词级时间戳
    4. 将词级结果合并为句级字幕条目

    暂时回退到 Mode A。
    """
    raise NotImplementedError(
        "Mode B (ASR) is not yet implemented. "
        "Please use --mode script (Mode A) for now."
    )


# ── FFmpeg 字幕烧录 ─────────────────────────────────────────────────────────────

def _has_libass() -> bool:
    """检查 FFmpeg 是否支持 subtitles 过滤器（需要 libass）。"""
    try:
        result = subprocess.run(
            ["ffmpeg", "-filters"], capture_output=True, text=True, timeout=10,
        )
        return "subtitles" in result.stdout
    except Exception:
        return False


def burn_subtitles(
    input_video: str,
    srt_path: str,
    output_path: str,
    font: str = "PingFang SC",
    font_size: int = 22,
) -> str:
    """
    用 FFmpeg 将 SRT 字幕烧录到视频中。

    优先使用 subtitles 过滤器硬烧（需要 libass）；
    若 libass 不可用，回退到 mov_text 软字幕嵌入。
    """
    if _has_libass():
        # 硬烧模式（libass）
        srt_escaped = srt_path.replace("\\", "/").replace(":", "\\:")
        force_style = (
            f"FontSize={font_size},"
            f"FontName={font},"
            "PrimaryColour=&HFFFFFF,"
            "OutlineColour=&H000000,"
            "Outline=2,"
            "MarginV=30"
        )
        cmd = [
            "ffmpeg", "-y",
            "-i", input_video,
            "-vf", f"subtitles={srt_escaped}:force_style='{force_style}'",
            "-c:a", "copy",
            output_path,
        ]
        print(f"  Hard-burning subtitles (libass) → {output_path}")
    else:
        # 软字幕回退模式（mov_text）
        print(f"  Warning: libass not available, using mov_text soft subtitles")
        cmd = [
            "ffmpeg", "-y",
            "-i", input_video,
            "-i", srt_path,
            "-map", "0:v", "-map", "0:a", "-map", "1:s",
            "-c:v", "copy", "-c:a", "copy",
            "-c:s", "mov_text",
            "-movflags", "+faststart",
            output_path,
        ]
        print(f"  Embedding soft subtitles (mov_text) → {output_path}")

    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        raise RuntimeError(f"FFmpeg subtitle failed: {result.stderr[-500:]}")
    return output_path


# ── 核心流程 ────────────────────────────────────────────────────────────────────

def run_stage9(
    project_dir: str,
    mode: str = "script",
    storyboard_path: str | None = None,
    font: str = "PingFang SC",
) -> dict[str, str]:
    """
    执行 Stage 9 完整字幕生成 + 烧录流程。

    Args:
        project_dir: 项目根目录（如 output/test-001）
        mode: 字幕生成模式，"script" 或 "asr"
        storyboard_path: storyboard.yaml 路径（mode=script 时使用）
        font: 字幕字体名称

    Returns:
        {"srt_path": str, "video_path": str}
    """
    scripts_dir = os.path.join(project_dir, "scripts")
    audio_dir = os.path.join(project_dir, "audio")
    subtitles_dir = os.path.join(project_dir, "subtitles")
    videos_dir = os.path.join(project_dir, "videos")
    os.makedirs(subtitles_dir, exist_ok=True)
    os.makedirs(videos_dir, exist_ok=True)

    # 确定 storyboard 路径
    if storyboard_path is None:
        storyboard_path = os.path.join(scripts_dir, "storyboard.yaml")

    # 确定输入视频（lipsync.mp4 优先，否则 concat-mixed.mp4）
    input_video = None
    for candidate in ("lipsync.mp4", "concat-final.mp4", "concat-mixed.mp4"):
        path = os.path.join(videos_dir, candidate)
        if os.path.exists(path):
            input_video = path
            break

    if input_video is None:
        raise FileNotFoundError(
            f"No input video found in {videos_dir}. "
            "Expected lipsync.mp4 or concat-mixed.mp4."
        )

    srt_path = os.path.join(subtitles_dir, "final.srt")
    output_video = os.path.join(videos_dir, "final.mp4")

    # 生成字幕条目
    print(f"Stage 9: Generating subtitles (mode={mode}) from {storyboard_path}")

    if mode == "script":
        if not os.path.exists(storyboard_path):
            raise FileNotFoundError(f"Storyboard not found: {storyboard_path}")
        entries = generate_srt_from_script(storyboard_path, audio_dir)
    elif mode == "asr":
        entries = generate_srt_from_asr(input_video, audio_dir, project_dir)
    else:
        raise ValueError(f"Unknown mode: {mode}. Supported: script, asr")

    if not entries:
        raise ValueError("No subtitle entries generated. Check storyboard for dialogue fields.")

    # 写入 SRT
    srt_content = build_srt(entries)
    with open(srt_path, "w", encoding="utf-8") as f:
        f.write(srt_content)
    print(f"  SRT written: {srt_path} ({len(entries)} entries)")

    # 烧录字幕
    burn_subtitles(input_video, srt_path, output_video, font=font)

    print(f"Stage 9 complete:")
    print(f"  SRT:   {srt_path}")
    print(f"  Video: {output_video}")

    return {"srt_path": srt_path, "video_path": output_video}


def main():
    parser = argparse.ArgumentParser(description="Stage 9: Subtitle Generation + Burn-in")
    parser.add_argument("--project-id", required=True, help="Project ID (e.g., test-001)")
    parser.add_argument("--output-dir", default="Video-Producer-output", help="Base output directory")
    parser.add_argument(
        "--mode", default="script", choices=["script", "asr"],
        help="Subtitle generation mode: 'script' (from storyboard) or 'asr' (speech recognition, TODO)",
    )
    parser.add_argument(
        "--storyboard",
        help="Path to storyboard.yaml (default: output/{project-id}/scripts/storyboard.yaml)",
    )
    parser.add_argument(
        "--font", default="PingFang SC",
        help="Subtitle font name (default: PingFang SC)",
    )
    args = parser.parse_args()

    project_dir = os.path.join(args.output_dir, args.project_id)
    run_stage9(
        project_dir,
        mode=args.mode,
        storyboard_path=args.storyboard,
        font=args.font,
    )


if __name__ == "__main__":
    main()
