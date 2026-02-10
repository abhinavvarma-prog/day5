from http.server import BaseHTTPRequestHandler
import json


class handler(BaseHTTPRequestHandler):
    def do_POST(self):
        content_length = int(self.headers.get("Content-Length", 0))
        body = self.rfile.read(content_length).decode() if content_length else ""

        # Try parsing as JSON, fall back to raw string
        try:
            data = json.loads(body)
        except (json.JSONDecodeError, ValueError):
            data = body

        print(f"Webhook received - Data: {data}")

        response = {
            "received": True,
            "data": data,
            "method": "POST"
        }

        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.end_headers()
        self.wfile.write(json.dumps(response).encode())
