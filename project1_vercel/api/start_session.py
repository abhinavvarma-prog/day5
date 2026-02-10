from http.server import BaseHTTPRequestHandler
import json
import os
from urllib.request import Request, urlopen
from urllib.parse import parse_qs, urlparse
from datetime import datetime, timezone


def redis_command(command):
    """Send a command to Upstash Redis via REST API."""
    url = os.environ["KV_REST_API_URL"]
    token = os.environ["KV_REST_API_TOKEN"]

    req = Request(url, data=json.dumps(command).encode(), headers={
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    })
    with urlopen(req) as resp:
        return json.loads(resp.read().decode())


class handler(BaseHTTPRequestHandler):
    def do_POST(self):
        # Get caller_id from query params
        query = parse_qs(urlparse(self.path).query)
        caller_id = query.get("caller_id", [None])[0]

        if not caller_id:
            self.send_response(400)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps({"error": "caller_id query param required"}).encode())
            return

        session_data = {
            "step": "greeting",
            "started_at": datetime.now(timezone.utc).isoformat()
        }

        key = f"session:{caller_id}"

        # SET key value EX 1800 (30 min TTL)
        redis_command(["SET", key, json.dumps(session_data), "EX", 1800])

        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.end_headers()
        self.wfile.write(json.dumps({
            "message": "Session started",
            "caller_id": caller_id,
            "session": session_data,
            "ttl": 1800
        }).encode())
