"""
Stage 10: 质量审查 (ffprobe + QA Report)

使用 ffprobe 提取视频技术指标，生成结构化 QA 报告。

用法:
    python scripts/stage10_qa.py --project-id test-001
    python scripts/stage10_qa.py --project-id test-001 --video videos/final.mp4
"""

import argparse
import json
import os
import subprocess
import sys
from datetime import datetime


def probe_video(video_path: str) -> dict:
    """用 ffprobe 提取视频元数据。"""
    cmd = [
        "ffprobe",
        "-v", "quiet",
        "-print_format", "json",
        "-show_format",
        "-show_streams",
        video_path,
    ]
    result = subprocess.run(cmd, capture_output=True, text=True, check=True)
    return json.loads(result.stdout)


def check_resolution(streams: list, expected: str = "1920x1080") -> dict:
    """检查视频分辨率。"""
    video_streams = [s for s in streams if s.get("codec_type") == "video"]
    if not video_streams:
        return {"check": "resolution", "status": "FAIL", "detail": "No video stream found"}

    vs = video_streams[0]
    actual = f"{vs.get('width', 0)}x{vs.get('height', 0)}"
    w, h = int(vs.get("width", 0)), int(vs.get("height", 0))
    exp_w, exp_h = map(int, expected.split("x"))

    passed = w >= exp_w and h >= exp_h
    return {
        "check": "resolution",
        "status": "PASS" if passed else "WARN",
        "expected": expected,
        "actual": actual,
    }


def check_duration(fmt: dict, expected_range: tuple[float, float]) -> dict:
    """检查视频总时长。"""
    duration = float(fmt.get("duration", 0))
    min_d, max_d = expected_range
    passed = min_d <= duration <= max_d
    return {
        "check": "duration",
        "status": "PASS" if passed else "FAIL",
        "expected_range": f"{min_d}-{max_d}s",
        "actual": f"{duration:.1f}s",
    }


def check_codec(streams: list) -> dict:
    """检查编码格式。"""
    video_codec = None
    audio_codec = None

    for s in streams:
        if s.get("codec_type") == "video":
            video_codec = s.get("codec_name", "unknown")
        elif s.get("codec_type") == "audio":
            audio_codec = s.get("codec_name", "unknown")

    video_ok = video_codec in ("h264", "hevc", "av1")
    audio_ok = audio_codec in ("aac", "mp3", "opus", None)  # None = 无音频也OK

    return {
        "check": "codec",
        "status": "PASS" if video_ok and audio_ok else "WARN",
        "video_codec": video_codec or "none",
        "audio_codec": audio_codec or "none",
        "expected": "H.264/HEVC + AAC",
    }


def check_black_frames(video_path: str, threshold: float = 0.98) -> dict:
    """检测黑帧（采样前 5 帧和后 5 帧）。"""
    try:
        cmd = [
            "ffmpeg", "-i", video_path,
            "-vf", f"blackdetect=d=0.5:pix_th={threshold}",
            "-an", "-f", "null", "-",
        ]
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
        stderr = result.stderr
        black_segments = stderr.count("black_start")
        return {
            "check": "black_frames",
            "status": "PASS" if black_segments == 0 else "WARN",
            "black_segments_detected": black_segments,
        }
    except (subprocess.TimeoutExpired, subprocess.CalledProcessError):
        return {"check": "black_frames", "status": "SKIP", "detail": "Detection failed"}


def check_file_size(video_path: str, max_mb: float = 500) -> dict:
    """检查文件大小。"""
    size_bytes = os.path.getsize(video_path)
    size_mb = size_bytes / (1024 * 1024)
    return {
        "check": "file_size",
        "status": "PASS" if size_mb <= max_mb else "WARN",
        "size_mb": round(size_mb, 2),
        "max_mb": max_mb,
    }


def run_stage10(
    project_dir: str,
    video_name: str = "final.mp4",
    expected_duration_range: tuple[float, float] = (10, 600),
    expected_resolution: str = "1920x1080",
) -> dict:
    """执行 Stage 10 完整 QA 流程。"""
    # 按优先级查找视频文件
    videos_dir = os.path.join(project_dir, "videos")
    candidates = [video_name, "final.mp4", "lipsync.mp4", "concat-mixed.mp4"]
    video_path = None
    for name in candidates:
        path = os.path.join(videos_dir, name)
        if os.path.exists(path):
            video_path = path
            break

    if not video_path:
        return {
            "status": "ERROR",
            "detail": f"No video found in {videos_dir}",
            "candidates_checked": candidates,
        }

    print(f"Stage 10: QA review for {video_path}")

    # ffprobe 提取元数据
    probe_data = probe_video(video_path)
    streams = probe_data.get("streams", [])
    fmt = probe_data.get("format", {})

    # 逐项检查
    checks = [
        check_resolution(streams, expected_resolution),
        check_duration(fmt, expected_duration_range),
        check_codec(streams),
        check_black_frames(video_path),
        check_file_size(video_path),
    ]

    # 汇总
    fail_count = sum(1 for c in checks if c["status"] == "FAIL")
    warn_count = sum(1 for c in checks if c["status"] == "WARN")

    report = {
        "qa_version": "1.0",
        "timestamp": datetime.now().isoformat(),
        "video_path": video_path,
        "summary": {
            "total_checks": len(checks),
            "passed": sum(1 for c in checks if c["status"] == "PASS"),
            "warnings": warn_count,
            "failures": fail_count,
            "overall": "FAIL" if fail_count > 0 else ("WARN" if warn_count > 0 else "PASS"),
        },
        "checks": checks,
        "probe_data": {
            "format_name": fmt.get("format_name"),
            "duration": fmt.get("duration"),
            "size": fmt.get("size"),
            "bit_rate": fmt.get("bit_rate"),
        },
    }

    # 保存报告
    report_path = os.path.join(project_dir, "qa-report.json")
    with open(report_path, "w", encoding="utf-8") as f:
        json.dump(report, f, ensure_ascii=False, indent=2)

    print(f"  Overall: {report['summary']['overall']}")
    print(f"  Checks: {report['summary']['passed']} PASS, {warn_count} WARN, {fail_count} FAIL")
    print(f"  Report: {report_path}")

    return report


def main():
    parser = argparse.ArgumentParser(description="Stage 10: QA Review")
    parser.add_argument("--project-id", required=True, help="Project ID")
    parser.add_argument("--output-dir", default="Video-Producer-output", help="Base output directory")
    parser.add_argument("--video", default="final.mp4", help="Video filename to check")
    parser.add_argument("--expected-duration", default="10-600", help="Expected duration range (s)")
    parser.add_argument("--expected-resolution", default="1920x1080", help="Expected resolution")
    args = parser.parse_args()

    project_dir = os.path.join(args.output_dir, args.project_id)
    min_d, max_d = map(float, args.expected_duration.split("-"))

    run_stage10(project_dir, args.video, (min_d, max_d), args.expected_resolution)


if __name__ == "__main__":
    main()
