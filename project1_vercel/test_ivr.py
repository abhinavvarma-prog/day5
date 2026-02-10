import requests
import sys

if len(sys.argv) < 2:
    print("Usage: python test_ivr.py <your-vercel-url>")
    print("Example: python test_ivr.py https://project1-vercel-mauve.vercel.app")
    sys.exit(1)

base_url = sys.argv[1].rstrip("/")

print("=" * 60)
print("IVR SIMULATION TEST")
print("=" * 60)

# Test 1: Incoming call - hits /api/answer
print("\n--- Test 1: Incoming call (simulating Plivo hitting /api/answer) ---")
resp = requests.post(f"{base_url}/api/answer", data={
    "From": "+1234567890",
    "CallUUID": "test-uuid-001",
})
print(f"Status: {resp.status_code}")
print(f"Content-Type: {resp.headers.get('Content-Type')}")
print(f"XML Response:\n{resp.text}")

# Test 2: Press 1 for Sales
print("\n--- Test 2: Press 1 - Sales ---")
resp = requests.post(f"{base_url}/api/handle_input", data={
    "From": "+1234567890",
    "Digits": "1",
    "CallUUID": "test-uuid-001",
})
print(f"Status: {resp.status_code}")
print(f"XML Response:\n{resp.text}")

# Test 3: New call, Press 2 for Support
print("\n--- Test 3: New call, Press 2 - Support ---")
requests.post(f"{base_url}/api/answer", data={
    "From": "+1234567890",
    "CallUUID": "test-uuid-002",
})
resp = requests.post(f"{base_url}/api/handle_input", data={
    "From": "+1234567890",
    "Digits": "2",
    "CallUUID": "test-uuid-002",
})
print(f"Status: {resp.status_code}")
print(f"XML Response:\n{resp.text}")

# Test 4: New call, Press 3 for Caller ID readback
print("\n--- Test 4: New call, Press 3 - Caller ID ---")
requests.post(f"{base_url}/api/answer", data={
    "From": "+5555555555",
    "CallUUID": "test-uuid-003",
})
resp = requests.post(f"{base_url}/api/handle_input", data={
    "From": "+5555555555",
    "Digits": "3",
    "CallUUID": "test-uuid-003",
})
print(f"Status: {resp.status_code}")
print(f"XML Response:\n{resp.text}")

# Test 5: New call, Press 9 - Invalid input
print("\n--- Test 5: New call, Press 9 - Invalid ---")
requests.post(f"{base_url}/api/answer", data={
    "From": "+1234567890",
    "CallUUID": "test-uuid-004",
})
resp = requests.post(f"{base_url}/api/handle_input", data={
    "From": "+1234567890",
    "Digits": "9",
    "CallUUID": "test-uuid-004",
})
print(f"Status: {resp.status_code}")
print(f"XML Response:\n{resp.text}")

# Test 6: Check call history
print("\n--- Test 6: Call history for +1234567890 ---")
resp = requests.get(f"{base_url}/api/call_history/%2B1234567890")
print(f"Status: {resp.status_code}")
print(f"Response: {resp.json()}")

# Test 7: Check call history for other number
print("\n--- Test 7: Call history for +5555555555 ---")
resp = requests.get(f"{base_url}/api/call_history/%2B5555555555")
print(f"Status: {resp.status_code}")
print(f"Response: {resp.json()}")

print("\n" + "=" * 60)
print("ALL TESTS COMPLETE")
print("=" * 60)
