"""
Stage 6: BGM 音乐生成 (MiniMax Music 2.5+, 同步 output_format=url)

使用 MiniMax Music 2.5+ API 生成纯器乐背景音乐。
API 使用 output_format="url" 模式，直接在响应中返回音频下载 URL。

用法:
    python stage6_bgm.py --project-id test-001 --prompt "Suspenseful cinematic BGM, orchestral"
    python stage6_bgm.py --project-id test-001 --prompt "..." --duration-hint 90
    python stage6_bgm.py --project-id test-001 --prompt "..." --dry-run
"""

import argparse
import os

from api_client import APIClient

_MUSIC_GENERATE_PATH = "/music_generation"

# BGM 生成超时（秒）— MiniMax 生成耗时较长，需 ≥ 300s
_BGM_TIMEOUT = 600


def run_stage6(
    project_dir: str,
    prompt: str,
    duration_hint: int = 60,
    dry_run: bool = False,
) -> str:
    """
    执行 Stage 6: BGM 生成（同步模式，output_format=url）。

    Args:
        project_dir: 项目输出目录（如 output/test-001）
        prompt: BGM 风格描述（英文效果最佳）
        duration_hint: 目标时长提示（秒）
        dry_run: 仅打印参数，不调用 API

    Returns:
        本地 bgm.mp3 的路径
    """
    audio_dir = os.path.join(project_dir, "audio")
    os.makedirs(audio_dir, exist_ok=True)
    output_path = os.path.join(audio_dir, "bgm.mp3")

    payload = {
        "model": "music-2.5+",
        "prompt": prompt,
        "is_instrumental": True,
        "lyrics_optimizer": True,
        "audio_setting": {
            "sample_rate": 44100,
            "bitrate": 256000,
            "format": "mp3",
        },
        "output_format": "url",
    }

    if duration_hint > 0:
        payload["refer_duration"] = duration_hint

    print(f"Stage 6: BGM Generation (MiniMax Music 2.5+)")
    print(f"  Prompt: {prompt}")
    print(f"  Duration hint: {duration_hint}s")
    print(f"  Output format: url (synchronous)")
    print(f"  Timeout: {_BGM_TIMEOUT}s")

    if dry_run:
        print(f"  [dry-run] Payload: {payload}")
        print(f"  [dry-run] Skipping API call")
        return output_path

    client = APIClient("minimax", timeout=_BGM_TIMEOUT)

    print(f"  Submitting BGM generation request...")
    try:
        resp = client.post(_MUSIC_GENERATE_PATH, json=payload, timeout=_BGM_TIMEOUT)
        body = resp.json()
    except Exception as e:
        raise RuntimeError(f"MiniMax music generation failed: {e}") from e

    data = body.get("data", {})

    # 检查 API 错误
    base_resp = body.get("base_resp", {})
    status_code = base_resp.get("status_code", 0)
    if status_code != 0:
        raise RuntimeError(
            f"MiniMax API error {status_code}: {base_resp.get('status_msg', 'unknown')}"
        )

    # 提取音频（data.audio 可能是 URL 或 hex 编码）
    audio_value = (
        data.get("audio")
        or data.get("audio_file")
        or data.get("audio_url")
        or body.get("audio_file")
        or body.get("audio_url")
    )

    if not audio_value:
        raise RuntimeError(f"No audio data in MiniMax response: {body}")

    # 判断是 URL 还是 hex 编码数据
    if audio_value.startswith("http"):
        audio_url = audio_value
    else:
        # hex 编码音频回退
        print(f"  Decoding hex audio data ({len(audio_value)} chars)")
        audio_bytes = bytes.fromhex(audio_value)
        with open(output_path, "wb") as f:
            f.write(audio_bytes)
        size_kb = len(audio_bytes) / 1024
        print(f"Stage 6 complete: {output_path} ({size_kb:.0f} KB)")
        return output_path

    # 下载音频文件
    print(f"  Downloading: {audio_url[:80]}...")
    client.download(audio_url, output_path)

    file_size = os.path.getsize(output_path)
    print(f"Stage 6 complete: {output_path} ({file_size / 1024:.0f} KB)")
    return output_path


def main():
    parser = argparse.ArgumentParser(
        description="Stage 6: BGM Music Generation (MiniMax Music 2.5+)"
    )
    parser.add_argument("--project-id", required=True, help="Project ID")
    parser.add_argument("--output-dir", default="Video-Producer-output", help="Base output directory")
    parser.add_argument(
        "--prompt",
        required=True,
        help="BGM style description in English",
    )
    parser.add_argument(
        "--duration-hint",
        type=int,
        default=60,
        help="Target BGM duration in seconds (default: 60)",
    )
    parser.add_argument("--dry-run", action="store_true", help="Print params without calling API")
    args = parser.parse_args()

    project_dir = os.path.join(args.output_dir, args.project_id)
    run_stage6(project_dir, args.prompt, args.duration_hint, args.dry_run)


if __name__ == "__main__":
    main()
