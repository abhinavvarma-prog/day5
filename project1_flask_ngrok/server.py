from flask import Flask, request, jsonify
import json

app = Flask(__name__)


@app.route("/health", methods=["GET"])
def health():
    return jsonify({"status": "ok"})


@app.route("/webhook-test", methods=["POST"])
def webhook_test():
    data = request.get_json(silent=True) or request.form.to_dict() or request.data.decode()
    print(f"\n--- Webhook Received ---")
    print(f"Headers: {dict(request.headers)}")
    print(f"Data: {json.dumps(data, indent=2) if isinstance(data, dict) else data}")
    print(f"------------------------\n")
    return jsonify({"received": True})


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
