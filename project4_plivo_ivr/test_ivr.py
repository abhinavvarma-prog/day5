import requests
import sys
import webbrowser

base_url = sys.argv[1] if len(sys.argv) > 1 else "http://localhost:5003"
test_caller = "+1234567890"
test_uuid = "test-call-uuid-001"

print("=== Test 1: Simulate incoming call (/answer) ===")
resp = requests.post(f"{base_url}/answer", data={
    "From": test_caller,
    "CallUUID": test_uuid,
})
print(f"Status: {resp.status_code}")
print(f"XML:\n{resp.text}\n")

print("=== Test 2: Press 1 — Sales ===")
resp = requests.post(f"{base_url}/handle-input", data={
    "From": test_caller,
    "CallUUID": test_uuid,
    "Digits": "1",
})
print(f"Status: {resp.status_code}")
print(f"XML:\n{resp.text}\n")

# Start a new call for test 3
test_uuid2 = "test-call-uuid-002"
print("=== Test 3: New call, Press 3 — Hear caller ID ===")
requests.post(f"{base_url}/answer", data={
    "From": test_caller,
    "CallUUID": test_uuid2,
})
resp = requests.post(f"{base_url}/handle-input", data={
    "From": test_caller,
    "CallUUID": test_uuid2,
    "Digits": "3",
})
print(f"Status: {resp.status_code}")
print(f"XML:\n{resp.text}\n")

# Start a new call for test 4
test_uuid3 = "test-call-uuid-003"
print("=== Test 4: New call, Press 9 — Invalid input ===")
requests.post(f"{base_url}/answer", data={
    "From": test_caller,
    "CallUUID": test_uuid3,
})
resp = requests.post(f"{base_url}/handle-input", data={
    "From": test_caller,
    "CallUUID": test_uuid3,
    "Digits": "9",
})
print(f"Status: {resp.status_code}")
print(f"XML:\n{resp.text}\n")

print("=== Test 5: Check call history ===")
resp = requests.get(f"{base_url}/call-history/{test_caller}")
print(f"Status: {resp.status_code}")
print(f"Call logs: {resp.json()}\n")

# Open call history in browser
url = f"{base_url}/call-history/{test_caller}"
print(f"Opening {url} in browser...")
webbrowser.open(url)
