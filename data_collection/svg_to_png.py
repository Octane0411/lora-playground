#!/usr/bin/env python3
"""
将 SVG 转换为 PNG（用于 LoRA 训练）
使用 CairoSVG 或 cairosvg 库
"""

import os
import sys
from pathlib import Path
from typing import List, Tuple
import subprocess
import argparse


def check_cairosvg() -> bool:
    """检查是否安装了 cairosvg"""
    try:
        import cairosvg
        return True
    except ImportError:
        return False


def convert_with_cairosvg(svg_path: str, png_path: str, size: Tuple[int, int] = (512, 512)) -> bool:
    """
    使用 CairoSVG 将 SVG 转换为 PNG

    Args:
        svg_path: SVG 文件路径
        png_path: 输出 PNG 路径
        size: 输出尺寸 (width, height)

    Returns:
        是否成功
    """
    try:
        import cairosvg

        cairosvg.svg2png(
            url=svg_path,
            write_to=png_path,
            output_width=size[0],
            output_height=size[1],
            background_color="white"  # 白色背景
        )
        return True

    except Exception as e:
        print(f"Error converting {svg_path}: {e}")
        return False


def convert_with_inkscape(svg_path: str, png_path: str, size: Tuple[int, int] = (512, 512)) -> bool:
    """
    使用 Inkscape 将 SVG 转换为 PNG（备用方案）

    Args:
        svg_path: SVG 文件路径
        png_path: 输出 PNG 路径
        size: 输出尺寸

    Returns:
        是否成功
    """
    try:
        cmd = [
            "inkscape",
            svg_path,
            "--export-filename", png_path,
            "--export-width", str(size[0]),
            "--export-height", str(size[1]),
            "--export-background", "white"
        ]

        result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
        return result.returncode == 0

    except Exception as e:
        print(f"Inkscape error for {svg_path}: {e}")
        return False


def convert_with_imagemagick(svg_path: str, png_path: str, size: Tuple[int, int] = (512, 512)) -> bool:
    """
    使用 ImageMagick 将 SVG 转换为 PNG（备用方案）

    Args:
        svg_path: SVG 文件路径
        png_path: 输出 PNG 路径
        size: 输出尺寸

    Returns:
        是否成功
    """
    try:
        cmd = [
            "convert",
            "-background", "white",
            "-resize", f"{size[0]}x{size[1]}",
            svg_path,
            png_path
        ]

        result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
        return result.returncode == 0

    except Exception as e:
        print(f"ImageMagick error for {svg_path}: {e}")
        return False


def convert_svg_to_png(
    svg_path: str,
    png_path: str,
    size: Tuple[int, int] = (512, 512),
    method: str = "auto"
) -> bool:
    """
    转换单个 SVG 到 PNG

    Args:
        svg_path: SVG 文件路径
        png_path: 输出 PNG 路径
        size: 输出尺寸
        method: 转换方法 ("auto", "cairosvg", "inkscape", "imagemagick")

    Returns:
        是否成功
    """
    # 确保输出目录存在
    Path(png_path).parent.mkdir(parents=True, exist_ok=True)

    # 如果已存在则跳过
    if os.path.exists(png_path):
        return True

    # 选择转换方法
    if method == "auto":
        if check_cairosvg():
            method = "cairosvg"
        else:
            # 检查 inkscape
            try:
                subprocess.run(["inkscape", "--version"], capture_output=True, check=True)
                method = "inkscape"
            except:
                method = "imagemagick"

    # 执行转换
    if method == "cairosvg":
        return convert_with_cairosvg(svg_path, png_path, size)
    elif method == "inkscape":
        return convert_with_inkscape(svg_path, png_path, size)
    elif method == "imagemagick":
        return convert_with_imagemagick(svg_path, png_path, size)
    else:
        print(f"Unknown method: {method}")
        return False


def batch_convert(
    input_dir: str = "dataset/simple_icons",
    output_dir: str = "dataset/simple_icons",
    size: Tuple[int, int] = (512, 512),
    method: str = "auto"
) -> int:
    """
    批量转换 SVG 到 PNG

    Args:
        input_dir: SVG 文件目录
        output_dir: PNG 输出目录
        size: 输出尺寸
        method: 转换方法

    Returns:
        成功转换的数量
    """
    # 查找所有 SVG 文件
    svg_files = list(Path(input_dir).glob("*.svg"))
    print(f"Found {len(svg_files)} SVG files")

    if not svg_files:
        print(f"No SVG files found in {input_dir}")
        return 0

    # 确定转换方法
    if method == "auto":
        if check_cairosvg():
            method = "cairosvg"
            print("Using CairoSVG for conversion")
        else:
            print("CairoSVG not found, trying alternatives...")
            try:
                subprocess.run(["inkscape", "--version"], capture_output=True, check=True)
                method = "inkscape"
                print("Using Inkscape for conversion")
            except:
                method = "imagemagick"
                print("Using ImageMagick for conversion")

    # 批量转换
    success_count = 0
    from tqdm import tqdm

    for svg_file in tqdm(svg_files, desc="Converting SVG to PNG"):
        png_path = os.path.join(output_dir, svg_file.stem + ".png")

        if convert_svg_to_png(str(svg_file), png_path, size, method):
            success_count += 1

    print(f"\nConverted {success_count} / {len(svg_files)} files")
    return success_count


def main():
    parser = argparse.ArgumentParser(description="Convert SVG icons to PNG for training")
    parser.add_argument("--input", "-i", default="dataset/simple_icons", help="Input directory with SVG files")
    parser.add_argument("--output", "-o", default="dataset/simple_icons", help="Output directory for PNG files")
    parser.add_argument("--size", "-s", type=int, default=512, help="Output size (width and height)")
    parser.add_argument("--method", "-m", default="auto", choices=["auto", "cairosvg", "inkscape", "imagemagick"],
                        help="Conversion method")

    args = parser.parse_args()

    print("=" * 60)
    print("SVG to PNG Converter")
    print("=" * 60)
    print(f"Input: {args.input}")
    print(f"Output: {args.output}")
    print(f"Size: {args.size}x{args.size}")
    print(f"Method: {args.method}")
    print()

    count = batch_convert(
        input_dir=args.input,
        output_dir=args.output,
        size=(args.size, args.size),
        method=args.method
    )

    print(f"\nDone! Converted {count} icons to PNG")


if __name__ == "__main__":
    main()
