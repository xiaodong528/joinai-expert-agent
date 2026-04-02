"""
Stage 5: TTS 语音合成 + 字幕生成 (豆包语音合成 2.0 大模型，V3 异步长文本 API)

从分镜脚本中提取每个场景的台词/旁白，调用豆包语音合成 2.0 异步 API 合成语音，
同时通过 enable_timestamp 获取字幕时间戳，生成 SRT 文件，并嵌入到对应视频片段中。

输出:
  audio/tts-{01..N}.mp3        — 每个场景的语音文件
  subtitles/scene-{01..N}.srt  — 每个场景的字幕文件
  clips/scene-{01..N}-tts-sub.mp4 — 带旁白+字幕的视频片段
  audio/tts-manifest.json      — 时长清单（供 Stage 7 对齐）

用法:
    python stage5_tts.py --project-id test-001 --storyboard output/test-001/scripts/storyboard.yaml
    python stage5_tts.py --project-id test-001 --storyboard ... --speaker zh_male_ruyayichen_uranus_bigtts
    python stage5_tts.py --project-id test-001 --storyboard ... --dry-run
"""

import argparse
import json
import os
import shutil
import subprocess
import time
import uuid

import requests
import yaml

# 豆包语音合成 2.0 大模型 — V3 异步长文本端点
TTS_SUBMIT_URL = "https://openspeech.bytedance.com/api/v3/tts/submit"
TTS_QUERY_URL = "https://openspeech.bytedance.com/api/v3/tts/query"
TTS_RESOURCE_ID = "seed-tts-2.0"

POLL_INTERVAL = 3  # seconds
POLL_TIMEOUT = 120  # seconds


def _get_tts_credentials() -> tuple[str, str]:
    """加载 TTS 认证凭据。"""
    app_id = os.environ.get("TTS_APP_ID", "")
    token = os.environ.get("TTS_TOKEN", "") or os.environ.get("ARK_API_KEY", "")

    if not app_id:
        raise EnvironmentError("TTS_APP_ID not set")
    if not token:
        raise EnvironmentError("TTS_TOKEN or ARK_API_KEY not set")

    return app_id, token


def _get_headers(app_id: str, token: str) -> dict:
    """构建 V3 API 请求头。"""
    return {
        "Content-Type": "application/json",
        "X-Api-App-Id": app_id,
        "X-Api-Access-Key": token,
        "X-Api-Resource-Id": TTS_RESOURCE_ID,
        "X-Api-Request-Id": str(uuid.uuid4()),
    }


def _load_storyboard(storyboard_path: str) -> list[dict]:
    """加载分镜脚本 YAML，返回场景列表。"""
    with open(storyboard_path, encoding="utf-8") as f:
        data = yaml.safe_load(f)

    if isinstance(data, list):
        return data
    if isinstance(data, dict):
        for key in ("scenes", "分镜", "分镜列表", "storyboard"):
            if key in data and isinstance(data[key], list):
                return data[key]
    raise ValueError(f"Cannot parse storyboard: {storyboard_path}")


def _extract_text(scene: dict) -> str:
    """从场景 dict 中提取台词或旁白文本。"""
    for key in ("台词", "旁白", "dialogue", "narration", "text", "voiceover"):
        value = scene.get(key)
        if value and isinstance(value, str) and value.strip():
            return value.strip()
    return ""


def submit_tts_task(
    text: str,
    app_id: str,
    token: str,
    speaker: str = "zh_male_ruyayichen_uranus_bigtts",
) -> str:
    """
    提交 V3 异步 TTS 任务，返回 task_id。

    使用豆包语音合成 2.0 大模型（seed-tts-2.0），启用 enable_timestamp 获取字幕时间戳。
    """
    payload = {
        "user": {"uid": "video-pipeline"},
        "unique_id": str(uuid.uuid4()),
        "req_params": {
            "text": text,
            "speaker": speaker,
            "audio_params": {
                "format": "mp3",
                "sample_rate": 24000,
                "enable_timestamp": True,
            },
        },
    }

    resp = requests.post(
        TTS_SUBMIT_URL,
        json=payload,
        headers=_get_headers(app_id, token),
        timeout=30,
    )
    resp.raise_for_status()
    body = resp.json()

    code = body.get("code", 0)
    if code != 20000000:
        raise RuntimeError(f"TTS submit error {code}: {body.get('message', '')}")

    task_id = body.get("data", {}).get("task_id", "")
    if not task_id:
        raise RuntimeError(f"No task_id in TTS submit response: {body}")

    return task_id


