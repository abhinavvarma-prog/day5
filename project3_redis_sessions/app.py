from flask import Flask, jsonify
import redis
import json
from datetime import datetime, timezone

app = Flask(__name__)

r = redis.Redis(host="localhost", port=6379, db=0, decode_responses=True)

SESSION_TTL = 1800  # 30 minutes in seconds


@app.route("/health", methods=["GET"])
def health():
    return jsonify({"status": "ok"})


@app.route("/start-session/<caller_id>", methods=["POST"])
def start_session(caller_id):
    key = f"session:{caller_id}"
    session_data = {
        "caller_id": caller_id,
        "step": "greeting",
        "started_at": datetime.now(timezone.utc).isoformat(),
    }
    r.setex(key, SESSION_TTL, json.dumps(session_data))
    ttl = r.ttl(key)
    return jsonify({"success": True, "session": session_data, "ttl": ttl}), 201


@app.route("/get-session/<caller_id>", methods=["GET"])
def get_session(caller_id):
    key = f"session:{caller_id}"
    data = r.get(key)
    if not data:
        return jsonify({"error": "Session not found or expired"}), 404
    ttl = r.ttl(key)
    return jsonify({"session": json.loads(data), "ttl": ttl})


@app.route("/update-session/<caller_id>/<step>", methods=["PUT"])
def update_session(caller_id, step):
    key = f"session:{caller_id}"
    data = r.get(key)
    if not data:
        return jsonify({"error": "Session not found or expired"}), 404
    session_data = json.loads(data)
    session_data["step"] = step
    ttl = r.ttl(key)
    r.setex(key, ttl, json.dumps(session_data))
    return jsonify({"success": True, "session": session_data, "ttl": ttl})


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5002, debug=True)
