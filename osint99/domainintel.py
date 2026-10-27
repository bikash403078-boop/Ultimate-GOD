"""Passive domain intelligence from public registration and certificate sources."""
from __future__ import annotations
import json
import re
import socket
from urllib.parse import urlencode
from urllib.request import Request, urlopen
from urllib.error import HTTPError, URLError
from datetime import datetime, timezone


def validate_domain(value: str) -> str:
    domain = value.strip().lower().rstrip(".")
    if "://" in domain or "/" in domain or ":" in domain or not re.fullmatch(r"(?=.{1,253}$)(?:[a-z0-9](?:[a-z0-9-]{0,61}[a-z0-9])?\.)+[a-z]{2,63}", domain):
        raise ValueError("Enter a domain name only, such as example.com (no scheme, path, or IP address).")
    return domain


def _get_json(url: str, timeout: int = 10):
    req = Request(url, headers={"User-Agent": "UltimateGOD/0.3 (passive domain research)", "Accept": "application/json"})
    with urlopen(req, timeout=timeout) as response:
        return json.loads(response.read(2_000_000).decode("utf-8", errors="replace"))


def investigate_domain(value: str) -> dict:
    """Collect passive public RDAP and certificate-transparency data for a domain."""
    domain = validate_domain(value)
    result = {
        "domain": domain,
        "collected_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "scope": "passive public-source domain research",
        "sources": [],
        "errors": [],
        "dns": [],
        "registration": {},
        "certificates": [],
    }

    # DNS resolution only; no port scanning or service probing.
    try:
        addresses = sorted({item[4][0] for item in socket.getaddrinfo(domain, None, type=socket.SOCK_STREAM)})
        result["dns"] = addresses
        result["sources"].append({"name": "System DNS resolver", "url": "local resolver", "status": "success"})
    except OSError as exc:
        result["errors"].append({"source": "DNS", "error": type(exc).__name__})

    # RDAP domain registration metadata via the public rdap.org bootstrap service.
    try:
        data = _get_json("https://rdap.org/domain/" + domain)
        events = data.get("events", [])
        nameservers = [x.get("ldhName") for x in data.get("nameservers", []) if x.get("ldhName")]
        entities = []
        for entity in data.get("entities", []):
            roles = entity.get("roles", [])
            if any(role in {"registrar"} for role in roles):
                entities.append({"roles": roles, "handle": entity.get("handle")})
        result["registration"] = {
            "ldhName": data.get("ldhName"),
            "status": data.get("status", []),
            "events": [{"action": e.get("eventAction"), "date": e.get("eventDate")} for e in events],
            "nameservers": nameservers,
            "registrar_entities": entities,
        }
        result["sources"].append({"name": "RDAP", "url": "https://rdap.org/domain/" + domain, "status": "success"})
    except (HTTPError, URLError, TimeoutError, OSError, ValueError, json.JSONDecodeError) as exc:
        result["errors"].append({"source": "RDAP", "error": type(exc).__name__})

    # Certificate Transparency search is passive and reveals certificate names, not proof of active hosts.
    try:
        query = urlencode({"q": "%." + domain, "output": "json"})
        data = _get_json("https://crt.sh/?" + query)
        seen = set()
        for item in data if isinstance(data, list) else []:
            names = item.get("name_value", "")
            for name in names.splitlines():
                name = name.strip().lower().lstrip("*.")
                if name == domain or name.endswith("." + domain):
                    seen.add(name)
        result["certificates"] = sorted(seen)[:500]
        result["sources"].append({"name": "Certificate Transparency (crt.sh)", "url": "https://crt.sh/?" + query, "status": "success"})
    except (HTTPError, URLError, TimeoutError, OSError, ValueError, json.JSONDecodeError) as exc:
        result["errors"].append({"source": "Certificate Transparency", "error": type(exc).__name__})

    result["summary"] = {
        "resolved_addresses": len(result["dns"]),
        "certificate_names": len(result["certificates"]),
        "registration_data_found": bool(result["registration"]),
        "sources_succeeded": len(result["sources"]),
        "sources_failed": len(result["errors"]),
    }
    return result