def poll_tts_result(
    task_id: str,
    app_id: str,
    token: str,
) -> dict:
    """
    轮询 V3 TTS 任务直到完成，返回完整结果。

    task_status: 1=Running, 2=Success, 3=Failure
    """
    deadline = time.time() + POLL_TIMEOUT

    while time.time() < deadline:
        resp = requests.post(
            TTS_QUERY_URL,
            json={"task_id": task_id},
            headers=_get_headers(app_id, token),
            timeout=30,
        )
        resp.raise_for_status()
        body = resp.json()

        data = body.get("data", {})
        status = data.get("task_status")
        if status == 2:  # Success
            return data
        if status == 3:  # Failure
            raise RuntimeError(f"TTS task failed: {body}")

        time.sleep(POLL_INTERVAL)

    raise TimeoutError(f"TTS task {task_id} timed out after {POLL_TIMEOUT}s")


def download_audio(url: str, dest_path: str) -> None:
    """下载音频文件。"""
    os.makedirs(os.path.dirname(dest_path), exist_ok=True)
    resp = requests.get(url, stream=True, timeout=60)
    resp.raise_for_status()
    with open(dest_path, "wb") as f:
        for chunk in resp.iter_content(chunk_size=8192):
            f.write(chunk)


def _get_audio_duration(audio_path: str) -> float:
    """用 ffprobe 提取音频时长（秒）。"""
    try:
        result = subprocess.run(
            ["ffprobe", "-v", "quiet", "-print_format", "json",
             "-show_format", audio_path],
            capture_output=True, text=True, check=True, timeout=10,
        )
        data = json.loads(result.stdout)
        return float(data.get("format", {}).get("duration", 0.0))
    except Exception:
        return 0.0


def sentences_to_srt(sentences: list[dict], srt_path: str) -> None:
    """
    将 V3 API 返回的 sentences 时间戳转为 SRT 字幕文件。

    V3 格式: [{"text": "...", "startTime": 0.315, "endTime": 2.545}, ...]
    时间单位: 秒（float64）
    """
    os.makedirs(os.path.dirname(srt_path), exist_ok=True)

    lines = []
    for i, s in enumerate(sentences, start=1):
        start = s.get("startTime", 0.0)
        end = s.get("endTime", 0.0)
        text = s.get("text", "").strip()
        if not text:
            continue

        lines.append(str(i))
        lines.append(f"{_sec_to_srt_time(start)} --> {_sec_to_srt_time(end)}")
        lines.append(text)
        lines.append("")

    with open(srt_path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))


