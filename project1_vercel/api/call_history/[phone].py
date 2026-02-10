from http.server import BaseHTTPRequestHandler
import json
import os
import psycopg2
from urllib.parse import urlparse, unquote


class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        # Extract phone number from URL path: /api/call_history/+1234567890
        path = urlparse(self.path).path
        phone = unquote(path.split("/api/call_history/")[-1])

        if not phone:
            self.send_response(400)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps({"error": "Phone number required in URL"}).encode())
            return

        conn = psycopg2.connect(os.environ["POSTGRES_URL"])
        cur = conn.cursor()

        cur.execute(
            """SELECT id, caller_number, called_number, call_status, duration_seconds, created_at
               FROM call_logs WHERE caller_number = %s ORDER BY created_at DESC""",
            (phone,)
        )
        rows = cur.fetchall()
        cur.close()
        conn.close()

        logs = [
            {
                "id": row[0],
                "caller_number": row[1],
                "called_number": row[2],
                "call_status": row[3],
                "duration_seconds": row[4],
                "created_at": row[5].isoformat()
            }
            for row in rows
        ]

        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.end_headers()
        self.wfile.write(json.dumps({"phone": phone, "call_logs": logs, "count": len(logs)}).encode())
