"""Secure, loopback-only local browser UI for one JARVIS product."""
from __future__ import annotations

import argparse
import json
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlsplit

from jarvis_agent import run_agent

MAX_BODY = 1_000_000
ALLOWED_HOSTS = {"127.0.0.1", "localhost"}
WEB_ROOT = Path(__file__).resolve().parent


class Handler(BaseHTTPRequestHandler):
    def _send(self, status: int, body: bytes, content_type: str) -> None:
        self.send_response(status)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        self.send_header("X-Content-Type-Options", "nosniff")
        self.send_header("Referrer-Policy", "no-referrer")
        self.send_header(
            "Content-Security-Policy",
            "default-src 'none'; style-src 'self'; script-src 'self'; connect-src 'self'; "
            "img-src 'self' data:; base-uri 'none'; form-action 'self'; frame-ancestors 'none'",
        )
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self) -> None:
        assets = {
            "/": ("index.html", "text/html; charset=utf-8"),
            "/index.html": ("index.html", "text/html; charset=utf-8"),
            "/app.js": ("app.js", "text/javascript; charset=utf-8"),
            "/styles.css": ("styles.css", "text/css; charset=utf-8"),
        }
        if self.path not in assets:
            self._send(404, b"Not found", "text/plain; charset=utf-8")
            return
        filename, content_type = assets[self.path]
        body = (WEB_ROOT / filename).read_bytes()
        self._send(200, body, content_type)

    def do_POST(self) -> None:
        if self.path != "/api/run":
            self._send(404, b'{"error":"Not found"}', "application/json")
            return
        host = self.headers.get("Host", "").split(":")[0].strip("[]").lower()
        if host not in ALLOWED_HOSTS:
            self._send(403, b'{"error":"Localhost requests only"}', "application/json")
            return
        origin = self.headers.get("Origin")
        if origin:
            parsed = urlsplit(origin)
            if parsed.scheme not in {"http", "https"} or parsed.hostname not in ALLOWED_HOSTS:
                self._send(403, b'{"error":"Local origin required"}', "application/json")
                return
        if self.headers.get_content_type() != "application/json":
            self._send(415, b'{"error":"Content-Type must be application/json"}', "application/json")
            return
        try:
            length = int(self.headers.get("Content-Length", "0"))
        except ValueError:
            length = 0
        if length <= 0 or length > MAX_BODY:
            self._send(413, b'{"error":"Request body must be between 1 byte and 1 MB"}', "application/json")
            return
        try:
            payload = json.loads(self.rfile.read(length).decode("utf-8"))
            if not isinstance(payload, dict):
                raise ValueError("Input must be a JSON object.")
            result = run_agent(payload)
            body = json.dumps(result, ensure_ascii=False).encode("utf-8")
            if len(body) > MAX_BODY:
                self._send(413, b'{"error":"Report exceeds the 1 MB response limit"}', "application/json")
                return
            self._send(200, body, "application/json; charset=utf-8")
        except (UnicodeDecodeError, json.JSONDecodeError, ValueError) as exc:
            body = json.dumps({"error": str(exc)}, ensure_ascii=False).encode("utf-8")
            self._send(400, body, "application/json; charset=utf-8")
        except Exception:
            self._send(500, b'{"error":"Internal processing error"}', "application/json")

    def log_message(self, format: str, *args: object) -> None:
        return


def main() -> int:
    parser = argparse.ArgumentParser(description="Run the JARVIS local browser workspace.")
    parser.add_argument("--port", type=int, default=8765)
    args = parser.parse_args()
    if args.port < 0 or args.port > 65535:
        parser.error("Port must be between 0 and 65535.")
    server = ThreadingHTTPServer(("127.0.0.1", args.port), Handler)
    print(f"JARVIS_UI_URL=http://127.0.0.1:{server.server_port}", flush=True)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