def _sec_to_srt_time(sec: float) -> str:
    """秒 → SRT 时间格式 HH:MM:SS,mmm"""
    h = int(sec // 3600)
    m = int((sec % 3600) // 60)
    s = sec % 60
    ms = int((s - int(s)) * 1000)
    return f"{h:02d}:{m:02d}:{int(s):02d},{ms:03d}"


def embed_audio_and_subtitle(
    video_path: str,
    audio_path: str,
    srt_path: str,
    output_path: str,
) -> None:
    """
    用 FFmpeg 将 TTS 音频和 SRT 字幕混合嵌入到视频片段中。

    音频处理：amix 混合视频原音（Seedance 环境音效，volume=0.3）和 TTS 旁白（volume=1.0），
    duration=longest 确保音频轨与视频等长（如 12 秒），TTS 结束后只剩环境音。
    不使用 -shortest，保持视频原始时长，不裁剪。
    字幕使用 mov_text 软字幕，不需要 libass。
    """
    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    cmd = [
        "ffmpeg", "-y",
        "-i", video_path,
        "-i", audio_path,
        "-i", srt_path,
        "-filter_complex",
        "[0:a]volume=0.3[env];[1:a]volume=1.0[tts];[env][tts]amix=inputs=2:duration=longest[aout]",
        "-map", "0:v", "-map", "[aout]", "-map", "2:s",
        "-c:v", "copy",
        "-c:a", "aac", "-b:a", "128k",
        "-c:s", "mov_text",
        "-movflags", "+faststart",
        output_path,
    ]

    result = subprocess.run(
        cmd, capture_output=True, text=True, timeout=120,
    )
    if result.returncode != 0:
        raise RuntimeError(f"FFmpeg embed failed: {result.stderr[-500:]}")


def _write_empty_mp3(output_path: str) -> float:
    """dry-run 模式：写入最小有效 MP3 文件（静音帧）。"""
    silent_mp3 = bytes(
        [0xFF, 0xFB, 0x90, 0x00, *([0x00] * 413)]
    )
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, "wb") as f:
        f.write(silent_mp3)
    return 0.0


def run_stage5(
    project_dir: str,
    storyboard_path: str,
    speaker: str = "zh_male_ruyayichen_uranus_bigtts",
    dry_run: bool = False,
    scene_filter: int | None = None,
) -> list[dict]:
    """
    执行 Stage 5: TTS 合成 + 字幕生成 + 嵌入视频。

    使用豆包语音合成 2.0 大模型（seed-tts-2.0）。

    输出:
        audio/tts-{01..N}.mp3        — 语音文件
        subtitles/scene-{01..N}.srt  — 字幕文件
        clips/scene-{01..N}-tts-sub.mp4 — 带旁白+字幕的视频片段
        audio/tts-manifest.json      — 时长清单
    """
    audio_dir = os.path.join(project_dir, "audio")
    subtitles_dir = os.path.join(project_dir, "subtitles")
    clips_dir = os.path.join(project_dir, "clips")
    os.makedirs(audio_dir, exist_ok=True)
    os.makedirs(subtitles_dir, exist_ok=True)

    scenes = _load_storyboard(storyboard_path)
    print(f"Stage 5: {len(scenes)} scenes loaded from {storyboard_path}")
    print(f"  Model: seed-tts-2.0 (大模型语音合成)")
    print(f"  Speaker: {speaker}")

    if not dry_run:
        app_id, token = _get_tts_credentials()
    else:
        app_id, token = ("", "")
        print("  [dry-run] Skipping API calls")

    results = []
    for i, scene in enumerate(scenes, start=1):
        if scene_filter is not None and i != scene_filter:
            continue
        scene_num = str(i).zfill(2)
        audio_path = os.path.join(audio_dir, f"tts-{scene_num}.mp3")
        srt_path = os.path.join(subtitles_dir, f"scene-{scene_num}.srt")
        final_path = ""

        text = _extract_text(scene)
        if not text:
            print(f"  Scene {scene_num}: no 台词/旁白 found, skipping")
            continue

        print(f"  Scene {scene_num}: synthesizing ({len(text)} chars)")

        if dry_run:
            duration = _write_empty_mp3(audio_path)
            print(f"  Scene {scene_num}: [dry-run] placeholder written")
        else:
            # 1. 提交异步任务
            task_id = submit_tts_task(text, app_id, token, speaker)
            print(f"  Scene {scene_num}: task_id={task_id}, polling...")

            # 2. 轮询等待完成
            result = poll_tts_result(task_id, app_id, token)

            # 3. 下载音频
            audio_url = result.get("audio_url", "")
            if not audio_url:
                raise RuntimeError(f"No audio_url for scene {scene_num}: {result}")
            download_audio(audio_url, audio_path)
            duration = _get_audio_duration(audio_path)
            print(f"  Scene {scene_num}: audio saved ({duration:.1f}s) → {audio_path}")

            # 4. 生成 SRT 字幕
            sentences = result.get("sentences", [])
            if sentences:
                sentences_to_srt(sentences, srt_path)
                print(f"  Scene {scene_num}: subtitle saved ({len(sentences)} entries) → {srt_path}")
            else:
                print(f"  Scene {scene_num}: no subtitle data returned")

            # 5. FFmpeg 嵌入音频+字幕到视频片段
            video_path = os.path.join(clips_dir, f"scene-{scene_num}.mp4")
            final_path = os.path.join(clips_dir, f"scene-{scene_num}-tts-sub.mp4")
            if os.path.exists(video_path) and os.path.exists(srt_path):
                print(f"  Scene {scene_num}: embedding audio+subtitle into video...")
                embed_audio_and_subtitle(video_path, audio_path, srt_path, final_path)
                print(f"  Scene {scene_num}: final video → {final_path}")
            elif os.path.exists(video_path):
                print(f"  Scene {scene_num}: no SRT, skipping embed")
                final_path = ""
            else:
                print(f"  Scene {scene_num}: video clip not found at {video_path}, skipping embed")
                final_path = ""

        results.append({
            "scene_num": scene_num,
            "audio_path": audio_path,
            "srt_path": srt_path,
            "final_video_path": final_path if not dry_run else "",
            "duration_s": duration,
            "text": text,
        })

    # 写入时长清单
    manifest_path = os.path.join(audio_dir, "tts-manifest.json")
    with open(manifest_path, "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=2)

    print(f"Stage 5 complete: {len(results)} audio + subtitle files")
    print(f"  Manifest: {manifest_path}")
    return results


def main():
    parser = argparse.ArgumentParser(
        description="Stage 5: TTS Voice Synthesis + Subtitle (豆包语音合成 2.0)"
    )
    parser.add_argument("--project-id", required=True)
    parser.add_argument("--output-dir", default="Video-Producer-output")
    parser.add_argument(
        "--scene", default="all",
        help="Scene number (1-based) or 'all' (default: all)",
    )
    parser.add_argument("--storyboard", required=True)
    parser.add_argument(
        "--speaker", default="zh_male_ruyayichen_uranus_bigtts",
        help="豆包 TTS 2.0 音色 ID (default: zh_male_ruyayichen_uranus_bigtts)",
    )
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    project_dir = os.path.join(args.output_dir, args.project_id)
    scene_filter = None if args.scene == "all" else int(args.scene)
    run_stage5(project_dir, args.storyboard, args.speaker, args.dry_run, scene_filter=scene_filter)


if __name__ == "__main__":
    main()
