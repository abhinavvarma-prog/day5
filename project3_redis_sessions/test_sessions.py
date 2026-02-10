import requests
import sys
import webbrowser
import time

base_url = sys.argv[1] if len(sys.argv) > 1 else "http://localhost:5002"
caller_id = "caller_101"

# Step 1: Start session
print(f"=== Starting session for {caller_id} ===")
resp = requests.post(f"{base_url}/start-session/{caller_id}")
print(f"Status: {resp.status_code}")
print(f"Response: {resp.json()}\n")

# Step 2: Get session
print(f"=== Getting session for {caller_id} ===")
resp = requests.get(f"{base_url}/get-session/{caller_id}")
print(f"Status: {resp.status_code}")
print(f"Response: {resp.json()}\n")

# Step 3: Update session step
print(f"=== Updating session step to 'collect_input' ===")
resp = requests.put(f"{base_url}/update-session/{caller_id}/collect_input")
print(f"Status: {resp.status_code}")
print(f"Response: {resp.json()}\n")

# Step 4: Get session again to verify update
print(f"=== Getting session again to verify update ===")
resp = requests.get(f"{base_url}/get-session/{caller_id}")
print(f"Status: {resp.status_code}")
print(f"Response: {resp.json()}\n")

# Step 5: Update to another step
print(f"=== Updating session step to 'farewell' ===")
resp = requests.put(f"{base_url}/update-session/{caller_id}/farewell")
print(f"Status: {resp.status_code}")
print(f"Response: {resp.json()}\n")

# Open get-session in browser
url = f"{base_url}/get-session/{caller_id}"
print(f"Opening {url} in browser...")
webbrowser.open(url)

print("\n--- Verify in terminal ---")
print(f"  redis-cli KEYS '*session*'")
print(f"  redis-cli GET session:{caller_id}")
print(f"  redis-cli TTL session:{caller_id}")
