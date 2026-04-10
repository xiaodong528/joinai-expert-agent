"""
Stage 8: 对口型 — 可灵 (Kling) Lip-Sync API (异步)

将视频片段与 TTS 语音做口型对齐。

限制: 可灵单次 Lip-Sync 最长支持 10 秒视频，超长片段需拆段处理后重新拼接。

用法:
    python scripts/stage8_lipsync.py --project-id test-001 --scene 1
    python scripts/stage8_lipsync.py --project-id test-001 --scene all
    python scripts/stage8_lipsync.py --project-id test-001 --scene 1 --max-segment 8
"""

import argparse
import os
import subprocess
from pathlib import Path

from api_client import APIClient
from async_poller import poll_with_config

# ── 常量 ───────────────────────────────────────────────────────────────────────

KLING_LIPSYNC_SUBMIT = "/videos/lip-sync"
KLING_LIPSYNC_POLL = "/videos/lip-sync/{task_id}"


# ── FFmpeg 辅助函数 ─────────────────────────────────────────────────────────────

def get_video_duration(video_path: str) -> float:
    """用 ffprobe 获取视频时长（秒）。"""
    cmd = [
        "ffprobe", "-v", "quiet",
        "-show_entries", "format=duration",
        "-of", "csv=p=0",
        video_path,
    ]
    result = subprocess.run(cmd, capture_output=True, text=True, check=True)
    return float(result.stdout.strip())


def split_video_segments(video_path: str, max_duration: float = 10.0) -> list[str]:
    """
    将视频切分为不超过 max_duration 秒的片段。

    若总时长 <= max_duration 则返回原路径（不做切分）。

    Returns:
        片段文件路径列表（升序排列）
    """
    duration = get_video_duration(video_path)
    if duration <= max_duration:
        return [video_path]

    base = Path(video_path)
    seg_dir = base.parent / f"{base.stem}_segments"
    seg_dir.mkdir(parents=True, exist_ok=True)

    segment_paths = []
    start = 0.0
    idx = 0
    while start < duration:
        seg_path = str(seg_dir / f"seg-{idx:03d}.mp4")
        cmd = [
            "ffmpeg", "-y",
            "-ss", str(start),
            "-i", video_path,
            "-t", str(max_duration),
            "-c", "copy",
            seg_path,
        ]
        subprocess.run(cmd, check=True, capture_output=True)
        segment_paths.append(seg_path)
        start += max_duration
        idx += 1

    print(f"  Split into {len(segment_paths)} segments (<= {max_duration}s each)")
    return segment_paths


def join_video_segments(segments: list[str], output_path: str) -> str:
    """
    将多个视频片段按顺序拼接为一个文件。

    Returns:
        输出文件路径
    """
    if len(segments) == 1:
        # 单片段，直接复制
        subprocess.run(
            ["ffmpeg", "-y", "-i", segments[0], "-c", "copy", output_path],
            check=True, capture_output=True,
        )
        return output_path

    filelist_path = output_path + ".segments.txt"
    with open(filelist_path, "w") as f:
        for seg in segments:
            f.write(f"file '{os.path.abspath(seg)}'\n")

    cmd = [
        "ffmpeg", "-y",
        "-f", "concat", "-safe", "0",
        "-i", filelist_path,
        "-c", "copy",
        output_path,
    ]
    subprocess.run(cmd, check=True, capture_output=True)
    os.remove(filelist_path)
    print(f"  Joined {len(segments)} segments → {output_path}")
    return output_path


# ── Kling API 调用 ──────────────────────────────────────────────────────────────

