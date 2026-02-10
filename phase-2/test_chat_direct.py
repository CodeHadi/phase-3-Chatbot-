#!/usr/bin/env python3
"""
Debug script to test chat endpoint WITHOUT frontend CORS issues.
Tests the endpoint directly from backend perspective.
"""
import requests
import json
import time

BASE_URL = "http://localhost:8000"
TEST_EMAIL = "chattest@example.com"
TEST_PASSWORD = "testpass123"

print("=" * 70)
print("🧪 TESTING CHAT ENDPOINT (Direct Backend Test)")
print("=" * 70)

# Step 1: Signup
print("\n1️⃣  SIGNUP")
print("-" * 70)
try:
    signup_response = requests.post(
        f"{BASE_URL}/api/auth/sign-up",
        json={"email": TEST_EMAIL, "password": TEST_PASSWORD},
        headers={"Content-Type": "application/json"}
    )
    print(f"Status: {signup_response.status_code}")
    signup_data = signup_response.json()
    print(f"Response: {json.dumps(signup_data, indent=2)}")
    
    if signup_response.status_code != 200:
        print("❌ Signup failed!")
        exit(1)
    
    token = signup_data.get("session", {}).get("token")
    if not token:
        print("❌ No token in response!")
        exit(1)
    
    print(f"✅ Token received: {token[:30]}...")
except Exception as e:
    print(f"❌ Error: {e}")
    exit(1)

# Step 2: Test Chat Endpoint
print("\n2️⃣  CHAT ENDPOINT TEST")
print("-" * 70)
try:
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    chat_payload = {"message": "Add a task to buy milk"}
    print(f"Request to: POST {BASE_URL}/api/{TEST_EMAIL}/chat")
    print(f"Headers: {json.dumps(dict(headers), indent=2)}")
    print(f"Body: {json.dumps(chat_payload, indent=2)}")
    
    chat_response = requests.post(
        f"{BASE_URL}/api/{TEST_EMAIL}/chat",
        json=chat_payload,
        headers=headers
    )
    
    print(f"\nStatus: {chat_response.status_code}")
    
    if chat_response.status_code != 200:
        print(f"Response Text: {chat_response.text}")
        print("❌ Chat request failed!")
        exit(1)
    
    chat_data = chat_response.json()
    print(f"Response: {json.dumps(chat_data, indent=2)}")
    
    # Check for conversation_id
    conversation_id = chat_data.get("conversation_id")
    if conversation_id:
        print(f"✅ conversation_id received: {conversation_id}")
    else:
        print("❌ No conversation_id in response!")
    
    # Check for reply
    reply = chat_data.get("reply")
    if reply:
        print(f"✅ reply received: {reply}")
    else:
        print("⚠️  No reply in response")
    
    # Check for actions
    actions = chat_data.get("actions", [])
    print(f"✅ actions count: {len(actions)}")
    for i, action in enumerate(actions):
        print(f"   Action {i+1}: {action.get('tool')}")
        if "result" in action:
            print(f"   Result: {json.dumps(action['result'], indent=6)}")
        if "error" in action:
            print(f"   Error: {action['error']}")

except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()
    exit(1)

# Step 3: Test MCP List Endpoint
print("\n3️⃣  MCP LIST ENDPOINT TEST")
print("-" * 70)
try:
    list_url = f"{BASE_URL}/api/mcp/{TEST_EMAIL}/todo.list"
    print(f"Request: GET {list_url}")
    
    list_response = requests.get(list_url, headers=headers)
    print(f"Status: {list_response.status_code}")
    
    if list_response.status_code == 200:
        tasks = list_response.json()
        print(f"✅ Tasks retrieved: {len(tasks)} tasks")
        for task in tasks:
            print(f"   - [{task.get('id')}] {task.get('title')} (completed: {task.get('completed')})")
    else:
        print(f"❌ Failed: {list_response.status_code}")
        print(f"Response: {list_response.text}")

except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "=" * 70)
print("✅ TEST COMPLETE")
print("=" * 70)
