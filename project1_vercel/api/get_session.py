from http.server import BaseHTTPRequestHandler
import json
import os
from urllib.request import Request, urlopen
from urllib.parse import parse_qs, urlparse


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
    def do_GET(self):
        # Get caller_id from query params
        query = parse_qs(urlparse(self.path).query)
        caller_id = query.get("caller_id", [None])[0]

        if not caller_id:
            self.send_response(400)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps({"error": "caller_id query param required"}).encode())
            return

        key = f"session:{caller_id}"

        # GET session data
        result = redis_command(["GET", key])
        session_data = result.get("result")

        if not session_data:
            self.send_response(404)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps({"error": "Session not found or expired"}).encode())
            return

        # GET remaining TTL
        ttl_result = redis_command(["TTL", key])
        ttl = ttl_result.get("result", -1)

        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.end_headers()
        self.wfile.write(json.dumps({
            "caller_id": caller_id,
            "session": json.loads(session_data),
            "ttl_remaining": ttl
        }).encode())