def submit_lipsync(client: APIClient, video_url: str, audio_url: str) -> str:
    """
    提交 Lip-Sync 任务。

    Args:
        video_url: 可公开访问的视频 URL
        audio_url: 可公开访问的音频 URL

    Returns:
        task_id
    """
    payload = {
        "input": {
            "video_url": video_url,
            "audio_url": audio_url,
            "mode": "audio2video",
        }
    }
    resp = client.post(KLING_LIPSYNC_SUBMIT, json=payload)
    data = resp.json()
    task_id = data.get("data", {}).get("task_id")
    if not task_id:
        raise RuntimeError(f"Lip-Sync submit failed, no task_id in response: {data}")
    print(f"  Submitted Lip-Sync task: {task_id}")
    return task_id


def poll_lipsync(client: APIClient, task_id: str) -> str:
    """
    轮询 Lip-Sync 任务直到完成，返回结果视频 URL。
    """
    poll_url = KLING_LIPSYNC_POLL.format(task_id=task_id)
    result = poll_with_config(client, poll_url, config_name="kling_lipsync")

    # 从嵌套结构中提取视频 URL
    works = result.get("data", {}).get("task_result", {}).get("videos", [])
    if not works:
        raise RuntimeError(f"No video URL in Lip-Sync result: {result}")
    return works[0].get("url", "")


# ── 本地文件 URL 占位 ────────────────────────────────────────────────────────────

def resolve_public_url(local_path: str) -> str:
    """
    将本地文件路径转换为可公开访问的 URL。

    NOTE: 可灵 API 要求视频/音频 URL 必须可公网访问。
    实际部署时需在此处实现文件上传逻辑（如上传到 OSS/S3/CDN）。
    当前实现仅做路径透传，供本地测试或已有 URL 时使用。
    """
    if local_path.startswith("http://") or local_path.startswith("https://"):
        return local_path
    # TODO: 实现上传到对象存储并返回公开 URL
    raise NotImplementedError(
        f"Local file '{local_path}' cannot be used directly with Kling API. "
        "Please upload it to a publicly accessible URL (e.g., OSS/S3) first, "
        "then pass the URL via --video-url / --audio-url."
    )


# ── 核心流程 ────────────────────────────────────────────────────────────────────

def lipsync_single_scene(
    client: APIClient,
    video_path: str,
    audio_path: str,
    output_path: str,
    max_segment: float = 10.0,
    video_url: str | None = None,
    audio_url: str | None = None,
) -> str:
    """
    对单个场景执行 Lip-Sync（含自动拆段/合并）。

    Args:
        video_url / audio_url: 若提供则跳过本地文件解析，直接使用 URL。
    """
    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    v_url = video_url or resolve_public_url(video_path)
    a_url = audio_url or resolve_public_url(audio_path)

    duration = get_video_duration(video_path) if os.path.exists(video_path) else max_segment + 1

    if duration <= max_segment:
        # 单段直接处理
        task_id = submit_lipsync(client, v_url, a_url)
        result_url = poll_lipsync(client, task_id)
        client.download(result_url, output_path)
        print(f"  Lip-Sync complete: {output_path}")
        return output_path

    # 超长: 拆段 → 逐段处理 → 合并
    print(f"  Video duration {duration:.1f}s > {max_segment}s, splitting...")
    segments = split_video_segments(video_path, max_segment)

    synced_segments = []
    seg_dir = Path(output_path).parent / f"{Path(output_path).stem}_segs"
    seg_dir.mkdir(parents=True, exist_ok=True)

    for i, seg_path in enumerate(segments):
        seg_v_url = resolve_public_url(seg_path)
        seg_out = str(seg_dir / f"synced-{i:03d}.mp4")
        print(f"  Processing segment {i + 1}/{len(segments)}: {seg_path}")
        task_id = submit_lipsync(client, seg_v_url, a_url)
        result_url = poll_lipsync(client, task_id)
        client.download(result_url, seg_out)
        synced_segments.append(seg_out)

    return join_video_segments(synced_segments, output_path)


