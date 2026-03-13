#!/usr/bin/env python3
import http.server
import json
import os
import subprocess
import urllib.parse

PORT = 8742
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

APPLESCRIPTS = {
    "terminal": """
tell application "Terminal" to activate
delay 0.2
tell application "System Events"
    keystroke "v" using command down
end tell
""",
    "iterm2": """
tell application "iTerm2" to activate
delay 0.2
tell application "System Events"
    keystroke "v" using command down
end tell
""",
    "vscode": """
tell application "Visual Studio Code" to activate
delay 0.3
tell application "System Events"
    keystroke "`" using control down
    delay 0.2
    keystroke "v" using command down
end tell
""",
    "claude": """
tell application "Claude" to activate
delay 0.2
tell application "System Events"
    keystroke "v" using command down
end tell
""",
}


class Handler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=BASE_DIR, **kwargs)

    def do_POST(self):
        if self.path == "/paste":
            length = int(self.headers.get("Content-Length", 0))
            body = self.rfile.read(length)
            try:
                data = json.loads(body)
                app = data.get("app", "")
                script = APPLESCRIPTS.get(app)
                if not script:
                    self._json(400, {"error": f"Unknown app: {app}"})
                    return
                result = subprocess.run(
                    ["osascript", "-e", script],
                    capture_output=True, text=True
                )
                if result.returncode != 0:
                    self._json(500, {"error": result.stderr.strip()})
                else:
                    self._json(200, {"ok": True})
            except Exception as e:
                self._json(500, {"error": str(e)})
        else:
            self._json(404, {"error": "Not found"})

    def _json(self, code, obj):
        payload = json.dumps(obj).encode()
        self.send_response(code)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(payload)))
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()
        self.wfile.write(payload)

    def do_OPTIONS(self):
        self.send_response(204)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "POST, GET, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()

    def log_message(self, format, *args):
        pass  # 로그 억제


if __name__ == "__main__":
    with http.server.ThreadingHTTPServer(("127.0.0.1", PORT), Handler) as httpd:
        print(f"PromptMan 서버 실행 중: http://localhost:{PORT}")
        httpd.serve_forever()
