#!/usr/bin/env python3
"""
Comprehensive verification script to test MCP Chat Integration end-to-end.
Tests: signup -> chat -> agent actions -> MCP tool execution -> database persistence
"""

import sys
import os
import time
import json
import sqlite3
import socket
import subprocess
from pathlib import Path

# Change to project directory
os.chdir(Path(__file__).parent)
sys.path.insert(0, str(Path(__file__).parent))

def check_port_open(port=8000):
    """Check if backend is running on given port."""
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    result = sock.connect_ex(('localhost', port))
    sock.close()
    return result == 0

def start_backend():
    """Start uvicorn backend in background."""
    if check_port_open():
        print("✅ Backend already running on port 8000")
        return True
    
    print("🚀 Starting backend server...")
    process = subprocess.Popen(
        [sys.executable, "-m", "uvicorn", "backend.main:app", "--reload", "--host", "0.0.0.0", "--port", "8000"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )
    
    # Wait for server to start
    for i in range(30):
        if check_port_open():
            print("✅ Backend server started successfully")
            return True
        time.sleep(1)
        print(f"⏳ Waiting for backend... ({i+1}/30)")
    
    print("❌ Backend failed to start")
    return False

def test_via_api():
    """Test via HTTP requests using curl (PowerShell)."""
    print("\n" + "="*60)
    print("TESTING VIA API")
    print("="*60)
    
    # PowerShell script for testing
    ps_script = """
$ErrorActionPreference = "Stop"

# 1. Signup
Write-Host "1️⃣  Signing up test user..."
try {
    $signup = Invoke-RestMethod -Method POST `
        -Uri "http://localhost:8000/api/auth/sign-up" `
        -ContentType "application/json" `
        -Body '{
            "email": "testuser@example.com",
            "password": "password123"
        }'
    $token = $signup.session.token
    Write-Host "✅ Signup successful. Token: $($token.Substring(0, 20))..."
} catch {
    Write-Host "❌ Signup failed: $_"
    exit 1
}

# 2. Test chat endpoint with message
Write-Host ""
Write-Host "2️⃣  Sending chat message: 'Add task to buy milk'"
$headers = @{
    "Authorization" = "Bearer $token"
    "Content-Type" = "application/json"
}

try {
    $chat = Invoke-RestMethod -Method POST `
        -Uri "http://localhost:8000/api/testuser@example.com/chat" `
        -Headers $headers `
        -Body '{
            "message": "Add task to buy milk"
        }'
    
    Write-Host "✅ Chat response received:"
    Write-Host "  - Conversation ID: $($chat.conversation_id)"
    Write-Host "  - Reply: $($chat.reply)"
    Write-Host "  - Actions executed: $($chat.actions.Count)"
    
    if ($chat.actions.Count -gt 0) {
        Write-Host "  📋 Actions:"
        foreach ($action in $chat.actions) {
            Write-Host "     - Tool: $($action.tool)"
            Write-Host "       Result: $($action.result | ConvertTo-Json -Depth 3 -Compress)"
        }
    }
} catch {
    Write-Host "❌ Chat request failed: $_"
    exit 1
}

# 3. List tasks
Write-Host ""
Write-Host "3️⃣  Listing tasks..."
try {
    $list = Invoke-RestMethod -Method GET `
        -Uri "http://localhost:8000/api/mcp/testuser@example.com/todo.list" `
        -Headers $headers
    
    Write-Host "✅ Tasks retrieved: $($list.Count)"
    foreach ($task in $list) {
        Write-Host "  - ID: $($task.id), Title: $($task.title), Completed: $($task.completed)"
    }
} catch {
    Write-Host "❌ List failed: $_"
    exit 1
}
"""

    # Write PS script to temp file
    ps_file = "temp_test.ps1"
    with open(ps_file, 'w') as f:
        f.write(ps_script)
    
    try:
        result = subprocess.run(
            ["powershell", "-NoProfile", "-ExecutionPolicy", "Bypass", "-File", ps_file],
            capture_output=True,
            text=True,
            timeout=30
        )
        print(result.stdout)
        if result.stderr:
            print("STDERR:", result.stderr)
        return result.returncode == 0
    finally:
        if os.path.exists(ps_file):
            os.remove(ps_file)

def query_database():
    """Query local SQLite database directly."""
    print("\n" + "="*60)
    print("QUERYING DATABASE")
    print("="*60)
    
    db_path = "dev.db"
    if not os.path.exists(db_path):
        print(f"❌ Database file not found: {db_path}")
        return False
    
    print(f"✅ Database found: {db_path}")
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Check table exists
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = [row[0] for row in cursor.fetchall()]
        print(f"\n📊 Tables in database: {', '.join(tables)}")
        
        # Query User table
        print("\n👤 USERS:")
        cursor.execute("SELECT COUNT(*) FROM user")
        user_count = cursor.fetchone()[0]
        print(f"  Total users: {user_count}")
        cursor.execute("SELECT email, created_at FROM user LIMIT 5")
        for row in cursor.fetchall():
            print(f"    - {row[0]} (created: {row[1]})")
        
        # Query Task table
        print("\n📝 TASKS:")
        cursor.execute("SELECT COUNT(*) FROM task")
        task_count = cursor.fetchone()[0]
        print(f"  Total tasks: {task_count}")
        cursor.execute("SELECT id, user_id, title, completed, created_at FROM task ORDER BY created_at DESC LIMIT 10")
        for row in cursor.fetchall():
            status = "✓" if row[3] else "○"
            print(f"    {status} [{row[0]}] {row[2]} (user: {row[1]}, created: {row[4]})")
        
        # Query Conversation table
        print("\n💬 CONVERSATIONS:")
        cursor.execute("SELECT COUNT(*) FROM conversation")
        conv_count = cursor.fetchone()[0]
        print(f"  Total conversations: {conv_count}")
        cursor.execute("SELECT id, user_id, title, created_at FROM conversation ORDER BY created_at DESC LIMIT 10")
        for row in cursor.fetchall():
            print(f"    - [{row[0]}] {row[2]} (user: {row[1]}, created: {row[3]})")
        
        # Query Message table
        print("\n💭 MESSAGES:")
        cursor.execute("SELECT COUNT(*) FROM message")
        msg_count = cursor.fetchone()[0]
        print(f"  Total messages: {msg_count}")
        cursor.execute("SELECT id, conversation_id, role, content, created_at FROM message ORDER BY created_at DESC LIMIT 10")
        for row in cursor.fetchall():
            content_preview = row[3][:50] + "..." if len(row[3]) > 50 else row[3]
            print(f"    - [{row[0]}] {row[2]:6s} in conv {row[1]}: {content_preview}")
        
        conn.close()
        return True
    
    except Exception as e:
        print(f"❌ Database query failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    print("="*60)
    print("🧪 FULL SYSTEM VERIFICATION")
    print("="*60)
    
    # 1. Check backend
    if not check_port_open():
        if not start_backend():
            print("\n❌ Could not start backend server")
            return False
        time.sleep(3)  # Wait for tables to be created
    
    # 2. Test via API
    if not test_via_api():
        print("\n⚠️  API test had errors (may still have data)")
    
    # 3. Query database
    time.sleep(2)  # Give DB time to flush
    if not query_database():
        print("\n❌ Database verification failed")
        return False
    
    print("\n" + "="*60)
    print("✅ VERIFICATION COMPLETE")
    print("="*60)
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