def run_stage8(
    project_dir: str,
    scene: str = "all",
    max_segment: float = 10.0,
    video_url: str | None = None,
    audio_url: str | None = None,
) -> str:
    """
    执行 Stage 8 完整 Lip-Sync 流程。

    Args:
        project_dir: 项目根目录（如 output/test-001）
        scene: 场景编号字符串（如 "1", "2"）或 "all"
        max_segment: 单段最大时长（秒，默认 10）
        video_url: 直接提供视频 URL（覆盖本地文件解析）
        audio_url: 直接提供音频 URL（覆盖本地文件解析）

    Returns:
        输出视频路径
    """
    clips_dir = os.path.join(project_dir, "clips")
    audio_dir = os.path.join(project_dir, "audio")
    videos_dir = os.path.join(project_dir, "videos")
    os.makedirs(videos_dir, exist_ok=True)

    client = APIClient("kling")

    if scene == "all":
        # 处理所有场景，最终拼接为 lipsync.mp4
        video_files = sorted(Path(clips_dir).glob("scene-*-tts-sub.mp4"))
        if not video_files:
            video_files = sorted(Path(clips_dir).glob("scene-*.mp4"))
        if not video_files:
            raise FileNotFoundError(f"No scene-*.mp4 found in {clips_dir}")

        synced_clips = []
        for vf in video_files:
            scene_num = vf.stem.split("-")[1]
            audio_path = os.path.join(audio_dir, f"tts-{scene_num}.mp3")
            seg_out = os.path.join(videos_dir, f"lipsync-scene-{scene_num}.mp4")

            print(f"Stage 8: Processing scene {scene_num}")
            lipsync_single_scene(
                client, str(vf), audio_path, seg_out,
                max_segment=max_segment,
                video_url=video_url,
                audio_url=audio_url,
            )
            synced_clips.append(seg_out)

        output_path = os.path.join(videos_dir, "lipsync.mp4")
        if len(synced_clips) > 1:
            join_video_segments(synced_clips, output_path)
        else:
            subprocess.run(
                ["ffmpeg", "-y", "-i", synced_clips[0], "-c", "copy", output_path],
                check=True, capture_output=True,
            )
    else:
        # 单场景
        scene_num = scene.zfill(2)
        tts_sub_path = os.path.join(clips_dir, f"scene-{scene_num}-tts-sub.mp4")
        plain_path = os.path.join(clips_dir, f"scene-{scene_num}.mp4")
        video_path = tts_sub_path if os.path.exists(tts_sub_path) else plain_path
        audio_path = os.path.join(audio_dir, f"tts-{scene_num}.mp3")
        output_path = os.path.join(videos_dir, "lipsync.mp4")

        if not os.path.exists(video_path):
            raise FileNotFoundError(f"Video not found: {video_path}")

        print(f"Stage 8: Processing scene {scene_num}")
        lipsync_single_scene(
            client, video_path, audio_path, output_path,
            max_segment=max_segment,
            video_url=video_url,
            audio_url=audio_url,
        )

    print(f"Stage 8 complete: {output_path}")
    return output_path


def main():
    parser = argparse.ArgumentParser(description="Stage 8: Kling Lip-Sync")
    parser.add_argument("--project-id", required=True, help="Project ID (e.g., test-001)")
    parser.add_argument("--output-dir", default="Video-Producer-output", help="Base output directory")
    parser.add_argument(
        "--scene", default="all",
        help="Scene number (e.g., 1) or 'all' (default: all)",
    )
    parser.add_argument(
        "--max-segment", type=float, default=10.0,
        help="Max segment duration in seconds for Kling 10s limit (default: 10)",
    )
    parser.add_argument(
        "--video-url",
        help="Publicly accessible video URL (bypasses local file resolution)",
    )
    parser.add_argument(
        "--audio-url",
        help="Publicly accessible audio URL (bypasses local file resolution)",
    )
    args = parser.parse_args()

    project_dir = os.path.join(args.output_dir, args.project_id)
    run_stage8(
        project_dir,
        scene=args.scene,
        max_segment=args.max_segment,
        video_url=args.video_url,
        audio_url=args.audio_url,
    )


if __name__ == "__main__":
    main()
