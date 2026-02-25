"""
获取 GitHub Trending repositories
由于 GitHub 没有 Trending API，需要爬取网页
"""

import requests
import json
import time
from typing import List, Dict
from bs4 import BeautifulSoup
from tqdm import tqdm


def fetch_trending_repos(language: str = "", since: str = "daily") -> List[Dict]:
    """
    获取 GitHub Trending 仓库

    Args:
        language: 编程语言筛选，如 "python", "javascript"，空字符串表示所有语言
        since: 时间范围，"daily", "weekly", "monthly"

    Returns:
        仓库列表
    """
    repos = []

    # 构建 URL
    url = "https://github.com/trending"
    if language:
        url += f"/{language}"
    url += f"?since={since}"

    headers = {
        "Accept": "text/html",
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36"
    }

    try:
        response = requests.get(url, headers=headers, timeout=30)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, "html.parser")

        # 解析 trending 仓库列表
        articles = soup.find_all("article", class_="Box-row")

        for article in articles:
            try:
                # 获取仓库名
                h2 = article.find("h2")
                if not h2:
                    continue

                a_tag = h2.find("a")
                if not a_tag:
                    continue

                full_name = a_tag.get("href", "").strip("/")
                if not full_name:
                    continue

                parts = full_name.split("/")
                if len(parts) != 2:
                    continue

                owner, name = parts

                # 获取描述
                description_p = article.find("p", class_="col-9")
                description = ""
                if description_p:
                    description = description_p.get_text(strip=True)

                # 获取 stars 数（trending 页面可能显示今日新增 stars）
                stars_span = article.find("span", class_="d-inline-block")
                stars = 0
                if stars_span:
                    stars_text = stars_span.get_text(strip=True)
                    # 提取数字
                    import re
                    match = re.search(r'[\d,]+', stars_text)
                    if match:
                        stars = int(match.group().replace(",", ""))

                repos.append({
                    "name": name,
                    "owner": owner,
                    "full_name": full_name,
                    "stars": stars,
                    "description": description,
                    "url": f"https://github.com/{full_name}",
                    "language": language or "Unknown",
                    "source": f"trending_{since}"
                })

            except Exception as e:
                print(f"Error parsing article: {e}")
                continue

    except requests.exceptions.RequestException as e:
        print(f"Error fetching trending: {e}")

    return repos


def fetch_all_trending() -> List[Dict]:
    """获取多个语言和时间范围的 trending 仓库"""
    all_repos = []

    # 不同语言的 trending
    languages = ["", "python", "javascript", "typescript", "go", "rust", "java"]
    since_options = ["daily", "weekly"]

    for language in tqdm(languages, desc="Languages"):
        for since in since_options:
            repos = fetch_trending_repos(language=language, since=since)
            all_repos.extend(repos)
            time.sleep(1)  # 礼貌性延迟

    # 去重
    seen = set()
    unique_repos = []
    for repo in all_repos:
        if repo["full_name"] not in seen:
            seen.add(repo["full_name"])
            unique_repos.append(repo)

    return unique_repos


def save_repos(repos: List[Dict], output_path: str = "dataset/trending_repos.json"):
    """保存仓库列表到 JSON 文件"""
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(repos, f, indent=2, ensure_ascii=False)
    print(f"Saved {len(repos)} repos to {output_path}")


if __name__ == "__main__":
    print("Fetching trending repositories from GitHub...")
    repos = fetch_all_trending()
    save_repos(repos)
    print(f"Done! Fetched {len(repos)} unique repositories")
