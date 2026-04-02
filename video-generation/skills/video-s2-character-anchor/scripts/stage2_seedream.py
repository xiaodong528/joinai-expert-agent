"""
Stage 2: 角色锚定 — Seedream 4.0 图像生成

使用 Seedream 4.0 生成角色参考图，支持 txt2img 和 img2img（image_urls 锚定）。

用法:
    python scripts/stage2_seedream.py --project-id test-001 --prompt "角色描述..." --name hero
    python scripts/stage2_seedream.py --project-id test-001 --prompt "..." --name hero \\
        --image-urls https://example.com/ref.png --scale 0.7
    python scripts/stage2_seedream.py --project-id test-001 --prompt "..." --name hero --n 3
"""

import argparse
import os

import yaml

from api_client import APIClient

MODEL_ID = "doubao-seedream-4-0-250828"
API_PATH = "/images/generations"


def generate_images(
    client: APIClient,
    prompt: str,
    size: str = "1920x1080",
    negative_prompt: str = "",
    image_urls: list[str] | None = None,
    scale: float = 0.7,
    n: int = 1,
) -> list[str]:
    """
    调用 Seedream API 生成图像，返回图像 URL 列表。

    Args:
        client: ARK APIClient 实例
        prompt: 生成提示词（需含完整角色外观描述）
        size: 图像尺寸，格式 WxH
        negative_prompt: 负面提示词
        image_urls: 参考图 URL 列表（img2img 锚定用）
        scale: img2img 强度（0.0-1.0），仅在 image_urls 非空时生效
        n: 生成数量

    Returns:
        生成图像的 URL 列表
    """
    width, height = size.split("x")
    payload: dict = {
        "model": MODEL_ID,
        "prompt": prompt,
        "size": f"{width}x{height}",
        "n": n,
    }

    if negative_prompt:
        payload["negative_prompt"] = negative_prompt

    if image_urls:
        payload["image_urls"] = image_urls
        payload["scale"] = scale

    resp = client.post(API_PATH, json=payload)
    data = resp.json()

    urls = [item["url"] for item in data.get("data", [])]
    if not urls:
        raise RuntimeError(f"No image URLs in response: {data}")
    return urls


def run_stage2(
    project_dir: str,
    prompt: str,
    character_name: str = "character",
    size: str = "1920x1080",
    negative_prompt: str = "",
    image_urls: list[str] | None = None,
    scale: float = 0.7,
    n: int = 1,
) -> list[str]:
    """
    执行 Stage 2 完整角色锚定流程。

    Args:
        project_dir: 项目输出目录路径（如 output/test-001）
        prompt: 角色生成提示词
        character_name: 角色名称，用于文件命名
        size: 图像尺寸
        negative_prompt: 负面提示词
        image_urls: 参考图 URL（img2img 锚定）
        scale: img2img 强度
        n: 生成数量

    Returns:
        保存的本地文件路径列表
    """
    characters_dir = os.path.join(project_dir, "characters")
    os.makedirs(characters_dir, exist_ok=True)

    client = APIClient("ark")

    mode = "img2img" if image_urls else "txt2img"
    print(f"Stage 2: Generating {n} image(s) for '{character_name}' [{mode}]")

    urls = generate_images(client, prompt, size, negative_prompt, image_urls, scale, n)

    saved_paths = []
    for idx, url in enumerate(urls):
        if n == 1:
            filename = f"{character_name}-ref.png"
        else:
            filename = f"{character_name}-ref-{idx + 1:02d}.png"
        dest = os.path.join(characters_dir, filename)
        print(f"  Downloading image {idx + 1}/{len(urls)} → {dest}")
        client.download(url, dest)
        saved_paths.append(dest)

    print(f"Stage 2 complete: {len(saved_paths)} image(s) saved to {characters_dir}")
    return saved_paths


def build_character_prompt(character: dict, style_prefix: str) -> str:
    """从角色 DNA 卡片构建生成提示词。"""
    appearance = character.get("外貌描述", {})
    parts = []

    gender = character.get("性别", "")
    age = character.get("年龄段", "")
    if gender and age:
        parts.append(f"{age}{gender}")

    for field in ["面部特征", "发型发色", "肤色质感", "体型"]:
        val = appearance.get(field, "")
        if val:
            parts.append(val)

    costume = character.get("服装", {}).get("默认服装", "")
    if costume:
        parts.append(costume)

    accessory = character.get("标志配饰", "")
    if accessory:
        parts.append(accessory)

    dna = "，".join(parts)
    return f"{style_prefix}, {dna}"


def run_stage2_from_story(
    project_dir: str,
    story_path: str,
    size: str = "",
) -> list[str]:
    """从 story.yaml 批量生成所有角色的参考图。"""
    with open(story_path, encoding="utf-8") as f:
        story = yaml.safe_load(f)

    characters = story.get("角色", [])
    if not characters:
        print("No characters found in story.yaml, skipping Stage 2")
        return []

    style_lock = story.get("风格锁定", {})
    style_prefix = style_lock.get("统一风格前缀", "")
    negative_prompt = style_lock.get("负面提示词", "")

    if not size:
        resolution = str(style_lock.get("分辨率", "1920x1080"))
        size = resolution if "x" in resolution else "1920x1080"

    print(f"Stage 2: Found {len(characters)} character(s) in {story_path}")

    all_paths: list[str] = []
    for character in characters:
        name = character.get("姓名", "character")
        prompt = build_character_prompt(character, style_prefix)
        paths = run_stage2(
            project_dir,
            prompt=prompt,
            character_name=name,
            size=size,
            negative_prompt=negative_prompt,
        )
        all_paths.extend(paths)

    return all_paths


def main():
    parser = argparse.ArgumentParser(description="Stage 2: Character Anchoring via Seedream 4.0")
    parser.add_argument("--project-id", required=True, help="Project ID (e.g., test-001)")
    parser.add_argument("--output-dir", default="Video-Producer-output", help="Base output directory")
    parser.add_argument("--story", default=None, help="Path to story.yaml (batch mode: generates for all characters)")
    parser.add_argument("--prompt", default=None, help="Character generation prompt (single mode)")
    parser.add_argument("--name", default="character", help="Character name for file naming (single mode)")
    parser.add_argument("--size", default="", help="Image size WxH (auto-detect from story.yaml if empty)")
    parser.add_argument(
        "--image-urls",
        nargs="+",
        default=None,
        help="Reference image URLs for img2img anchoring",
    )
    parser.add_argument(
        "--scale",
        type=float,
        default=0.7,
        help="img2img strength (0.0-1.0), used when --image-urls provided",
    )
    parser.add_argument("--n", type=int, default=1, help="Number of images to generate")
    parser.add_argument("--negative-prompt", default="", help="Negative prompt for generation")
    args = parser.parse_args()

    project_dir = os.path.join(args.output_dir, args.project_id)

    if args.story:
        run_stage2_from_story(project_dir, args.story, size=args.size)
    elif args.prompt:
        size = args.size or "1920x1080"
        run_stage2(
            project_dir,
            prompt=args.prompt,
            character_name=args.name,
            size=size,
            negative_prompt=args.negative_prompt,
            image_urls=args.image_urls,
            scale=args.scale,
            n=args.n,
        )
    else:
        parser.error("Either --story or --prompt is required")


if __name__ == "__main__":
    main()
