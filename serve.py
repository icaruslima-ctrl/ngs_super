#!/usr/bin/env python3
"""Local dev server for the synced Claude Design pages.

The .dc.html files expect window.React / window.ReactDOM to already exist —
the design host provides them. Rather than editing the synced files (which
would make them diverge from the project and complicate re-syncing), this
server injects the vendored React UMD builds into <head> on the way out.

    python3 serve.py [port]        # default 8000

Then open http://localhost:8000/
"""
import http.server
import re
import socketserver
import sys
from pathlib import Path

ROOT = Path(__file__).parent.resolve()
PORT = int(sys.argv[1]) if len(sys.argv) > 1 else 8000

INJECT = (
    b'<script src="/vendor/react.production.min.js"></script>\n'
    b'<script src="/vendor/react-dom.production.min.js"></script>\n'
)

PAGES = [
    ("What is super - Responsive.dc.html", "Responsive (switches at 1280px)"),
    ("What is super.dc.html", "Desktop"),
    ("What is super - Mobile.dc.html", "Mobile (390px)"),
]

INDEX = """<!doctype html><meta charset="utf-8">
<title>NGS &mdash; What is super</title>
<style>
  body {{ font-family: -apple-system, "Helvetica Neue", Arial, sans-serif;
         background: #f7f9f7; color: #17453a; margin: 0; padding: 56px 28px; }}
  main {{ max-width: 620px; margin: 0 auto; }}
  h1 {{ font-size: 30px; margin: 0 0 6px; letter-spacing: -0.02em; }}
  p.sub {{ color: #5c6b64; margin: 0 0 32px; }}
  a.page {{ display: block; background: #fff; border: 1px solid #dfe8e2;
            border-radius: 14px; padding: 18px 22px; margin-bottom: 12px;
            text-decoration: none; color: #17453a; }}
  a.page:hover {{ border-color: #4bb462; }}
  a.page b {{ display: block; font-size: 17px; }}
  a.page span {{ color: #5c6b64; font-size: 14px; }}
</style>
<main>
  <h1>What is super</h1>
  <p class="sub">Synced from the Claude Design project &ldquo;Like-for-like page design&rdquo;.</p>
  {links}
</main>
"""


class Handler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *a, **kw):
        super().__init__(*a, directory=str(ROOT), **kw)

    def do_GET(self):
        if self.path in ("/", "/index.html"):
            links = "\n  ".join(
                f'<a class="page" href="/{name}"><b>{label}</b><span>{name}</span></a>'
                for name, label in PAGES
            )
            return self._send(INDEX.format(links=links).encode(), "text/html")

        path = Path(self.translate_path(self.path))
        if path.suffix == ".html" and path.is_file():
            html = path.read_bytes()
            # Inject React immediately before the runtime that requires it.
            patched, n = re.subn(rb'(?=<script src="\./support\.js")', INJECT, html, count=1)
            if n == 0:
                patched = html.replace(b"</head>", INJECT + b"</head>", 1)
            return self._send(patched, "text/html")

        return super().do_GET()

    def _send(self, body, ctype):
        self.send_response(200)
        self.send_header("Content-Type", f"{ctype}; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, fmt, *args):
        if "404" in (fmt % args):
            super().log_message(fmt, *args)


class Server(socketserver.TCPServer):
    allow_reuse_address = True


if __name__ == "__main__":
    with Server(("127.0.0.1", PORT), Handler) as httpd:
        print(f"Serving {ROOT} at http://localhost:{PORT}/  (Ctrl-C to stop)")
        httpd.serve_forever()
