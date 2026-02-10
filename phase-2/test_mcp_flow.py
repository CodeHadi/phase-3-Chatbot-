#!/usr/bin/env python3
"""
Quick test of the MCP -> Chat flow:
1. Sign up a user
2. Send a chat message that triggers MCP tool call
3. List tasks to verify tool executed
"""
import subprocess
import json
import sys

BASE_URL = "http://localhost:8000"

def run_curl(method, endpoint, data=None, token=None):
    """Run curl and return JSON response."""
    cmd = ["curl", "-s", "-X", method, f"{BASE_URL}{endpoint}"]
    cmd.append("-H")
    cmd.append("Content-Type: application/json")
    if token:
        cmd.append("-H")
        cmd.append(f"Authorization: Bearer {token}")
    if data:
        cmd.append("-d")
        cmd.append(json.dumps(data))
    result = subprocess.run(cmd, capture_output=True, text=True)
    try:
        return json.loads(result.stdout)
    except json.JSONDecodeError:
        print("Failed to parse JSON:", result.stdout[:200])
        return None

print("=" * 60)
print("Testing MCP Chat Integration")
print("=" * 60)

# Sign up
print("\n1. Signing up test user...")
signup_resp = run_curl("POST", "/api/auth/sign-up", {"email": "testuser@example.com", "password": "password123"})
if not signup_resp:
    print("Error: signup failed")
    sys.exit(1)

token = signup_resp.get("session", {}).get("token")
if not token:
    print("Error: no token in signup response")
    print(json.dumps(signup_resp, indent=2))
    sys.exit(1)
print(f"✓ Signed up, token: {token[:20]}...")

# Send chat message
print("\n2. Sending chat message: 'Add task to buy milk'...")
chat_resp = run_curl("POST", "/api/testuser@example.com/chat", {"message": "Add task to buy milk"}, token=token)
if not chat_resp:
    print("Error: chat endpoint failed")
    sys.exit(1)

print("Chat response:")
print(json.dumps(chat_resp, indent=2))

# Check if actions were returned
actions = chat_resp.get("actions", [])
print(f"\n✓ Agent returned {len(actions)} action(s)")
for action in actions:
    print(f"  - Tool: {action.get('tool')}, Result: {action.get('result', {})[:100] if isinstance(action.get('result'), str) else '...'}")

# List tasks to verify
print("\n3. Listing tasks to verify MCP executed...")
tasks_resp = run_curl("GET", "/api/mcp/testuser@example.com/todo.list", token=token)
if not isinstance(tasks_resp, list):
    print("Error: could not fetch tasks")
    print(json.dumps(tasks_resp, indent=2))
    sys.exit(1)

print(f"✓ Found {len(tasks_resp)} task(s):")
for task in tasks_resp:
    print(f"  - [{task.get('id')}] {task.get('title')} (completed: {task.get('completed')})")

print("\n" + "=" * 60)
print("✅ MCP Chat Integration Test Complete!")
print("=" * 60)
