import requests
import sys

# Pass your Vercel URL as argument: python test_webhook.py https://your-project.vercel.app
if len(sys.argv) < 2:
    print("Usage: python test_webhook.py <your-vercel-url>")
    print("Example: python test_webhook.py https://my-project.vercel.app")
    sys.exit(1)

base_url = sys.argv[1].rstrip("/")

# Test 1: Health endpoint
print("=== Test 1: GET /api/health ===")
resp = requests.get(f"{base_url}/api/health")
print(f"Status: {resp.status_code}")
print(f"Response: {resp.json()}")
print()

# Test 2: Webhook POST with JSON
print("=== Test 2: POST /api/webhook_test ===")
payload = {"message": "Hello from test script!", "project": "day5-vercel", "test": True}
resp = requests.post(f"{base_url}/api/webhook_test", json=payload)
print(f"Status: {resp.status_code}")
print(f"Response: {resp.json()}")
print()

# Test 3: Webhook POST with different data
print("=== Test 3: POST /api/webhook_test (different payload) ===")
payload2 = {"caller": "+1234567890", "event": "call_started", "timestamp": "2025-01-01T00:00:00Z"}
resp = requests.post(f"{base_url}/api/webhook_test", json=payload2)
print(f"Status: {resp.status_code}")
print(f"Response: {resp.json()}")
