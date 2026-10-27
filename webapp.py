"""Minimal localhost-only dashboard for Ultimate GOD; standard library only."""
from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import parse_qs
import html
import json
from osint99.core import new_case, add_lead, add_finding, username_candidates, save_json

CASE = new_case("Web dashboard case")


class Handler(BaseHTTPRequestHandler):
    def send_page(self, body: str, status: int = 200) -> None:
        data = body.encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def do_GET(self):
        leads = "".join(f"<li>{html.escape(x['type'])}: {html.escape(x['value'])}</li>" for x in CASE["leads"])
        findings = "".join(
            f"<li><b>{html.escape(x['title'])}</b> — <a rel='noreferrer' href='{html.escape(x['source_url'], quote=True)}'>{html.escape(x['source_url'])}</a><br>{html.escape(x['notes'])} ({html.escape(x['confidence'])})</li>"
            for x in CASE["findings"]
        )
        self.send_page(f"""<!doctype html><html><head><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Ultimate GOD</title><style>body{{font:16px system-ui;max-width:850px;margin:2rem auto;padding:0 1rem}}input,textarea,select,button{{font:inherit;width:100%;padding:.6rem;margin:.3rem 0 1rem}}fieldset{{margin:1rem 0}}li{{overflow-wrap:anywhere;margin:.7rem 0}}.note{{background:#fff4d6;padding:1rem}}</style></head><body>
<h1>Ultimate GOD</h1><p class="note">Public-source research organizer. Use only public or authorized information. This server listens on this device only.</p>
<fieldset><legend>Add lead</legend><form method="post" action="/lead"><label>Type</label><select name="kind"><option>name</option><option>username</option><option>phone-format-only</option><option>other</option></select><label>Search lead</label><input name="value" required><button>Save lead</button></form></fieldset>
<fieldset><legend>Add finding</legend><form method="post" action="/finding"><label>Title</label><input name="title" required><label>Public source URL</label><input name="url" required><label>Notes</label><textarea name="notes"></textarea><label>Confidence</label><select name="confidence"><option>unverified</option><option>low</option><option>medium</option><option>high</option></select><button>Save finding</button></form></fieldset>
<h2>Leads</h2><ul>{leads or '<li>None yet</li>'}</ul><h2>Findings</h2><ul>{findings or '<li>None yet</li>'}</ul>
<form method="post" action="/export"><button>Export JSON report</button></form></body></html>""")

    def do_POST(self):
        global CASE
        length = int(self.headers.get("Content-Length", "0"))
        if length > 20000:
            return self.send_page("Request too large", 413)
        fields = parse_qs(self.rfile.read(length).decode("utf-8"), keep_blank_values=True)
        get = lambda key, default="": fields.get(key, [default])[0]
        try:
            if self.path == "/lead":
                add_lead(CASE, get("kind", "other"), get("value"))
            elif self.path == "/finding":
                add_finding(CASE, get("title"), get("url"), get("notes"), get("confidence", "unverified"))
            elif self.path == "/export":
                payload = json.dumps(CASE, indent=2, ensure_ascii=False)
                self.send_response(200)
                self.send_header("Content-Type", "application/json; charset=utf-8")
                self.send_header("Content-Disposition", 'attachment; filename="ultimate_god_case.json"')
                self.end_headers()
                self.wfile.write(payload.encode("utf-8"))
                return
            else:
                return self.send_page("Not found", 404)
        except ValueError as exc:
            return self.send_page(html.escape(str(exc)), 400)
        self.send_response(303)
        self.send_header("Location", "/")
        self.end_headers()

    def log_message(self, fmt, *args):
        print("dashboard:", fmt % args)


if __name__ == "__main__":
    print("Ultimate GOD dashboard: http://127.0.0.1:8765")
    HTTPServer(("127.0.0.1", 8765), Handler).serve_forever()
