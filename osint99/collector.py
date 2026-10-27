"""Conservative public-page checks; no login, bypass, or private-data access."""
from html.parser import HTMLParser
from urllib.request import Request, urlopen
from urllib.error import HTTPError, URLError
from .core import normalize_url, username_candidates


class _Metadata(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.title = False
        self.title_text = []
        self.meta = {}

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if tag.lower() == "title":
            self.title = True
        if tag.lower() == "meta":
            key = (attrs.get("name") or attrs.get("property") or "").lower()
            value = attrs.get("content", "").strip()
            if key in {"description", "og:title", "og:description"} and value:
                self.meta[key] = value[:500]

    def handle_endtag(self, tag):
        if tag.lower() == "title":
            self.title = False

    def handle_data(self, data):
        if self.title and data.strip():
            self.title_text.append(data.strip())


def check_public_url(value: str, timeout: int = 8) -> dict:
    """Fetch at most 512 KiB of a public HTTP(S) page and summarize response metadata."""
    url = normalize_url(value)
    if not url:
        raise ValueError("URL is required.")
    request = Request(url, headers={"User-Agent": "UltimateGOD/0.2 (public-source research; contact: repository README)"})
    result = {"url": url, "status": None, "final_url": url, "page_title": "", "description": "",
              "result": "inconclusive", "note": ""}
    try:
        with urlopen(request, timeout=timeout) as response:
            result["status"] = response.status
            result["final_url"] = response.geturl()
            content_type = response.headers.get("Content-Type", "")
            if "text/html" not in content_type.lower():
                result["result"] = "responded-non-html"
                result["note"] = "The server responded, but did not return an HTML page."
                return result
            raw = response.read(512 * 1024)
            charset = response.headers.get_content_charset() or "utf-8"
            document = raw.decode(charset, errors="replace")
            parser = _Metadata()
            parser.feed(document)
            result["page_title"] = " ".join(parser.title_text)[:300] or parser.meta.get("og:title", "")
            result["description"] = parser.meta.get("description", parser.meta.get("og:description", ""))[:500]
            result["result"] = "http-success"
            result["note"] = "HTTP success only. This does not prove the profile is genuine or belongs to the searched person."
    except HTTPError as exc:
        result["status"] = exc.code
        result["final_url"] = exc.geturl() or url
        result["result"] = "http-error"
        result["note"] = "Inconclusive: the site returned an HTTP error; blocked, rate-limited, and missing pages may look similar."
    except (URLError, TimeoutError, OSError, ValueError) as exc:
        result["result"] = "network-error"
        result["note"] = f"Could not verify the page: {type(exc).__name__}. Network failures are inconclusive."
    return result


def check_username(username: str) -> list[dict]:
    """Check a small set of public profile URL candidates without logging in."""
    results = []
    for candidate in username_candidates(username):
        item = check_public_url(candidate["url"])
        item["service"] = candidate["service"]
        results.append(item)
    return results


def search_public_web(query: str, timeout: int = 10, limit: int = 8) -> list[dict]:
    """Return a public search URL when automated search results are unavailable."""
    from urllib.parse import urlencode
    query = query.strip()
    if not query:
        raise ValueError("Search query is required.")
    url = "https://duckduckgo.com/?" + urlencode({"q": query})
    return [{"title": "Open public web search (review results manually)", "url": url}]
