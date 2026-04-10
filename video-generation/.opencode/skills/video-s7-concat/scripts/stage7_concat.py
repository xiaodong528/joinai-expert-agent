"""
Stage 7: 视频拼接 + 音频混合 (FFmpeg)

将多个视频片段拼接为一个完整视频，可选混合 TTS 语音和 BGM 音轨。

用法:
    python scripts/stage7_concat.py --project-id test-001
    python scripts/stage7_concat.py --project-id test-001 --with-bgm --with-tts
"""

import argparse
import json
import os
import subprocess
import sys
from pathlib import Path


def find_clips(clips_dir: str) -> list[str]:
    """
    按编号排序查找视频片段。

    优先使用 scene-{N}-tts-sub.mp4（含旁白+字幕），
    回退到 scene-{N}.mp4（原始片段）。
    不会同时包含同一场景的两个版本。
    """
    clips_path = Path(clips_dir)

    # 收集所有场景编号
    scene_nums: set[str] = set()
    for f in clips_path.glob("scene-*.mp4"):
        parts = f.stem.split("-")
        if len(parts) >= 2:
            scene_nums.add(parts[1])  # e.g. "01", "02"

    if not scene_nums:
        raise FileNotFoundError(f"No scene-*.mp4 found in {clips_dir}")

    # 每个场景选择最佳版本：-tts-sub 优先
    clips = []
    for num in sorted(scene_nums):
        tts_sub = clips_path / f"scene-{num}-tts-sub.mp4"
        original = clips_path / f"scene-{num}.mp4"
        if tts_sub.exists():
            clips.append(str(tts_sub))
        elif original.exists():
            clips.append(str(original))

    return clips


def _get_duration(file_path: str) -> float:
    """用 ffprobe 获取文件时长（秒）。"""
    result = subprocess.run(
        ["ffprobe", "-v", "quiet", "-print_format", "json",
         "-show_format", file_path],
        capture_output=True, text=True, timeout=10,
    )
    import json as _json
    data = _json.loads(result.stdout)
    return float(data.get("format", {}).get("duration", 0.0))


def _parse_srt_time(time_str: str) -> float:
    """SRT 时间 HH:MM:SS,mmm → 秒。"""
    parts = time_str.replace(",", ".").split(":")
    return float(parts[0]) * 3600 + float(parts[1]) * 60 + float(parts[2])


