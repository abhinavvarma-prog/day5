from http.server import BaseHTTPRequestHandler
import json
import os
import psycopg2


class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        conn = psycopg2.connect(os.environ["POSTGRES_URL"])
        cur = conn.cursor()

        cur.execute("""
            CREATE TABLE IF NOT EXISTS call_logs (
                id SERIAL PRIMARY KEY,
                caller_number VARCHAR(20) NOT NULL,
                called_number VARCHAR(20),
                call_status VARCHAR(50) DEFAULT 'initiated',
                duration_seconds INTEGER DEFAULT 0,
                created_at TIMESTAMP DEFAULT NOW()
            )
        """)
        conn.commit()
        cur.close()
        conn.close()

        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.end_headers()
        self.wfile.write(json.dumps({"message": "Table created successfully"}).encode())
