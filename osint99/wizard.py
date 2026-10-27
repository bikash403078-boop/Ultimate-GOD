"""Guided, optional-input investigation workflow."""
from __future__ import annotations
from datetime import datetime, timezone
from pathlib import Path
import hashlib
import json

from .core import new_case, add_lead, add_finding, save_json
from .collector import search_public_web, check_username, fetch_public_page


def _prompt(label: str) -> str:
    value = input(label).strip()
    return "" if value.lower() in {"-", "skip", "s", "none", "n/a"} else value


def _image_summary(path_value: str) -> dict:
    path = Path(path_value).expanduser()
    if not path.is_file():
        raise ValueError("That image file was not found on this device.")
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    result = {"file_name": path.name, "size_bytes": path.stat().st_size,
              "sha256": digest.hexdigest(), "metadata": {}, "note": "Local file only; no image is uploaded."}
    try:
        from PIL import Image, ExifTags
        with Image.open(path) as image:
            exif = image.getexif()
            result["image_format"] = image.format
            result["dimensions"] = list(image.size)
            result["metadata"] = {str(ExifTags.TAGS.get(k, k)): str(v)[:300]
                                  for k, v in exif.items()
                                  if str(ExifTags.TAGS.get(k, k)).lower() not in {"gpsinfo"}}
    except ImportError:
        result["note"] += " Install Pillow optionally to read non-GPS EXIF metadata."
    except Exception as exc:
        result["image_read_note"] = type(exc).__name__
    return result


def run_guided_investigation() -> None:
    print("\n=== Ultimate GOD | Guided public-source investigation ===")
    print("Enter known information; press Enter or type 'skip' for anything unknown.")
    print("Use this only for yourself, an authorized assessment, or a legitimate public-interest case.")
    title = "Automatic guided investigation"
    case = new_case(title)
    username = _prompt("1/6 Enter username (or press Enter to skip): ")
    phone = _prompt("2/6 Enter phone/WhatsApp number (stored as a lead only; no owner lookup; or skip): ")
    image_path = _prompt("3/6 Enter local image file path (not an image URL; or skip): ")
    social_url = _prompt("4/6 Enter public social-media profile URL (or skip): ")
    target_name = _prompt("5/6 Enter name / public search keywords (or skip): ")
    domain = _prompt("6/6 Enter public website/domain you own or are authorized to assess (or skip): ")

    if target_name:
        add_lead(case, "name/search-keywords", target_name)
    if username:
        add_lead(case, "username", username)
    if phone:
        add_lead(case, "phone-format-only", phone)
    if social_url:
        add_lead(case, "public-social-url", social_url)
    if image_path:
        add_lead(case, "local-image-path", image_path)
    if domain:
        add_lead(case, "authorized-domain", domain)

    report = {"tool": "Ultimate GOD", "created_at": datetime.now(timezone.utc).isoformat(),
              "case_title": title, "scope": "public-source / user-provided inputs only",
              "inputs": {"name_or_keywords": target_name or None, "username": username or None,
                         "phone": ("provided; not reverse-looked-up" if phone else None),
                         "social_url": social_url or None, "image_path": image_path or None,
                         "domain": domain or None},
              "search_results": [], "username_checks": [], "page_extract": None,
              "image_analysis": None, "notes": [
                  "A matching name or username is not proof of identity.",
                  "No private-account access, login scraping, message collection, or location tracking is performed.",
                  "Government ID numbers (Aadhaar/passport) are not searched, inferred, or displayed; use official consent-based verification channels instead."
              ], "errors": []}

    queries = []
    if target_name:
        queries.append(target_name)
    if username:
        queries.append(username)
    if social_url:
        queries.append(social_url)
    seen = set()
    for query in queries[:3]:
        try:
            for result in search_public_web(query, limit=5):
                url = result.get("url", "")
                key = (url, result.get("title", ""))
                if key in seen:
                    continue
                seen.add(key)
                report["search_results"].append({"query": query, **result})
                add_finding(case, "Public search result: " + result.get("title", "(untitled)"),
                            url, "Query: " + query + "; snippet: " + result.get("snippet", ""),
                            "unverified")
        except Exception as exc:
            report["errors"].append({"module": "public_search", "query": query,
                                     "error": type(exc).__name__, "message": str(exc)[:250]})

    if username:
        try:
            report["username_checks"] = check_username(username)
            for item in report["username_checks"]:
                add_finding(case, "Username URL check: " + item.get("service", "unknown"),
                            item.get("final_url", item.get("url", "")),
                            "Result: " + item.get("result", "unknown") + "; title: " + item.get("page_title", ""),
                            "unverified")
        except Exception as exc:
            report["errors"].append({"module": "username_checks", "error": type(exc).__name__,
                                     "message": str(exc)[:250]})

    if social_url:
        try:
            report["page_extract"] = fetch_public_page(social_url)
            page = report["page_extract"]
            add_finding(case, "Public page extraction: " + (page.get("title") or page.get("final_url", social_url)),
                        page.get("final_url", social_url),
                        "Description: " + page.get("description", "") + "\nText excerpt: " + page.get("text", "")[:3000],
                        "unverified")
        except Exception as exc:
            report["errors"].append({"module": "page_extract", "error": type(exc).__name__,
                                     "message": str(exc)[:250]})

    if image_path:
        try:
            report["image_analysis"] = _image_summary(image_path)
        except Exception as exc:
            report["errors"].append({"module": "image_analysis", "error": type(exc).__name__,
                                     "message": str(exc)[:250]})

    if domain:
        try:
            from .domainintel import investigate_domain
            report["domain_intelligence"] = investigate_domain(domain)
        except Exception as exc:
            report["errors"].append({"module": "domain_intelligence", "error": type(exc).__name__,
                                     "message": str(exc)[:250]})

    report["case"] = case
    out = "ultimate_god_investigation.json"
    Path(out).expanduser().write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print("\n=== Investigation summary ===")
    print(f"Public search results: {len(report['search_results'])}")
    print(f"Username URL checks: {len(report['username_checks'])}")
    print(f"Public page extracted: {'yes' if report['page_extract'] else 'no'}")
    print(f"Image analyzed locally: {'yes' if report['image_analysis'] else 'no'}")
    print(f"Errors / blocked sources: {len(report['errors'])}")
    print(f"Report saved automatically to: {out}")
    print("Review every source manually; a result is a lead, not identity confirmation.")
