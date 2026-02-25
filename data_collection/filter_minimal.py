"""
筛选极简风格的 Logo 图片
基于颜色数量和简单几何特征进行筛选
"""

import json
import os
from pathlib import Path
from typing import List, Dict, Tuple
from PIL import Image
from tqdm import tqdm
import colorsys


def count_colors(image_path: str, max_colors: int = 256) -> int:
    """
    计算图片中不同颜色的数量

    Args:
        image_path: 图片路径
        max_colors: 最大分析颜色数

    Returns:
        不同颜色的数量，-1 表示无法分析
    """
    # 跳过 SVG 文件（无法直接用 Pillow 分析）
    if image_path.lower().endswith('.svg'):
        return -2  # 特殊标记表示 SVG

    try:
        with Image.open(image_path) as img:
            # 转换为 RGB
            if img.mode != "RGB":
                img = img.convert("RGB")

            # 缩小图片以加速分析
            img.thumbnail((100, 100))

            # 获取颜色直方图
            colors = img.getcolors(maxcolors=max_colors)

            if colors is None:
                # 颜色太多，可能不是极简风格
                return max_colors + 1

            return len(colors)

    except Exception as e:
        print(f"Error analyzing {image_path}: {e}")
        return -1


def analyze_dominant_colors(image_path: str, n_colors: int = 5) -> List[Tuple]:
    """
    分析图片的主要颜色

    Returns:
        主要颜色的列表 (count, (r, g, b))
    """
    try:
        with Image.open(image_path) as img:
            if img.mode != "RGB":
                img = img.convert("RGB")

            # 缩小图片
            img.thumbnail((150, 150))

            # 量化颜色
            quantized = img.quantize(colors=n_colors, method=Image.Quantize.MEDIANCUT)
            palette = quantized.getpalette()[:n_colors * 3]

            # 获取颜色频次
            color_counts = quantized.getcolors()
            color_counts.sort(reverse=True)

            dominant = []
            for count, idx in color_counts[:n_colors]:
                r = palette[idx * 3]
                g = palette[idx * 3 + 1]
                b = palette[idx * 3 + 2]
                dominant.append((count, (r, g, b)))

            return dominant

    except Exception as e:
        print(f"Error analyzing colors in {image_path}: {e}")
        return []


def is_minimal_style(
    image_path: str,
    max_color_threshold: int = 10,
    min_size: Tuple[int, int] = (64, 64),
    max_size: Tuple[int, int] = (2048, 2048)
) -> Tuple[bool, Dict]:
    """
    判断图片是否符合极简风格

    Args:
        image_path: 图片路径
        max_color_threshold: 最大颜色数量阈值
        min_size: 最小尺寸
        max_size: 最大尺寸

    Returns:
        (是否通过, 详细信息字典)
    """
    result = {
        "path": image_path,
        "passed": False,
        "reasons": [],
        "color_count": 0,
        "dominant_colors": [],
        "size": (0, 0)
    }

    # SVG 文件特殊处理 - 通常适合极简风格
    if image_path.lower().endswith('.svg'):
        result["color_count"] = -2  # SVG marker
        result["passed"] = True
        return True, result

    try:
        with Image.open(image_path) as img:
            # 检查尺寸
            width, height = img.size
            result["size"] = (width, height)

            if width < min_size[0] or height < min_size[1]:
                result["reasons"].append(f"Too small: {width}x{height}")
                return False, result

            if width > max_size[0] or height > max_size[1]:
                result["reasons"].append(f"Too large: {width}x{height}")
                return False, result

            # 检查颜色数量
            color_count = count_colors(image_path)
            result["color_count"] = color_count

            if color_count < 0:
                result["reasons"].append("Failed to analyze colors")
                return False, result

            if color_count > max_color_threshold:
                result["reasons"].append(f"Too many colors: {color_count}")
                return False, result

            # 获取主要颜色
            dominant = analyze_dominant_colors(image_path)
            result["dominant_colors"] = dominant

            # 通过所有检查
            result["passed"] = True
            return True, result

    except Exception as e:
        result["reasons"].append(f"Error: {str(e)}")
        return False, result


def filter_minimal_logos(
    metadata_path: str = "dataset/metadata.json",
    output_dir: str = "dataset/filtered",
    max_colors: int = 10
) -> List[Dict]:
    """
    筛选极简风格的 logo

    Args:
        metadata_path: 元数据文件路径
        output_dir: 筛选后图片的输出目录
        max_colors: 最大颜色数量阈值

    Returns:
        通过筛选的仓库信息列表
    """
    # 读取元数据
    with open(metadata_path, "r", encoding="utf-8") as f:
        repos = json.load(f)

    Path(output_dir).mkdir(parents=True, exist_ok=True)

    filtered = []
    analysis_results = []

    for repo in tqdm(repos, desc="Filtering logos"):
        image_path = repo.get("image_path")

        if not image_path or not os.path.exists(image_path):
            continue

        passed, analysis = is_minimal_style(image_path, max_color_threshold=max_colors)
        analysis_results.append(analysis)

        if passed:
            # 复制通过筛选的图片
            filename = os.path.basename(image_path)
            new_path = os.path.join(output_dir, filename)

            import shutil
            shutil.copy2(image_path, new_path)

            repo["filtered_path"] = new_path
            repo["color_count"] = analysis["color_count"]
            filtered.append(repo)

    # 保存筛选结果
    with open("dataset/filtered_metadata.json", "w", encoding="utf-8") as f:
        json.dump(filtered, f, indent=2, ensure_ascii=False)

    with open("dataset/analysis_results.json", "w", encoding="utf-8") as f:
        json.dump(analysis_results, f, indent=2, ensure_ascii=False)

    print(f"\nFiltered {len(filtered)} / {len(repos)} logos")
    print(f"Filter rate: {len(filtered) / len(repos) * 100:.1f}%")

    return filtered


if __name__ == "__main__":
    print("Filtering minimal style logos...")
    filtered = filter_minimal_logos(max_colors=10)
    print(f"\nDone! {len(filtered)} logos passed the filter")
