"""
Minimal GitHub REST API integration for validating student submissions.
Works unauthenticated against public repos (60 req/hr rate limit from a
single IP - set GITHUB_TOKEN in the environment to raise that to 5000/hr).
"""

import os
import re
import requests

GITHUB_API = "https://api.github.com"


def _headers():
    token = os.environ.get("GITHUB_TOKEN")
    return {"Authorization": f"token {token}"} if token else {}


def parse_owner_repo(repo_url: str):
    """Extract (owner, repo) from a github.com URL, or None if it doesn't match."""
    match = re.search(r"github\.com/([^/\s]+)/([^/\s]+)", repo_url.strip())
    if not match:
        return None
    owner, repo = match.group(1), match.group(2).removesuffix(".git")
    return owner, repo


def fetch_repo_info(repo_url: str, timeout: float = 5.0):
    """
    Returns {"exists": bool, "last_commit_at": iso_str_or_None, "error": str_or_None}.
    Fails soft - network issues never block a submission from being saved.
    """
    parsed = parse_owner_repo(repo_url)
    if not parsed:
        return {"exists": False, "last_commit_at": None, "error": "Not a valid github.com URL"}

    owner, repo = parsed
    try:
        resp = requests.get(f"{GITHUB_API}/repos/{owner}/{repo}", headers=_headers(), timeout=timeout)
        if resp.status_code == 404:
            return {"exists": False, "last_commit_at": None, "error": "Repository not found or private"}
        resp.raise_for_status()

        commits = requests.get(
            f"{GITHUB_API}/repos/{owner}/{repo}/commits",
            headers=_headers(), params={"per_page": 1}, timeout=timeout,
        )
        last_commit_at = None
        if commits.ok and commits.json():
            last_commit_at = commits.json()[0]["commit"]["committer"]["date"]

        return {"exists": True, "last_commit_at": last_commit_at, "error": None}
    except requests.RequestException as exc:
        return {"exists": False, "last_commit_at": None, "error": f"Could not reach GitHub: {exc}"}
