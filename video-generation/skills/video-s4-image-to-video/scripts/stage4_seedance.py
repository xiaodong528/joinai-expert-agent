"""
Stage 4: 图生视频 — Seedance 1.5 Pro (异步)

将关键帧图像生成为视频片段，使用 volcenginesdkarkruntime SDK 提交任务，
通过 ARK REST API 轮询任务状态。

用法:
    python scripts/stage4_seedance.py --project-id test-001 --scene 1
    python scripts/stage4_seedance.py --project-id test-001 --scene all
    python scripts/stage4_seedance.py --project-id test-001 --scene all --generate-audio
"""

import argparse
import base64
import os
import time
from pathlib import Path

from api_client import APIClient

MODEL_ID = "doubao-seedance-1-5-pro-251215"
POLL_INTERVAL = 5  # seconds
POLL_TIMEOUT = 300  # 5 minutes


def _read_frame_as_data_uri(frame_path: str) -> str:
    """读取本地帧图像，返回 base64 data URI。"""
    with open(frame_path, "rb") as f:
        data = f.read()
    b64 = base64.b64encode(data).decode()
    return f"data:image/png;base64,{b64}"


def _get_ark_client():
    """获取 Ark SDK 客户端单例。"""
    from volcenginesdkarkruntime import Ark

    return Ark(api_key=os.environ["ARK_API_KEY"])


def submit_video_task(
    frame_path: str,
    video_prompt: str,
    last_frame_path: str | None = None,
    generate_audio: bool = True,
    duration: int = 12,
) -> str:
    """
    提交单个图生视频任务，返回 task_id。

    支持首尾帧模式：content 数组中 2 个 image_url（首帧+尾帧）+ 1 个 text。
    Uses SDK: ark.content_generation.tasks.create()
    """
    ark = _get_ark_client()

    content: list[dict] = [
        {
            "type": "image_url",
            "image_url": {"url": _read_frame_as_data_uri(frame_path)},
            "role": "first_frame",
        },
    ]
    if last_frame_path and os.path.exists(last_frame_path):
        content.append({
            "type": "image_url",
            "image_url": {"url": _read_frame_as_data_uri(last_frame_path)},
            "role": "last_frame",
        })

    content.append({"type": "text", "text": video_prompt})

    response = ark.content_generation.tasks.create(
        model=MODEL_ID,
        content=content,
        generate_audio=generate_audio,
        duration=duration,
    )

    task_id = response.id
    if not task_id:
        raise RuntimeError(f"No task_id in Seedance response: {response}")
    return task_id


def poll_and_download_video(
    client: APIClient,
    task_id: str,
    dest_path: str,
) -> str:
    """
    轮询 Seedance 任务直到完成，下载视频文件。

    Uses SDK: ark.content_generation.tasks.get()
    """
    ark = _get_ark_client()
    deadline = time.time() + POLL_TIMEOUT

    print(f"  Polling task {task_id} (timeout={POLL_TIMEOUT}s)")
    while time.time() < deadline:
        result = ark.content_generation.tasks.get(task_id=task_id)
        status = result.status

        if status == "succeeded":
            video_url = result.content.video_url
            if not video_url:
                raise RuntimeError(f"No video_url in succeeded task: {task_id}")
            print(f"  Downloading video → {dest_path}")
            client.download(video_url, dest_path)
            return dest_path

        if status == "failed":
            error = getattr(result, "error", None)
            raise RuntimeError(f"Video task failed: task_id={task_id}, error={error}")

        time.sleep(POLL_INTERVAL)

    raise TimeoutError(f"Task {task_id} timed out after {POLL_TIMEOUT}s")


def process_scene(
    project_dir: str,
    client: APIClient,
    scene_num: int,
    video_prompt: str,
    generate_audio: bool = True,
) -> str:
    """
    处理单个 scene：查找首帧（+尾帧），提交任务、轮询、下载。

    帧查找优先级:
    - 新格式: scene-{N}-first.png + scene-{N}-last.png (首尾帧模式)
    - 旧格式: scene-{N}.png (单帧向后兼容)
    """
    frames_dir = os.path.join(project_dir, "frames")

    # 查找首帧（新格式优先，旧格式回退）
    first_path = os.path.join(frames_dir, f"scene-{scene_num:02d}-first.png")
    legacy_path = os.path.join(frames_dir, f"scene-{scene_num:02d}.png")

    if os.path.exists(first_path):
        frame_path = first_path
    elif os.path.exists(legacy_path):
        frame_path = legacy_path
    else:
        raise FileNotFoundError(f"Keyframe not found: {first_path} or {legacy_path}")

    # 查找尾帧（可选）
    last_path = os.path.join(frames_dir, f"scene-{scene_num:02d}-last.png")
    last_frame_path = last_path if os.path.exists(last_path) else None

    clips_dir = os.path.join(project_dir, "clips")
    os.makedirs(clips_dir, exist_ok=True)
    dest_path = os.path.join(clips_dir, f"scene-{scene_num:02d}.mp4")

    mode = "first+last" if last_frame_path else "first-only"
    print(f"  Scene {scene_num:02d}: submitting [{mode}]")
    task_id = submit_video_task(
        frame_path, video_prompt, last_frame_path, generate_audio
    )
    print(f"  Scene {scene_num:02d}: task_id={task_id}")

    return poll_and_download_video(client, task_id, dest_path)