def _format_srt_time(seconds: float) -> str:
    """秒 → SRT 时间 HH:MM:SS,mmm。"""
    h = int(seconds // 3600)
    m = int((seconds % 3600) // 60)
    s = seconds % 60
    ms = int((s - int(s)) * 1000)
    return f"{h:02d}:{m:02d}:{int(s):02d},{ms:03d}"


def merge_subtitles(clips: list[str], subtitles_dir: str, output_path: str) -> str | None:
    """
    合并各场景 SRT 字幕文件，根据片段时长偏移时间戳。

    Returns:
        合并后的 SRT 文件路径，无字幕文件则返回 None
    """
    combined_lines = []
    entry_num = 1
    time_offset = 0.0

    for clip_path in clips:
        # 从 clip 文件名提取场景编号: scene-01-tts-sub.mp4 → 01
        stem = Path(clip_path).stem  # scene-01-final or scene-01
        scene_num = stem.split("-")[1]  # 01

        srt_path = os.path.join(subtitles_dir, f"scene-{scene_num}.srt")
        if not os.path.exists(srt_path):
            # 该场景无字幕，仅累加时间偏移
            time_offset += _get_duration(clip_path)
            continue

        with open(srt_path, encoding="utf-8") as f:
            content = f.read().strip()

        if not content:
            time_offset += _get_duration(clip_path)
            continue

        # 解析 SRT 条目
        blocks = content.split("\n\n")
        for block in blocks:
            lines = block.strip().split("\n")
            if len(lines) < 3:
                continue

            # 解析时间行: 00:00:00,000 --> 00:00:05,960
            time_line = lines[1]
            start_str, end_str = time_line.split(" --> ")
            start = _parse_srt_time(start_str) + time_offset
            end = _parse_srt_time(end_str) + time_offset
            text = "\n".join(lines[2:])

            combined_lines.append(str(entry_num))
            combined_lines.append(f"{_format_srt_time(start)} --> {_format_srt_time(end)}")
            combined_lines.append(text)
            combined_lines.append("")
            entry_num += 1

        time_offset += _get_duration(clip_path)

    if not combined_lines:
        return None

    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        f.write("\n".join(combined_lines))

    print(f"  Subtitles merged: {entry_num - 1} entries → {output_path}")
    return output_path


def create_filelist(clips: list[str], output_path: str) -> str:
    """生成 FFmpeg concat 所需的 filelist.txt。"""
    with open(output_path, "w") as f:
        for clip in clips:
            f.write(f"file '{os.path.abspath(clip)}'\n")
    return output_path


def concat_videos(filelist: str, output_path: str) -> str:
    """拼接视频片段（无音频处理）。"""
    cmd = [
        "ffmpeg", "-y",
        "-f", "concat", "-safe", "0",
        "-i", filelist,
        "-c", "copy",
        output_path,
    ]
    print(f"  Concatenating videos → {output_path}")
    subprocess.run(cmd, check=True, capture_output=True)
    return output_path


def combine_tts_audio(audio_dir: str, output_path: str) -> str:
    """按顺序拼接 TTS 音频文件。"""
    tts_files = sorted(Path(audio_dir).glob("tts-*.mp3"))
    if not tts_files:
        raise FileNotFoundError(f"No tts-*.mp3 found in {audio_dir}")

    filelist_path = os.path.join(os.path.dirname(output_path), "tts-filelist.txt")
    with open(filelist_path, "w") as f:
        for tf in tts_files:
            f.write(f"file '{os.path.abspath(tf)}'\n")

    cmd = [
        "ffmpeg", "-y",
        "-f", "concat", "-safe", "0",
        "-i", filelist_path,
        "-c", "copy",
        output_path,
    ]
    subprocess.run(cmd, check=True, capture_output=True)
    return output_path


def mix_audio_tracks(
    video_path: str,
    output_path: str,
    tts_path: str | None = None,
    bgm_path: str | None = None,
    bgm_volume: float = 0.15,
) -> str:
    """
    混合视频原声、TTS 语音和 BGM 音轨。

    始终保留视频自带音轨 [0:a]（可能包含 Seedance 环境音效 + 已嵌入的 TTS）。
    额外的 TTS 和 BGM 作为附加音轨混入。
    """
    inputs = ["-i", video_path]
    # 始终包含视频自带音轨
    filter_parts = ["[0:a]volume=1.0[va]"]
    mix_inputs = ["[va]"]
    input_idx = 1

    if tts_path:
        inputs.extend(["-i", tts_path])
        filter_parts.append(f"[{input_idx}:a]volume=1.0[voice]")
        mix_inputs.append("[voice]")
        input_idx += 1

    if bgm_path:
        inputs.extend(["-i", bgm_path])
        filter_parts.append(f"[{input_idx}:a]volume={bgm_volume}[bgm]")
        mix_inputs.append("[bgm]")
        input_idx += 1

    if len(mix_inputs) == 1 and not tts_path and not bgm_path:
        # 无额外音轨，直接复制
        cmd = ["ffmpeg", "-y", "-i", video_path, "-c", "copy", output_path]
        subprocess.run(cmd, check=True, capture_output=True)
        return output_path

    # 混合音轨（视频原声 + TTS + BGM）
    n_inputs = len(mix_inputs)
    mix_filter = ";".join(filter_parts)
    mix_filter += f";{''.join(mix_inputs)}amix=inputs={n_inputs}:duration=first[aout]"

    cmd = [
        "ffmpeg", "-y",
        *inputs,
        "-filter_complex", mix_filter,
        "-map", "0:v",
        "-map", "[aout]",
        "-c:v", "copy",
        "-c:a", "aac",
        "-b:a", "192k",
        output_path,
    ]
    print(f"  Mixing audio ({n_inputs} tracks) → {output_path}")
    subprocess.run(cmd, check=True, capture_output=True)
    return output_path


def run_stage7(
    project_dir: str,
    with_tts: bool = False,
    with_bgm: bool = False,
    bgm_volume: float = 0.15,
) -> str:
    """执行 Stage 7 完整流程。"""
    clips_dir = os.path.join(project_dir, "clips")
    audio_dir = os.path.join(project_dir, "audio")
    videos_dir = os.path.join(project_dir, "videos")
    os.makedirs(videos_dir, exist_ok=True)

    # 1. 查找并拼接视频
    clips = find_clips(clips_dir)
    print(f"Stage 7: Found {len(clips)} clips")

    filelist = create_filelist(clips, os.path.join(videos_dir, "filelist.txt"))
    raw_video = concat_videos(filelist, os.path.join(videos_dir, "concat-raw-silent.mp4"))

    # 2. 准备 TTS 合并音频（仅当片段未嵌入 TTS 时）
    clips_have_tts = all("tts-sub" in os.path.basename(c) for c in clips)
    tts_path = None
    if with_tts and not clips_have_tts:
        tts_combined = os.path.join(audio_dir, "tts-combined.mp3")
        tts_path = combine_tts_audio(audio_dir, tts_combined)
        print(f"  TTS combined: {tts_path}")
    elif with_tts and clips_have_tts:
        print("  TTS already embedded in -tts-sub clips, skipping separate TTS mix")

    # 3. BGM 路径
    bgm_path = None
    if with_bgm:
        bgm_candidate = os.path.join(audio_dir, "bgm.mp3")
        if os.path.exists(bgm_candidate):
            bgm_path = bgm_candidate
            print(f"  BGM: {bgm_path}")
        else:
            print(f"  Warning: BGM requested but {bgm_candidate} not found, skipping")

    # 4. 混合音轨
    mixed_path = os.path.join(videos_dir, "concat-mixed.mp4")
    mix_audio_tracks(raw_video, mixed_path, tts_path, bgm_path, bgm_volume)

    # 5. 合并字幕并嵌入到最终视频
    subtitles_dir = os.path.join(project_dir, "subtitles")
    combined_srt = os.path.join(subtitles_dir, "combined.srt")
    srt_path = merge_subtitles(clips, subtitles_dir, combined_srt)

    if srt_path:
        output_path = os.path.join(videos_dir, "concat-final.mp4")
        cmd = [
            "ffmpeg", "-y",
            "-i", mixed_path,
            "-i", srt_path,
            "-map", "0:v", "-map", "0:a", "-map", "1:s",
            "-c:v", "copy", "-c:a", "copy", "-c:s", "mov_text",
            "-movflags", "+faststart",
            output_path,
        ]
        print(f"  Embedding subtitles → {output_path}")
        subprocess.run(cmd, check=True, capture_output=True)
    else:
        output_path = mixed_path
        print("  No subtitles found, skipping embed")

    print(f"Stage 7 complete: {output_path}")
    return output_path


def main():
    parser = argparse.ArgumentParser(description="Stage 7: Video Concatenation + Audio Mixing")
    parser.add_argument("--project-id", required=True, help="Project ID (e.g., test-001)")
    parser.add_argument("--output-dir", default="Video-Producer-output", help="Base output directory")
    parser.add_argument("--with-tts", action="store_true", help="Include TTS audio")
    parser.add_argument("--with-bgm", action="store_true", help="Include BGM audio")
    parser.add_argument("--bgm-volume", type=float, default=0.15, help="BGM volume (0.0-1.0)")
    args = parser.parse_args()

    project_dir = os.path.join(args.output_dir, args.project_id)
    run_stage7(project_dir, args.with_tts, args.with_bgm, args.bgm_volume)


if __name__ == "__main__":
    main()
