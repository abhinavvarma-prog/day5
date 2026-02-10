from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, timezone
import os

app = Flask(__name__)

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://localhost/call_logs_db")
app.config["SQLALCHEMY_DATABASE_URI"] = DATABASE_URL
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app)


class CallLog(db.Model):
    __tablename__ = "call_logs"

    id = db.Column(db.Integer, primary_key=True)
    caller_number = db.Column(db.String(20), nullable=False)
    called_number = db.Column(db.String(20), nullable=False)
    call_status = db.Column(db.String(20), nullable=False)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    def to_dict(self):
        return {
            "id": self.id,
            "caller_number": self.caller_number,
            "called_number": self.called_number,
            "call_status": self.call_status,
            "created_at": self.created_at.isoformat(),
        }


@app.route("/health", methods=["GET"])
def health():
    return jsonify({"status": "ok"})


@app.route("/log-call", methods=["POST"])
def log_call():
    data = request.get_json()
    call = CallLog(
        caller_number=data["caller_number"],
        called_number=data["called_number"],
        call_status=data["call_status"],
    )
    db.session.add(call)
    db.session.commit()
    return jsonify({"success": True, "call": call.to_dict()}), 201


@app.route("/call-logs", methods=["GET"])
def get_call_logs():
    logs = CallLog.query.order_by(CallLog.created_at.desc()).all()
    return jsonify([log.to_dict() for log in logs])


if __name__ == "__main__":
    with app.app_context():
        db.create_all()
        print("Database tables created.")
    app.run(host="0.0.0.0", port=5001, debug=True)
