import requests
import sys
import webbrowser

# Use ngrok URL from command line argument, or default to localhost
base_url = sys.argv[1] if len(sys.argv) > 1 else "http://localhost:5000"

# Open health endpoint in browser for visual verification
health_url = f"{base_url}/health"
print(f"Opening {health_url} in browser...")
webbrowser.open(health_url)

# Send POST to webhook-test
url = f"{base_url}/webhook-test"
payload = {"message": "Hello from test script!", "project": "day4", "test": True}

print(f"Sending POST to {url}")
response = requests.post(url, json=payload)
print(f"Status: {response.status_code}")
print(f"Response: {response.json()}")
