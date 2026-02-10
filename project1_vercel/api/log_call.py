from http.server import BaseHTTPRequestHandler
import json
import os
import psycopg2


class handler(BaseHTTPRequestHandler):
    def do_POST(self):
        content_length = int(self.headers.get("Content-Length", 0))
        body = self.rfile.read(content_length).decode() if content_length else "{}"

        try:
            data = json.loads(body)
        except (json.JSONDecodeError, ValueError):
            self.send_response(400)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps({"error": "Invalid JSON body"}).encode())
            return

        caller_number = data.get("caller_number")
        if not caller_number:
            self.send_response(400)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps({"error": "caller_number is required"}).encode())
            return

        called_number = data.get("called_number", "")
        call_status = data.get("call_status", "initiated")
        duration_seconds = data.get("duration_seconds", 0)

        conn = psycopg2.connect(os.environ["POSTGRES_URL"])
        cur = conn.cursor()

        cur.execute(
            """INSERT INTO call_logs (caller_number, called_number, call_status, duration_seconds)
               VALUES (%s, %s, %s, %s) RETURNING id, created_at""",
            (caller_number, called_number, call_status, duration_seconds)
        )
        row = cur.fetchone()
        conn.commit()
        cur.close()
        conn.close()

        self.send_response(201)
        self.send_header("Content-Type", "application/json")
        self.end_headers()
        self.wfile.write(json.dumps({
            "message": "Call logged",
            "id": row[0],
            "created_at": row[1].isoformat()
        }).encode())
