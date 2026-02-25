#!/usr/bin/env python3
"""
获取 Simple Icons 的 SVG 图标数据
Simple Icons: https://simpleicons.org/
GitHub: https://github.com/simple-icons/simple-icons
"""

import requests
import json
import os
from pathlib import Path
from typing import List, Dict
from tqdm import tqdm
import time


def fetch_simple_icons_metadata() -> List[Dict]:
    """
    获取 Simple Icons 的元数据

    Returns:
        图标列表，每个包含 title, slug, hex 颜色等
    """
    url = "https://raw.githubusercontent.com/simple-icons/simple-icons/develop/data/simple-icons.json"

    try:
        response = requests.get(url, timeout=30)
        response.raise_for_status()
        data = response.json()

        # data 是 list 不是 dict
        icons = []
        for item in data:
            title = item.get("title", "")
            slug = item.get("slug", "")
            # 如果没有 slug，使用 title 的小写替换空格为下划线
            if not slug:
                slug = title.lower().replace(" ", "").replace("-", "").replace(".", "")

            icons.append({
                "title": title,
                "slug": slug,
                "hex": item.get("hex", ""),
                "source": item.get("source", ""),
                "guidelines": item.get("guidelines", ""),
                "license": item.get("license", {}),
            })

        # 过滤掉 slug 为空的
        icons = [i for i in icons if i["slug"]]

        return icons

    except Exception as e:
        print(f"Error fetching metadata: {e}")
        return []


def download_svg(slug: str, output_dir: str) -> bool:
    """
    下载单个 SVG 图标

    Args:
        slug: 图标 slug（文件名）
        output_dir: 保存目录

    Returns:
        是否成功
    """
    url = f"https://raw.githubusercontent.com/simple-icons/simple-icons/develop/icons/{slug}.svg"

    try:
        response = requests.get(url, timeout=30)
        response.raise_for_status()

        output_path = os.path.join(output_dir, f"{slug}.svg")
        Path(output_dir).mkdir(parents=True, exist_ok=True)

        with open(output_path, "w", encoding="utf-8") as f:
            f.write(response.text)

        return True

    except Exception as e:
        print(f"Error downloading {slug}: {e}")
        return False


def download_all_svgs(
    icons: List[Dict],
    output_dir: str = "dataset/simple_icons",
    delay: float = 0.1
) -> List[Dict]:
    """
    批量下载所有 SVG 图标

    Args:
        icons: 图标元数据列表
        output_dir: 保存目录
        delay: 下载间隔

    Returns:
        成功下载的图标列表
    """
    results = []

    for icon in tqdm(icons, desc="Downloading SVGs"):
        slug = icon["slug"]

        # 检查是否已存在
        output_path = os.path.join(output_dir, f"{slug}.svg")
        if os.path.exists(output_path):
            icon["path"] = output_path
            results.append(icon)
            continue

        if download_svg(slug, output_dir):
            icon["path"] = output_path
            results.append(icon)

        time.sleep(delay)

    return results


def generate_annotations(icons: List[Dict], output_dir: str = "dataset/simple_icons"):
    """
    为每个图标生成标注文件（用于 LoRA 训练）

    标注格式：{filename}.txt
    内容：描述文本（prompt）
    """
    prompts = []

    for icon in icons:
        title = icon["title"]
        slug = icon["slug"]

        # 生成多种 prompt 变体
        prompt_variants = [
            f"minimalist tech logo of {title}, geometric shape, flat design, single color, vector style, clean lines, software project icon, white background",
            f"{title} icon, simple geometric logo, minimal design, monochrome, tech brand identity",
            f"flat vector logo for {title}, minimal style, single color icon, clean geometric shape",
        ]

        # 保存标注文件
        txt_path = os.path.join(output_dir, f"{slug}.txt")
        with open(txt_path, "w", encoding="utf-8") as f:
            f.write("\n".join(prompt_variants))

        prompts.append({
            "slug": slug,
            "title": title,
            "prompts": prompt_variants
        })

    # 保存所有 prompt 的汇总
    with open(os.path.join(output_dir, "annotations.json"), "w", encoding="utf-8") as f:
        json.dump(prompts, f, indent=2, ensure_ascii=False)

    print(f"Generated annotations for {len(prompts)} icons")


def main(limit: int = 500):
    """
    Args:
        limit: 最多下载多少个图标（用于测试）
    """
    print("Fetching Simple Icons metadata...")
    icons = fetch_simple_icons_metadata()
    print(f"Found {len(icons)} icons")

    # 限制数量
    if limit and len(icons) > limit:
        icons = icons[:limit]
        print(f"Limited to {limit} icons for testing")

    # 保存元数据
    Path("dataset").mkdir(exist_ok=True)
    with open("dataset/simple_icons_metadata.json", "w", encoding="utf-8") as f:
        json.dump(icons, f, indent=2, ensure_ascii=False)

    # 下载 SVG
    print("\nDownloading SVG files...")
    downloaded = download_all_svgs(icons, output_dir="dataset/simple_icons")
    print(f"Downloaded {len(downloaded)} / {len(icons)} icons")

    # 生成标注
    print("\nGenerating annotations...")
    generate_annotations(downloaded)

    print("\n" + "=" * 60)
    print("Simple Icons 数据集准备完成！")
    print("=" * 60)
    print(f"图标数量: {len(downloaded)}")
    print(f"保存位置: dataset/simple_icons/")
    print(f"元数据: dataset/simple_icons_metadata.json")


if __name__ == "__main__":
    import sys
    limit = int(sys.argv[1]) if len(sys.argv) > 1 else 500
    main(limit=limit)
