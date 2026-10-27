"""Core helpers for a lawful, public-source OSINT research workflow."""
from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urlparse
import json
import re


def now_utc() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def new_case(title: str) -> dict:
    return {
        "tool": "Ultimate GOD",
        "created_at": now_utc(),
        "title": title.strip() or "Untitled case",
        "leads": [],
        "findings": [],
    }


def normalize_url(value: str) -> str:
    value = value.strip()
    if not value:
        return ""
    if "://" not in value:
        value = "https://" + value
    parsed = urlparse(value)
    if parsed.scheme not in ("http", "https") or not parsed.hostname:
        raise ValueError("Enter a valid http(s) URL or domain.")
    return parsed.geturl()


def url_details(value: str) -> dict:
    normalized = normalize_url(value)
    parsed = urlparse(normalized)
    return {
        "url": normalized,
        "scheme": parsed.scheme,
        "domain": parsed.hostname,
        "path": parsed.path or "/",
        "query_present": bool(parsed.query),
    }


def username_candidates(username: str) -> list[dict]:
    user = username.strip().lstrip("@")
    if not user or not re.fullmatch(r"[A-Za-z0-9._-]{1,64}", user):
        raise ValueError("Username should contain 1–64 letters, numbers, dots, underscores, or hyphens.")
    services = {
        "GitHub": f"https://github.com/{user}",
        "Reddit": f"https://www.reddit.com/user/{user}/",
        "Instagram": f"https://www.instagram.com/{user}/",
        "TikTok": f"https://www.tiktok.com/@{user}",
        "YouTube": f"https://www.youtube.com/@{user}",
    }
    return [{"service": name, "url": url, "verified": False} for name, url in services.items()]


def add_lead(case: dict, kind: str, value: str) -> dict:
    lead = {"type": kind, "value": value.strip(), "added_at": now_utc()}
    case.setdefault("leads", []).append(lead)
    return lead


def add_finding(case: dict, title: str, source_url: str, notes: str, confidence: str = "unverified") -> dict:
    source = normalize_url(source_url)
    if confidence not in {"unverified", "low", "medium", "high"}:
        raise ValueError("Confidence must be unverified, low, medium, or high.")
    finding = {
        "title": title.strip(),
        "source_url": source,
        "notes": notes.strip(),
        "confidence": confidence,
        "recorded_at": now_utc(),
    }
    case.setdefault("findings", []).append(finding)
    return finding


def save_json(case: dict, path: str = "ultimate_god_case.json") -> str:
    destination = Path(path).expanduser()
    destination.write_text(json.dumps(case, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return str(destination)
