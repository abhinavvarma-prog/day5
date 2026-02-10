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
        content_length = int(self.headers.get("Content-Length", 0))
        body = self.rfile.read(content_length).decode() if content_length else ""
        self._params = parse_qs(body)
        self._handle()

    def _get_param(self, name, default=""):
        if hasattr(self, "_params") and name in self._params:
            return self._params[name][0]
        from urllib.parse import urlparse
        query = parse_qs(urlparse(self.path).query)
        return query.get(name, [default])[0]

    def _handle(self):
        caller_number = self._get_param("From", "unknown")
        digit = self._get_param("Digits", "")
        call_uuid = self._get_param("CallUUID", "")

        # Read session from Redis
        session = None
        try:
            r = get_redis()
            data = r.get(f"ivr_session:{caller_number}")
            if data:
                session = json.loads(data)
        except Exception as e:
            print(f"WARNING: Redis unavailable - {e}")

        response = plivoxml.ResponseElement()

        if digit == "1":
            response.add(plivoxml.SpeakElement("Connecting to sales. Goodbye."))
            self._update_call_status(call_uuid, caller_number, "routed_sales")
            self._update_session(caller_number, session, "routed_sales")

        elif digit == "2":
            response.add(plivoxml.SpeakElement("Connecting to support. Goodbye."))
            self._update_call_status(call_uuid, caller_number, "routed_support")
            self._update_session(caller_number, session, "routed_support")

        elif digit == "3":
            spaced_number = " ".join(list(caller_number))
            response.add(plivoxml.SpeakElement(
                f"Your caller ID is {spaced_number}. Goodbye."
            ))
            self._update_call_status(call_uuid, caller_number, "read_caller_id")
            self._update_session(caller_number, session, "read_caller_id")

        else:
            response.add(plivoxml.SpeakElement("Invalid option. Returning to the main menu."))
            response.add(plivoxml.RedirectElement("/api/answer"))
            self._update_session(caller_number, session, "invalid_input")

        self.send_response(200)
        self.send_header("Content-Type", "application/xml")
        self.end_headers()
        self.wfile.write(response.to_string().encode())

    def _update_session(self, caller_number, session, step):
        if not session:
            return
        try:
            r = get_redis()
            session["step"] = step
            r.setex(f"ivr_session:{caller_number}", SESSION_TTL, json.dumps(session))
        except Exception:
            pass

    def _update_call_status(self, call_uuid, caller_number, status):
        try:
            conn = psycopg2.connect(os.environ["POSTGRES_URL"])
            cur = conn.cursor()
            cur.execute(
                """UPDATE call_logs SET call_status = %s
                   WHERE id = (
                       SELECT id FROM call_logs
                       WHERE caller_number = %s
                       ORDER BY created_at DESC LIMIT 1
                   )""",
                (status, caller_number)
            )
            conn.commit()
            cur.close()
            conn.close()
        except Exception as e:
            print(f"WARNING: Postgres update error - {e}")
