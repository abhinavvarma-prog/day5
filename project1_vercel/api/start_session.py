from http.server import BaseHTTPRequestHandler
import json
import os
import redis
from urllib.parse import parse_qs, urlparse
from datetime import datetime, timezone


def get_redis():
    return redis.from_url(os.environ["REDIS_URL"])


class handler(BaseHTTPRequestHandler):
    def do_POST(self):
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
        r = get_redis()
        r.setex(key, 1800, json.dumps(session_data))

        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.end_headers()
        self.wfile.write(json.dumps({
            "message": "Session started",
            "caller_id": caller_id,
            "session": session_data,
            "ttl": 1800
        }).encode())
