"""
获取 GitHub most starred repositories
使用 GitHub Search API
"""

import requests
import json
import time
from typing import List, Dict
from tqdm import tqdm


def fetch_starred_repos(limit: int = 1000, per_page: int = 100) -> List[Dict]:
    """
    获取 GitHub 上 stars 最多的仓库

    Args:
        limit: 最多获取多少个仓库
        per_page: 每页数量（GitHub API 最大 100）

    Returns:
        仓库列表，每个包含 name, owner, stars, description, url
    """
    repos = []
    pages = (limit + per_page - 1) // per_page

    headers = {
        "Accept": "application/vnd.github.v3+json",
        # 如果有 GitHub token，取消下面注释并替换
        # "Authorization": "token YOUR_GITHUB_TOKEN"
    }

    for page in tqdm(range(1, pages + 1), desc="Fetching starred repos"):
        url = "https://api.github.com/search/repositories"
        params = {
            "q": "stars:>1000",
            "sort": "stars",
            "order": "desc",
            "per_page": min(per_page, limit - len(repos)),
            "page": page
        }

        try:
            response = requests.get(url, headers=headers, params=params, timeout=30)
            response.raise_for_status()
            data = response.json()

            for item in data.get("items", []):
                repos.append({
                    "name": item["name"],
                    "owner": item["owner"]["login"],
                    "full_name": item["full_name"],
                    "stars": item["stargazers_count"],
                    "description": item.get("description", ""),
                    "url": item["html_url"],
                    "avatar_url": item["owner"]["avatar_url"],
                    "language": item.get("language", "Unknown")
                })

            # GitHub API 速率限制：未认证 10 次/分钟，认证 30 次/分钟
            time.sleep(2)

        except requests.exceptions.RequestException as e:
            print(f"Error fetching page {page}: {e}")
            time.sleep(5)
            continue

        if len(repos) >= limit:
            break

    return repos[:limit]


def save_repos(repos: List[Dict], output_path: str = "dataset/starred_repos.json"):
    """保存仓库列表到 JSON 文件"""
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(repos, f, indent=2, ensure_ascii=False)
    print(f"Saved {len(repos)} repos to {output_path}")


if __name__ == "__main__":
    print("Fetching most starred repositories from GitHub...")
    repos = fetch_starred_repos(limit=1000)
    save_repos(repos)
    print(f"Done! Fetched {len(repos)} repositories")
