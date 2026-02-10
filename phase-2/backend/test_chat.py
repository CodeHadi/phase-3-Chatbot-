import json
import urllib.request
import urllib.error

BASE = "http://localhost:8000"

def post(path, data, token=None):
    url = BASE + path
    body = json.dumps(data).encode()
    headers = {"Content-Type": "application/json"}
    if token:
        headers["Authorization"] = f"Bearer {token}"
    req = urllib.request.Request(url, data=body, headers=headers, method="POST")
    with urllib.request.urlopen(req) as resp:
        return json.load(resp)

def get(path, token=None):
    url = BASE + path
    headers = {}
    if token:
        headers["Authorization"] = f"Bearer {token}"
    req = urllib.request.Request(url, headers=headers, method="GET")
    with urllib.request.urlopen(req) as resp:
        return json.load(resp)

if __name__ == '__main__':
    try:
        print('Signing up test user...')
        signup = post('/api/auth/sign-up', {'email': 'agent', 'password': 'password123'})
        token = signup.get('session', {}).get('token')
        print('Token:', token)

        print('Sending chat message...')
        chat = post('/api/agent/chat', {'message': 'Add a task to buy milk'}, token=token)
        print('Chat response:')
        print(json.dumps(chat, indent=2))

        print('Fetching tasks via MCP list...')
        tasks = get('/api/mcp/agent/todo.list', token=token)
        print('Tasks:')
        print(json.dumps(tasks, indent=2))
    except urllib.error.HTTPError as e:
        print('HTTP Error:', e.code, e.read().decode())
    except Exception as e:
        print('Error:', str(e))
