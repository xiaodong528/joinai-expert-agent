"""
Stage 3: 关键帧生成 — 首尾帧锚定链 (Seedream 4.0)

实现首尾帧锚定链：
  Scene 1 首帧 (txt2img) → Scene 1 尾帧 (img2img) →
  Scene 2 首帧 (img2img, 锚定自 Scene 1 尾帧) → Scene 2 尾帧 → ...

每场景生成:
  - scene-{N}-first.png (首帧，必有)
  - scene-{N}-last.png  (尾帧，仅当 storyboard 含 末帧图提示词 时生成)

用法:
    python stage3_keyframe_chain.py --project-id test-001 --storyboard output/test-001/scripts/storyboard.yaml
    python stage3_keyframe_chain.py --project-id test-001 --storyboard ... --start-scene 1 --end-scene 3
    python stage3_keyframe_chain.py --project-id test-001 --storyboard ... --start-scene 4
"""

import argparse
import os

import yaml

from api_client import APIClient

MODEL_ID = "doubao-seedream-4-0-250828"
API_PATH = "/images/generations"

# 锚定链 img2img 强度范围（首帧锚定链设计值）
ANCHOR_SCALE_DEFAULT = 0.4


def generate_keyframe(
    client: APIClient,
    prompt: str,
    size: str = "1920x1080",
    negative_prompt: str = "",
    anchor_url: str | None = None,
    scale: float = ANCHOR_SCALE_DEFAULT,
) -> str:
    """
    生成单帧关键图，返回图像 URL。

    Args:
        client: ARK APIClient 实例
        prompt: 分镜提示词（含完整角色 DNA + 风格前缀）
        size: 图像尺寸
        negative_prompt: 负面提示词
        anchor_url: 前一场景首帧 URL（img2img 锚定），None 则使用 txt2img
        scale: img2img 强度（0.3-0.5 锚定链设计范围）

    Returns:
        生成图像的 URL
    """
    width, height = size.split("x")
    payload: dict = {
        "model": MODEL_ID,
        "prompt": prompt,
        "size": f"{width}x{height}",
        "n": 1,
    }

    if negative_prompt:
        payload["negative_prompt"] = negative_prompt

    if anchor_url:
        payload["image_urls"] = [anchor_url]
        payload["scale"] = scale

    resp = client.post(API_PATH, json=payload)
    data = resp.json()

    items = data.get("data", [])
    if not items:
        raise RuntimeError(f"No image data in response: {data}")
    return items[0]["url"]


def upload_local_image(local_path: str) -> str:
    """
    将本地图像文件转换为 data URI 供 image_urls 使用。

    Args:
        local_path: 本地图像路径

    Returns:
        base64 data URI 字符串
    """
    import base64

    with open(local_path, "rb") as f:
        data = f.read()
    b64 = base64.b64encode(data).decode()
    return f"data:image/png;base64,{b64}"


