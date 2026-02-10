from http.server import BaseHTTPRequestHandler
import json
import os
import redis
from urllib.parse import parse_qs, urlparse


def get_redis():
    return redis.from_url(os.environ["REDIS_URL"])


class handler(BaseHTTPRequestHandler):
    def do_POST(self):
        query = parse_qs(urlparse(self.path).query)
        caller_id = query.get("caller_id", [None])[0]
        step = query.get("step", [None])[0]

        if not caller_id or not step:
            self.send_response(400)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps({"error": "caller_id and step query params required"}).encode())
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

        session = json.loads(session_data)
        session["step"] = step

        ttl = r.ttl(key)
        if ttl < 0:
            ttl = 1800

        r.setex(key, ttl, json.dumps(session))

        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.end_headers()
        self.wfile.write(json.dumps({
            "message": "Session updated",
            "caller_id": caller_id,
            "session": session,
            "ttl_remaining": ttl
        }).encode())
