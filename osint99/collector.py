"""Conservative public-page checks; no login, bypass, or private-data access."""
from html.parser import HTMLParser
from urllib.request import Request, urlopen
from urllib.error import HTTPError, URLError
from .core import normalize_url, username_candidates
from urllib.parse import urlencode, urlparse, parse_qs
import re


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


class _SearchResults(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.results = []
        self.current = None
        self.capture = None

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        classes = attrs.get("class", "").split()
        if tag == "a" and "result__a" in classes:
            self.current = {"title": "", "url": attrs.get("href", ""), "snippet": ""}
            self.capture = "title"
        elif self.current is not None and tag in {"a", "div", "td"} and (
            "result__snippet" in classes or "result-snippet" in classes
        ):
            self.capture = "snippet"

    def handle_data(self, data):
        if self.current is not None and self.capture in {"title", "snippet"}:
            self.current[self.capture] += data

    def handle_endtag(self, tag):
        if tag == "a" and self.current is not None and self.capture == "title":
            raw = self.current["url"]
            parsed = urlparse(raw)
            if parsed.netloc.endswith("duckduckgo.com") and parsed.path.startswith("/l/"):
                raw = parse_qs(parsed.query).get("uddg", [raw])[0]
            self.current["url"] = raw
            self.current["title"] = self.current["title"].strip()
            self.capture = None
            if self.current["title"] and raw.startswith(("https://", "http://")):
                self.results.append(self.current)
            self.current = None
        elif tag in {"div", "td"} and self.capture == "snippet":
            self.capture = None


def search_public_web(query: str, timeout: int = 12, limit: int = 8) -> list[dict]:
    """Retrieve actual public DuckDuckGo HTML results; may be blocked or rate-limited."""
    query = query.strip()
    if not query:
        raise ValueError("Search query is required.")
    endpoint = "https://html.duckduckgo.com/html/?" + urlencode({"q": query})
    request = Request(endpoint, headers={"User-Agent": "Mozilla/5.0 (compatible; UltimateGOD/0.4; public-source research)"})
    try:
        with urlopen(request, timeout=timeout) as response:
            page = response.read(1_500_000).decode("utf-8", errors="replace")
    except (HTTPError, URLError, TimeoutError, OSError) as exc:
        raise RuntimeError(f"Search provider unavailable ({type(exc).__name__}); open DuckDuckGo manually and record sources.") from exc
    parser = _SearchResults()
    parser.feed(page)
    if not parser.results:
        raise RuntimeError("No results could be parsed. The provider may have changed its HTML or shown a challenge page.")
    return parser.results[:max(1, min(limit, 10))]


class _PageText(HTMLParser):
    SKIP = {"script", "style", "noscript", "svg", "nav", "footer"}
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.title = False
        self.title_parts = []
        self.text_parts = []
        self.links = []
        self.meta = {}
        self.skip_depth = 0
    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if tag == "title":
            self.title = True
        if tag in self.SKIP:
            self.skip_depth += 1
        if tag == "meta":
            key = (attrs.get("name") or attrs.get("property") or "").lower()
            value = attrs.get("content", "").strip()
            if key in {"description", "og:title", "og:description"} and value:
                self.meta[key] = value[:500]
        if tag == "a" and attrs.get("href"):
            self.links.append(attrs["href"])
    def handle_endtag(self, tag):
        if tag == "title":
            self.title = False
        if tag in self.SKIP and self.skip_depth:
            self.skip_depth -= 1
    def handle_data(self, data):
        value = " ".join(data.split())
        if not value:
            return
        if self.title:
            self.title_parts.append(value)
        if not self.skip_depth:
            self.text_parts.append(value)


def fetch_public_page(value: str, timeout: int = 10) -> dict:
    """Extract a bounded amount of readable text and links from a public HTTP(S) page."""
    url = normalize_url(value)
    request = Request(url, headers={"User-Agent": "Mozilla/5.0 (compatible; UltimateGOD/0.4; public-source research)"})
    with urlopen(request, timeout=timeout) as response:
        final_url = response.geturl()
        content_type = response.headers.get("Content-Type", "")
        if "text/html" not in content_type.lower():
            return {"url": url, "final_url": final_url, "status": response.status, "content_type": content_type,
                    "title": "", "description": "", "text": "", "links": [], "note": "Non-HTML response; body not parsed."}
        body = response.read(800_000).decode(response.headers.get_content_charset() or "utf-8", errors="replace")
        status = response.status
    parser = _PageText()
    parser.feed(body)
    text = re.sub(r"\\s+", " ", " ".join(parser.text_parts)).strip()
    base = final_url
    from urllib.parse import urljoin
    links = []
    for href in parser.links:
        absolute = urljoin(base, href)
        if absolute.startswith(("http://", "https://")) and absolute not in links:
            links.append(absolute)
    return {"url": url, "final_url": final_url, "status": status,
            "content_type": content_type, "title": " ".join(parser.title_parts)[:300],
            "description": parser.meta.get("description", parser.meta.get("og:description", "")),
            "text": text[:12000], "links": links[:100],
            "note": "Extracted only content delivered in the public HTML response; scripts, gated content, and hidden server data are not accessed."}
