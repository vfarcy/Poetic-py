#!/usr/bin/env python3
import argparse
import json
import os
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer

try:
    from bespoke_engine import BespokeRuntimeError, run_bespoke
except ImportError:
    from tools.bespoke_engine import BespokeRuntimeError, run_bespoke


class SiteHandler(SimpleHTTPRequestHandler):
    def __init__(self, *args, site_dir=None, **kwargs):
        self._site_dir = site_dir or os.getcwd()
        super().__init__(*args, directory=self._site_dir, **kwargs)

    def _send_json(self, status_code, payload):
        body = json.dumps(payload).encode("utf-8")
        self.send_response(status_code)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def end_headers(self):
        self.send_header("Access-Control-Allow-Origin", "*")
        super().end_headers()

    def do_OPTIONS(self):
        if self.path == "/api/run":
            self.send_response(204)
            self.send_header("Access-Control-Allow-Origin", "*")
            self.send_header("Access-Control-Allow-Methods", "POST, OPTIONS")
            self.send_header("Access-Control-Allow-Headers", "Content-Type")
            self.end_headers()
            return
        self.send_response(404)
        self.end_headers()

    def do_POST(self):
        if self.path != "/api/run":
            self._send_json(404, {"ok": False, "error": "Not found"})
            return

        try:
            content_length = int(self.headers.get("Content-Length", "0"))
            raw = self.rfile.read(content_length)
            data = json.loads(raw.decode("utf-8"))
        except Exception:
            self._send_json(400, {"ok": False, "error": "Invalid JSON payload"})
            return

        source = data.get("source", "")
        input_text = data.get("input", "")

        if not isinstance(source, str) or not isinstance(input_text, str):
            self._send_json(400, {"ok": False, "error": "Fields 'source' and 'input' must be strings"})
            return

        try:
            result = run_bespoke(
                source=source,
                input_text=input_text,
                max_steps=500000,
                max_output=100000,
                time_limit_s=5.0,
            )
            self._send_json(200, {"ok": True, **result})
        except BespokeRuntimeError as exc:
            self._send_json(200, {"ok": False, "error": str(exc)})
        except Exception:
            self._send_json(500, {"ok": False, "error": "Internal server error"})


def main():
    parser = argparse.ArgumentParser(description="Serve Poetic site + online interpreter API")
    parser.add_argument("--host", default="127.0.0.1", help="Bind address")
    parser.add_argument("--port", type=int, default=8000, help="Port")
    args = parser.parse_args()

    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    site_dir = os.path.join(base_dir, "site")

    if not os.path.isdir(site_dir):
        raise SystemExit(f"Site directory not found: {site_dir}")

    def handler(*h_args, **h_kwargs):
        return SiteHandler(*h_args, site_dir=site_dir, **h_kwargs)

    server = ThreadingHTTPServer((args.host, args.port), handler)
    print(f"Serving site on http://{args.host}:{args.port}")
    print("Open /tio/index.html to use Try It Online")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()


if __name__ == "__main__":
    main()
