"""
下载 GitHub 仓库的 Logo 图片
从仓库内容中查找 logo 文件
"""

import requests
import json
import os
import base64
from pathlib import Path
from typing import List, Dict, Optional
from tqdm import tqdm
import time


# 常见的 logo 文件路径（按优先级排序，只包括图片）
LOGO_PATHS = [
    "logo.svg", "icon.svg",  # SVG 优先（可缩放）
    "logo.png", "icon.png",
    "assets/logo.svg", "assets/icon.svg",
    "assets/logo.png", "assets/icon.png",
    "docs/logo.svg", "docs/logo.svg",
    "docs/logo.png", "docs/logo.svg",
    "images/logo.svg", "images/icon.svg",
    "images/logo.png", "images/icon.png",
    "static/logo.svg", "static/icon.svg",
    "static/logo.png", "static/icon.png",
    "public/logo.svg", "public/icon.svg",
    "public/logo.png", "public/icon.png",
    "src/logo.svg", "src/icon.svg",
    "app/logo.svg", "app/icon.svg",
    "brand/logo.svg", "brand/icon.svg",
    "media/logo.svg", "media/icon.svg",
    "resources/logo.svg", "resources/icon.svg",
]


def get_file_from_repo(owner: str, repo: str, path: str) -> Optional[bytes]:
    """
    从 GitHub 仓库获取文件内容

    Args:
        owner: 仓库所有者
        repo: 仓库名
        path: 文件路径

    Returns:
        文件内容，如果不存在则返回 None
    """
    url = f"https://api.github.com/repos/{owner}/{repo}/contents/{path}"
    headers = {
        "Accept": "application/vnd.github.v3+json",
    }

    try:
        response = requests.get(url, headers=headers, timeout=30)
        if response.status_code == 404:
            return None
        response.raise_for_status()

        data = response.json()
        if data.get("type") != "file":
            return None

        # 下载文件内容
        download_url = data.get("download_url")
        if download_url:
            content_response = requests.get(download_url, timeout=30)
            content_response.raise_for_status()
            return content_response.content

        return None

    except Exception as e:
        return None


def find_logo_in_repo(owner: str, repo: str) -> tuple[Optional[bytes], Optional[str]]:
    """
    在仓库中查找 logo 文件

    Returns:
        (文件内容, 文件扩展名) 或 (None, None)
    """
    # 首先尝试直接从常见路径获取
    for path in LOGO_PATHS:
        content = get_file_from_repo(owner, repo, path)
        if content:
            ext = path.split(".")[-1].lower()
            # 只接受图片文件
            if ext in ('png', 'svg', 'jpg', 'jpeg', 'gif'):
                return content, ext

    # 如果没找到，尝试列目录查找
    logo_files = list_repo_images(owner, repo)
    if logo_files:
        # 优先选择文件名包含 logo/icon 的图片
        for filename in logo_files:
            name_lower = filename.lower()
            if 'logo' in name_lower or 'icon' in name_lower:
                content = get_file_from_repo(owner, repo, filename)
                if content:
                    ext = filename.split(".")[-1].lower()
                    return content, ext

        # 如果没有 logo/icon 命名的，返回第一个图片
        first_img = logo_files[0]
        content = get_file_from_repo(owner, repo, first_img)
        if content:
            ext = first_img.split(".")[-1].lower()
            return content, ext

    return None, None


def list_repo_images(owner: str, repo: str, path: str = "") -> List[str]:
    """
    列出仓库中的图片文件

    Args:
        owner: 仓库所有者
        repo: 仓库名
        path: 目录路径（空字符串表示根目录）

    Returns:
        图片文件路径列表
    """
    image_exts = {'.png', '.svg', '.jpg', '.jpeg', '.gif'}
    images = []

    url = f"https://api.github.com/repos/{owner}/{repo}/contents/{path}"
    headers = {"Accept": "application/vnd.github.v3+json"}

    try:
        response = requests.get(url, headers=headers, timeout=30)
        if response.status_code != 200:
            return []

        items = response.json()
        if not isinstance(items, list):
            return []

        for item in items:
            if item.get("type") == "file":
                name = item.get("name", "").lower()
                if any(name.endswith(ext) for ext in image_exts):
                    images.append(item.get("path", ""))
            elif item.get("type") == "dir" and item.get("name", "").lower() in {
                "assets", "images", "static", "public", "docs", "media",
                "brand", "resources", "art", "design", "img"
            }:
                # 递归搜索常见图片目录
                sub_images = list_repo_images(owner, repo, item.get("path", ""))
                images.extend(sub_images)

    except Exception as e:
        pass

    return images


def save_logo(content: bytes, output_path: str) -> bool:
    """保存 logo 文件"""
    try:
        Path(output_path).parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, "wb") as f:
            f.write(content)
        return True
    except Exception as e:
        print(f"Error saving to {output_path}: {e}")
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

        # 在仓库中查找 logo
        content, ext = find_logo_in_repo(owner, name)

        if content and ext:
            # 构建文件名
            filename = f"{owner}_{name}.{ext}"
            output_path = os.path.join(output_dir, filename)

            # 如果已存在则跳过
            if os.path.exists(output_path):
                results.append({**repo, "image_path": output_path, "logo_ext": ext})
                continue

            # 保存 logo
            success = save_logo(content, output_path)

            if success:
                results.append({**repo, "image_path": output_path, "logo_ext": ext})

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
