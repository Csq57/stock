"""
GitHub starred repository analyser.

Fetches the public starred repositories of a GitHub user, filters those related
to stock / quantitative trading, and produces a summary report.

Usage:
    python analysis/analyse_starred.py <github_username>
    python analysis/analyse_starred.py <github_username> --token <YOUR_PAT>
"""

import argparse
import json
import sys
import time
from typing import List, Optional

import requests


STOCK_KEYWORDS = [
    "stock", "quant", "trading", "backtest", "finance", "投资",
    "量化", "股票", "alpha", "portfolio", "strategy", "factor",
    "market", "equity", "algotrading",
]


def fetch_starred(username: str, token: Optional[str] = None) -> List[dict]:
    """Fetch all starred repositories for *username* via the GitHub REST API."""
    headers = {"Accept": "application/vnd.github+json"}
    if token:
        headers["Authorization"] = f"Bearer {token}"

    repos = []
    page = 1
    while True:
        url = f"https://api.github.com/users/{username}/starred?per_page=100&page={page}"
        resp = requests.get(url, headers=headers, timeout=30)
        if resp.status_code == 403:
            print("[ERROR] GitHub API rate limit hit or access denied. Use --token to authenticate.", file=sys.stderr)
            break
        if resp.status_code != 200:
            print(f"[ERROR] GitHub API returned {resp.status_code}: {resp.text}", file=sys.stderr)
            break
        data = resp.json()
        if not data:
            break
        repos.extend(data)
        page += 1
        time.sleep(0.5)  # be polite to the API
    return repos


def filter_stock_repos(repos: List[dict]) -> List[dict]:
    """Return repos whose name, description or topics match stock/quant keywords."""
    matched = []
    for repo in repos:
        text = " ".join([
            (repo.get("name") or ""),
            (repo.get("description") or ""),
            " ".join(repo.get("topics") or []),
        ]).lower()
        if any(kw in text for kw in STOCK_KEYWORDS):
            matched.append(repo)
    return matched


def print_report(repos: List[dict]):
    """Pretty-print a summary table of matched repositories."""
    if not repos:
        print("No stock/quant related repositories found.")
        return

    print(f"\n{'#':<4} {'Repository':<45} {'Stars':>6}  Description")
    print("-" * 100)
    for i, repo in enumerate(sorted(repos, key=lambda r: r.get("stargazers_count", 0), reverse=True), 1):
        name = repo.get("full_name", "")[:44]
        stars = repo.get("stargazers_count", 0)
        desc = (repo.get("description") or "")[:50]
        print(f"{i:<4} {name:<45} {stars:>6}  {desc}")

    print(f"\nTotal: {len(repos)} repositories")


def main():
    parser = argparse.ArgumentParser(description="Analyse GitHub starred stock/quant repositories")
    parser.add_argument("username", help="GitHub username to analyse")
    parser.add_argument("--token", default=None, help="GitHub personal access token (increases rate limit)")
    parser.add_argument("--output", default=None, help="Save results as JSON to this file path")
    args = parser.parse_args()

    print(f"[INFO] Fetching starred repositories for user: {args.username}")
    all_repos = fetch_starred(args.username, token=args.token)
    print(f"[INFO] Total starred repos fetched: {len(all_repos)}")

    stock_repos = filter_stock_repos(all_repos)
    print(f"[INFO] Stock/quant related repos found: {len(stock_repos)}")

    print_report(stock_repos)

    if args.output:
        with open(args.output, "w", encoding="utf-8") as fh:
            json.dump(stock_repos, fh, ensure_ascii=False, indent=2)
        print(f"\n[INFO] Full results saved to {args.output}")


if __name__ == "__main__":
    main()
