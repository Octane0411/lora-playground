#!/usr/bin/env python3
"""
数据收集主脚本 - 一键运行完整流程
"""

import sys
import os

# 添加父目录到路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from fetch_starred import fetch_starred_repos, save_repos as save_starred
from fetch_trending import fetch_all_trending, save_repos as save_trending
from download_logo import merge_repos, download_repo_logos
from filter_minimal import filter_minimal_logos
import json


def main():
    print("=" * 60)
    print("GitHub Logo 数据收集工具")
    print("=" * 60)

    # Step 1: 获取 starred repos
    print("\n[Step 1/4] 获取 Most Starred Repositories...")
    try:
        starred = fetch_starred_repos(limit=500)  # 先测试 500 个
        save_starred(starred)
        print(f"✓ 获取了 {len(starred)} 个 starred repos")
    except Exception as e:
        print(f"✗ Error: {e}")
        starred = []

    # Step 2: 获取 trending repos
    print("\n[Step 2/4] 获取 Trending Repositories...")
    try:
        trending = fetch_all_trending()
        save_trending(trending)
        print(f"✓ 获取了 {len(trending)} 个 trending repos")
    except Exception as e:
        print(f"✗ Error: {e}")
        trending = []

    # Step 3: 下载 logo
    print("\n[Step 3/4] 下载 Logo 图片...")
    try:
        repos = merge_repos(
            "dataset/starred_repos.json",
            "dataset/trending_repos.json",
            "dataset/all_repos.json"
        )
        results = download_repo_logos(repos, output_dir="dataset/raw", delay=0.5)

        with open("dataset/metadata.json", "w", encoding="utf-8") as f:
            json.dump(results, f, indent=2, ensure_ascii=False)

        print(f"✓ 下载了 {len(results)} 个 logos")
    except Exception as e:
        print(f"✗ Error: {e}")
        results = []

    # Step 4: 筛选极简风格
    print("\n[Step 4/4] 筛选极简风格 Logo...")
    try:
        filtered = filter_minimal_logos(
            metadata_path="dataset/metadata.json",
            output_dir="dataset/filtered",
            max_colors=10
        )
        print(f"✓ 筛选出 {len(filtered)} 个极简风格 logos")
    except Exception as e:
        print(f"✗ Error: {e}")

    print("\n" + "=" * 60)
    print("数据收集完成！")
    print("=" * 60)
    print(f"原始数据: dataset/raw/")
    print(f"筛选结果: dataset/filtered/")
    print(f"元数据: dataset/metadata.json")
    print(f"筛选后元数据: dataset/filtered_metadata.json")


if __name__ == "__main__":
    main()
