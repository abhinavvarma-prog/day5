from flask import Flask, request, Response, jsonify
from flask_sqlalchemy import SQLAlchemy
from plivo import plivoxml
import redis
import json
import os
from datetime import datetime, timezone

app = Flask(__name__)

# Database config
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://localhost/plivo_ivr_db")
app.config["SQLALCHEMY_DATABASE_URI"] = DATABASE_URL
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db = SQLAlchemy(app)

# Redis config
REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/1")
r = redis.from_url(REDIS_URL, decode_responses=True)

SESSION_TTL = 1800  # 30 minutes


# --- Models ---

class CallLog(db.Model):
    __tablename__ = "call_logs"

    id = db.Column(db.Integer, primary_key=True)
    caller_number = db.Column(db.String(20), nullable=False)
    plivo_call_uuid = db.Column(db.String(100))
    call_status = db.Column(db.String(50), default="in_progress")
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc),
                           onupdate=lambda: datetime.now(timezone.utc))

    def to_dict(self):
        return {
            "id": self.id,
            "caller_number": self.caller_number,
            "plivo_call_uuid": self.plivo_call_uuid,
            "call_status": self.call_status,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
        }


# --- Helper functions ---

def get_redis_session(caller_number):
    key = f"ivr_session:{caller_number}"
    data = r.get(key)
    return json.loads(data) if data else None


def set_redis_session(caller_number, session_data):
    key = f"ivr_session:{caller_number}"
    r.setex(key, SESSION_TTL, json.dumps(session_data))


def xml_response(xml):
    return Response(xml.to_string(), content_type="application/xml")


# --- Routes ---

@app.route("/health", methods=["GET"])
def health():
    return jsonify({"status": "ok"})


@app.route("/answer", methods=["GET", "POST"])
def answer():
    caller_number = request.values.get("From", "unknown")
    call_uuid = request.values.get("CallUUID", "")

    # Store session in Redis
    session_data = {
        "caller_number": caller_number,
        "step": "main_menu",
        "call_uuid": call_uuid,
        "started_at": datetime.now(timezone.utc).isoformat(),
    }
    try:
        set_redis_session(caller_number, session_data)
    except redis.ConnectionError:
        print("WARNING: Redis unavailable, continuing without session")

    # Log call start in PostgreSQL
    call_log = CallLog(
        caller_number=caller_number,
        plivo_call_uuid=call_uuid,
        call_status="in_progress",
    )
    db.session.add(call_log)
    db.session.commit()

    # Return IVR greeting XML
    response = plivoxml.ResponseElement()
    get_input = response.add(plivoxml.GetInputElement(
        action="/handle-input",
        method="POST",
        input_type="dtmf",
        digit_end_timeout=5,
    ))
    get_input.add(plivoxml.SpeakElement(
        "Welcome to Acme Corp. Press 1 for Sales, Press 2 for Support, Press 3 to hear your caller ID."
    ))

    return xml_response(response)


@app.route("/handle-input", methods=["GET", "POST"])
def handle_input():
    caller_number = request.values.get("From", "unknown")
    digit = request.values.get("Digits", "")
    call_uuid = request.values.get("CallUUID", "")

    # Read session from Redis
    session = None
    try:
        session = get_redis_session(caller_number)
    except redis.ConnectionError:
        print("WARNING: Redis unavailable")

    response = plivoxml.ResponseElement()

    if digit == "1":
        # Sales
        response.add(plivoxml.SpeakElement("Connecting to sales. Goodbye."))
        _update_call_status(call_uuid, caller_number, "routed_sales")
        if session:
            session["step"] = "routed_sales"
            set_redis_session(caller_number, session)

    elif digit == "2":
        # Support
        response.add(plivoxml.SpeakElement("Connecting to support. Goodbye."))
        _update_call_status(call_uuid, caller_number, "routed_support")
        if session:
            session["step"] = "routed_support"
            set_redis_session(caller_number, session)

    elif digit == "3":
        # Read back caller ID
        spaced_number = " ".join(list(caller_number))
        response.add(plivoxml.SpeakElement(
            f"Your caller ID is {spaced_number}. Goodbye."
        ))
        _update_call_status(call_uuid, caller_number, "read_caller_id")
        if session:
            session["step"] = "read_caller_id"
            set_redis_session(caller_number, session)

    else:
        # Invalid input — redirect back to menu
        response.add(plivoxml.SpeakElement("Invalid option. Returning to the main menu."))
        response.add(plivoxml.RedirectElement("/answer"))
        if session:
            session["step"] = "invalid_input"
            set_redis_session(caller_number, session)

    return xml_response(response)


@app.route("/call-history/<phone_number>", methods=["GET"])
def call_history(phone_number):
    logs = CallLog.query.filter_by(caller_number=phone_number)\
        .order_by(CallLog.created_at.desc()).all()
    return jsonify([log.to_dict() for log in logs])


def _update_call_status(call_uuid, caller_number, status):
    call_log = CallLog.query.filter_by(plivo_call_uuid=call_uuid).first()
    if not call_log:
        call_log = CallLog.query.filter_by(caller_number=caller_number)\
            .order_by(CallLog.created_at.desc()).first()
    if call_log:
        call_log.call_status = status
        call_log.updated_at = datetime.now(timezone.utc)
        db.session.commit()


if __name__ == "__main__":
    with app.app_context():
        db.create_all()
        print("Database tables created.")
    app.run(host="0.0.0.0", port=5003, debug=True)
