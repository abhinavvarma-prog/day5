from http.server import BaseHTTPRequestHandler
import json
import os
import redis
from urllib.parse import parse_qs, urlparse


def get_redis():
    return redis.from_url(os.environ["REDIS_URL"])


class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        query = parse_qs(urlparse(self.path).query)
        caller_id = query.get("caller_id", [None])[0]

        if not caller_id:
            self.send_response(400)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps({"error": "caller_id query param required"}).encode())
            return

        key = f"session:{caller_id}"
        r = get_redis()
        session_data = r.get(key)

        if not session_data:
            self.send_response(404)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps({"error": "Session not found or expired"}).encode())
            return

        ttl = r.ttl(key)

        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.end_headers()
        self.wfile.write(json.dumps({
            "caller_id": caller_id,
            "session": json.loads(session_data),
            "ttl_remaining": ttl
        }).encode())