def run_stage4(
    project_dir: str,
    scene: str = "all",
    generate_audio: bool = True,
    storyboard_path: str | None = None,
) -> list[str]:
    """
    执行 Stage 4 完整图生视频流程。

    Args:
        project_dir: 项目输出目录路径
        scene: 场景编号（如 "1"、"3"）或 "all" 处理全部
        generate_audio: 是否启用 AI 配乐
        storyboard_path: storyboard.yaml 路径（提取视频提示词用）；
                         为 None 时使用默认提示词

    Returns:
        生成的视频路径列表
    """
    import yaml

    # 加载分镜脚本获取视频提示词
    scene_prompts: dict[int, str] = {}
    if storyboard_path and os.path.exists(storyboard_path):
        with open(storyboard_path, encoding="utf-8") as f:
            storyboard = yaml.safe_load(f)
        for s in storyboard.get("分镜列表", storyboard.get("scenes", [])):
            num = s.get("编号", s.get("scene_number", 0))
            prompt = s.get(
                "图生视频提示词",
                s.get("video_prompt", s.get("prompt", "cinematic video, 12s")),
            )
            scene_prompts[num] = prompt

    # 确定处理的帧列表（支持新格式 -first.png 和旧格式 .png）
    frames_dir = os.path.join(project_dir, "frames")
    if scene == "all":
        scene_numbers_set: set[int] = set()
        for fp in Path(frames_dir).glob("scene-*.png"):
            stem = fp.stem  # e.g. "scene-01-first", "scene-01-last", "scene-01"
            parts = stem.split("-")
            if len(parts) >= 2:
                try:
                    scene_numbers_set.add(int(parts[1]))
                except ValueError:
                    pass
        scene_numbers = sorted(scene_numbers_set)
    else:
        scene_numbers = [int(scene)]

    if not scene_numbers:
        raise FileNotFoundError(f"No keyframes found in {frames_dir}")

    client = APIClient("ark")
    print(
        f"Stage 4: Processing {len(scene_numbers)} scene(s), generate_audio={generate_audio}"
    )

    saved_paths: list[str] = []
    for num in scene_numbers:
        video_prompt = scene_prompts.get(num, "cinematic video, smooth motion, 12s")
        clip_path = process_scene(
            project_dir, client, num, video_prompt, generate_audio
        )
        saved_paths.append(clip_path)
        print(f"  Scene {num:02d}: saved → {clip_path}")

    print(
        f"Stage 4 complete: {len(saved_paths)} clip(s) saved to {os.path.join(project_dir, 'clips')}"
    )
    return saved_paths


def main():
    parser = argparse.ArgumentParser(
        description="Stage 4: Image-to-Video via Seedance 1.5 Pro"
    )
    parser.add_argument(
        "--project-id", required=True, help="Project ID (e.g., test-001)"
    )
    parser.add_argument("--output-dir", default="Video-Producer-output", help="Base output directory")
    parser.add_argument(
        "--scene",
        default="all",
        help="Scene number to process, or 'all' for all keyframes",
    )
    parser.add_argument(
        "--generate-audio",
        action="store_true",
        help="Enable AI audio generation for the video",
    )
    parser.add_argument(
        "--storyboard",
        default=None,
        help="Path to storyboard.yaml for video prompts",
    )
    args = parser.parse_args()

    project_dir = os.path.join(args.output_dir, args.project_id)

    # 默认 storyboard 路径
    storyboard_path = args.storyboard
    if storyboard_path is None:
        default_sb = os.path.join(project_dir, "scripts", "storyboard.yaml")
        if os.path.exists(default_sb):
            storyboard_path = default_sb

    run_stage4(
        project_dir,
        scene=args.scene,
        generate_audio=args.generate_audio,
        storyboard_path=storyboard_path,
    )


if __name__ == "__main__":
    main()
