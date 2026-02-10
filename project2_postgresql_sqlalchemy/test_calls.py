import requests
import sys
import webbrowser

base_url = sys.argv[1] if len(sys.argv) > 1 else "http://localhost:5001"

# POST fake call data
fake_calls = [
    {"caller_number": "+1234567890", "called_number": "+0987654321", "call_status": "completed"},
    {"caller_number": "+1112223333", "called_number": "+4445556666", "call_status": "missed"},
    {"caller_number": "+9998887777", "called_number": "+6665554444", "call_status": "busy"},
]

for call in fake_calls:
    print(f"Logging call: {call['caller_number']} -> {call['called_number']} ({call['call_status']})")
    response = requests.post(f"{base_url}/log-call", json=call)
    print(f"  Status: {response.status_code}, Response: {response.json()}\n")

# Open call-logs in browser for visual verification
logs_url = f"{base_url}/call-logs"
print(f"Opening {logs_url} in browser...")
webbrowser.open(logs_url)
