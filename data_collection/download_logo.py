"""
下载 GitHub 仓库的 Logo 图片
使用 GitHub Open Graph API 获取仓库预览图
"""

import requests
import json
import os
from pathlib import Path
from typing import List, Dict
from tqdm import tqdm
import time


def get_github_og_image(owner: str, repo: str) -> str:
    """
    获取 GitHub 仓库 Open Graph 图片 URL
    GitHub 会自动生成仓库的 social preview 图片
    """
    # GitHub Open Graph 图片 URL 格式
    return f"https://opengraph.githubassets.com/1/{owner}/{repo}"


def download_image(url: str, output_path: str, timeout: int = 30) -> bool:
    """
    下载图片到指定路径

    Args:
        url: 图片 URL
        output_path: 保存路径
        timeout: 超时时间

    Returns:
        是否成功
    """
    try:
        headers = {
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36"
        }
        response = requests.get(url, headers=headers, timeout=timeout)
        response.raise_for_status()

        # 检查 Content-Type 是否为图片
        content_type = response.headers.get("Content-Type", "")
        if not content_type.startswith("image/"):
            print(f"Warning: {url} is not an image (Content-Type: {content_type})")
            return False

        # 确保目录存在
        Path(output_path).parent.mkdir(parents=True, exist_ok=True)

        with open(output_path, "wb") as f:
            f.write(response.content)

        return True

    except Exception as e:
        print(f"Error downloading {url}: {e}")
        return False


def download_repo_logos(
    repos: List[Dict],
    output_dir: str = "dataset/raw",
    delay: float = 1.0
) -> List[Dict]:
    """
    批量下载仓库 logo

    Args:
        repos: 仓库列表
        output_dir: 图片保存目录
        delay: 下载间隔（秒）

    Returns:
        成功下载的仓库信息列表（包含图片路径）
    """
    results = []

    for repo in tqdm(repos, desc="Downloading logos"):
        owner = repo["owner"]
        name = repo["name"]

        # 构建文件名
        filename = f"{owner}_{name}.png"
        output_path = os.path.join(output_dir, filename)

        # 如果已存在则跳过
        if os.path.exists(output_path):
            results.append({**repo, "image_path": output_path})
            continue

        # 下载图片
        image_url = get_github_og_image(owner, name)
        success = download_image(image_url, output_path)

        if success:
            results.append({**repo, "image_path": output_path})

        time.sleep(delay)

    return results


def merge_repos(starred_path: str, trending_path: str, output_path: str):
    """
    合并 starred 和 trending 仓库列表，去重
    """
    all_repos = []

    # 读取 starred repos
    if os.path.exists(starred_path):
        with open(starred_path, "r", encoding="utf-8") as f:
            starred = json.load(f)
            for repo in starred:
                repo["source"] = "starred"
            all_repos.extend(starred)

    # 读取 trending repos
    if os.path.exists(trending_path):
        with open(trending_path, "r", encoding="utf-8") as f:
            trending = json.load(f)
            for repo in trending:
                if "source" not in repo:
                    repo["source"] = "trending"
            all_repos.extend(trending)

    # 去重（以 full_name 为准）
    seen = set()
    unique_repos = []
    for repo in all_repos:
        if repo["full_name"] not in seen:
            seen.add(repo["full_name"])
            unique_repos.append(repo)

    # 保存
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(unique_repos, f, indent=2, ensure_ascii=False)

    print(f"Merged {len(all_repos)} repos, {len(unique_repos)} unique")
    return unique_repos


if __name__ == "__main__":
    # 首先合并仓库列表
    print("Merging repo lists...")
    repos = merge_repos(
        "dataset/starred_repos.json",
        "dataset/trending_repos.json",
        "dataset/all_repos.json"
    )

    # 下载 logo
    print(f"\nDownloading logos for {len(repos)} repos...")
    results = download_repo_logos(repos, output_dir="dataset/raw")

    # 更新元数据
    with open("dataset/metadata.json", "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2, ensure_ascii=False)

    print(f"\nDone! Downloaded {len(results)} logos")
