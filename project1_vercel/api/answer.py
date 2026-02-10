from http.server import BaseHTTPRequestHandler
import json
import os
import redis
import psycopg2
from urllib.parse import parse_qs
from datetime import datetime, timezone
from plivo import plivoxml

SESSION_TTL = 1800


def get_redis():
    return redis.from_url(os.environ["REDIS_URL"])


class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        self._handle()

    def do_POST(self):
        # Read POST body for form data
        content_length = int(self.headers.get("Content-Length", 0))
        body = self.rfile.read(content_length).decode() if content_length else ""
        self._params = parse_qs(body)
        self._handle()

    def _get_param(self, name, default=""):
        # Check POST body params first, then query string
        if hasattr(self, "_params") and name in self._params:
            return self._params[name][0]
        from urllib.parse import urlparse
        query = parse_qs(urlparse(self.path).query)
        return query.get(name, [default])[0]

    def _handle(self):
        caller_number = self._get_param("From", "unknown")
        call_uuid = self._get_param("CallUUID", "")

        # Store session in Redis
        try:
            r = get_redis()
            session_data = {
                "caller_number": caller_number,
                "step": "main_menu",
                "call_uuid": call_uuid,
                "started_at": datetime.now(timezone.utc).isoformat(),
            }
            r.setex(f"ivr_session:{caller_number}", SESSION_TTL, json.dumps(session_data))
        except Exception as e:
            print(f"WARNING: Redis unavailable - {e}")

        # Log call in Postgres
        try:
            conn = psycopg2.connect(os.environ["POSTGRES_URL"])
            cur = conn.cursor()
            cur.execute(
                """INSERT INTO call_logs (caller_number, call_status)
                   VALUES (%s, %s)""",
                (caller_number, "in_progress")
            )
            conn.commit()
            cur.close()
            conn.close()
        except Exception as e:
            print(f"WARNING: Postgres error - {e}")

        # Build Plivo XML response
        response = plivoxml.ResponseElement()
        get_input = response.add(plivoxml.GetInputElement(
            action="/api/handle_input",
            method="POST",
            input_type="dtmf",
            digit_end_timeout=5,
        ))
        get_input.add(plivoxml.SpeakElement(
            "Welcome to Acme Corp. Press 1 for Sales, Press 2 for Support, Press 3 to hear your caller ID."
        ))

        self.send_response(200)
        self.send_header("Content-Type", "application/xml")
        self.end_headers()
        self.wfile.write(response.to_string().encode())
