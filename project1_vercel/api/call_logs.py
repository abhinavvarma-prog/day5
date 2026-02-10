from http.server import BaseHTTPRequestHandler
import json
import os
import psycopg2


class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        conn = psycopg2.connect(os.environ["POSTGRES_URL"])
        cur = conn.cursor()

        cur.execute("""
            SELECT id, caller_number, called_number, call_status, duration_seconds, created_at
            FROM call_logs ORDER BY created_at DESC
        """)
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
        self.wfile.write(json.dumps({"call_logs": logs, "count": len(logs)}).encode())