def run_stage3(
    project_dir: str,
    storyboard_path: str,
    start_scene: int = 1,
    end_scene: int | None = None,
    size: str = "1920x1080",
    negative_prompt: str = "",
    anchor_scale: float = ANCHOR_SCALE_DEFAULT,
) -> list[str]:
    """
    执行 Stage 3 首尾帧锚定链完整流程。

    每个场景生成:
    - scene-{N}-first.png (首帧，必有)
    - scene-{N}-last.png  (尾帧，仅当 末帧图提示词 存在时生成)

    锚定链: Scene N 的首帧锚定自 Scene N-1 的尾帧（优先）或首帧（回退）。

    Args:
        project_dir: 项目输出目录路径
        storyboard_path: storyboard.yaml 文件路径
        start_scene: 起始场景编号（支持断点续生）
        end_scene: 结束场景编号（含）；None 表示处理到最后一个场景。
                   与 start_scene 配合实现分批并行（批内串行、批间并行）
        size: 图像尺寸
        negative_prompt: 负面提示词（为空时自动从 storyboard 风格锁定读取）
        anchor_scale: img2img 锚定强度（0.3-0.5）

    Returns:
        保存的关键帧本地路径列表
    """
    frames_dir = os.path.join(project_dir, "frames")
    os.makedirs(frames_dir, exist_ok=True)

    with open(storyboard_path, encoding="utf-8") as f:
        storyboard = yaml.safe_load(f)

    # 支持中文和英文 key（中文优先）
    scenes = storyboard.get("分镜列表", storyboard.get("scenes", []))
    if not scenes:
        raise ValueError(f"No scenes found in {storyboard_path}")

    # 自动从 storyboard 风格锁定读取 negative_prompt
    if not negative_prompt:
        style_lock = storyboard.get("风格锁定", {})
        negative_prompt = style_lock.get("负面提示词", "")

    # 按编号排序
    scenes_sorted = sorted(scenes, key=lambda s: s.get("编号", s.get("scene_number", 0)))

    client = APIClient("ark")
    saved_paths: list[str] = []
    anchor_url: str | None = None

    range_desc = f"{start_scene}-{end_scene}" if end_scene is not None else f"{start_scene}-end"
    print(f"Stage 3: Processing scenes {range_desc} from storyboard ({len(scenes_sorted)} total)")

    for scene in scenes_sorted:
        scene_num = scene.get("编号", scene.get("scene_number", 0))

        if end_scene is not None and scene_num > end_scene:
            break

        first_prompt = scene.get("文生图提示词", scene.get("prompt", ""))
        last_prompt = scene.get("末帧图提示词", "")
        if not first_prompt:
            raise ValueError(f"Scene {scene_num} has no prompt in storyboard")

        first_path = os.path.join(frames_dir, f"scene-{scene_num:02d}-first.png")
        last_path = os.path.join(frames_dir, f"scene-{scene_num:02d}-last.png")

        if scene_num < start_scene:
            # 跳过生成，但读取已有帧作为下一场景锚点（优先尾帧）
            if os.path.exists(last_path):
                anchor_url = upload_local_image(last_path)
                print(f"  Scene {scene_num:02d}: skipped, using last frame as anchor")
            elif os.path.exists(first_path):
                anchor_url = upload_local_image(first_path)
                print(f"  Scene {scene_num:02d}: skipped, using first frame as anchor")
            else:
                anchor_url = None
                print(f"  Scene {scene_num:02d}: skipped, no existing frame for anchor")
            continue

        # 1. 生成首帧（锚定自上一场景的尾帧/首帧）
        mode = "img2img" if anchor_url else "txt2img"
        print(f"  Scene {scene_num:02d} first: [{mode}] → {first_path}")

        first_url = generate_keyframe(client, first_prompt, size, negative_prompt, anchor_url, anchor_scale)
        client.download(first_url, first_path)
        saved_paths.append(first_path)

        # 2. 生成尾帧（锚定自本场景首帧，仅当 末帧图提示词 存在时）
        if last_prompt:
            first_data_uri = upload_local_image(first_path)
            print(f"  Scene {scene_num:02d} last:  [img2img] → {last_path}")

            last_url = generate_keyframe(client, last_prompt, size, negative_prompt, first_data_uri, anchor_scale)
            client.download(last_url, last_path)
            saved_paths.append(last_path)

            # 下一场景锚定自尾帧
            anchor_url = upload_local_image(last_path)
        else:
            # 无尾帧 → 下一场景锚定自首帧（向后兼容）
            anchor_url = upload_local_image(first_path)

    print(f"Stage 3 complete: {len(saved_paths)} keyframe(s) saved to {frames_dir}")
    return saved_paths


def main():
    parser = argparse.ArgumentParser(description="Stage 3: Keyframe Chain Generation via Seedream 4.0")
    parser.add_argument("--project-id", required=True, help="Project ID (e.g., test-001)")
    parser.add_argument("--output-dir", default="Video-Producer-output", help="Base output directory")
    parser.add_argument("--storyboard", required=True, help="Path to storyboard.yaml")
    parser.add_argument("--start-scene", type=int, default=1, help="Start from this scene number")
    parser.add_argument("--end-scene", type=int, default=None, help="End at this scene number (inclusive); omit to process all remaining")
    parser.add_argument("--size", default="1920x1080", help="Image size WxH")
    parser.add_argument(
        "--anchor-scale",
        type=float,
        default=ANCHOR_SCALE_DEFAULT,
        help=f"img2img anchor strength (0.3-0.5, default: {ANCHOR_SCALE_DEFAULT})",
    )
    parser.add_argument("--negative-prompt", default="", help="Negative prompt (auto-read from storyboard if empty)")
    args = parser.parse_args()

    project_dir = os.path.join(args.output_dir, args.project_id)
    run_stage3(
        project_dir,
        storyboard_path=args.storyboard,
        start_scene=args.start_scene,
        end_scene=args.end_scene,
        size=args.size,
        negative_prompt=args.negative_prompt,
        anchor_scale=args.anchor_scale,
    )


if __name__ == "__main__":
    main()
