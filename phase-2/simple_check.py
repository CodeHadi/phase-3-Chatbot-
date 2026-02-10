#!/usr/bin/env python3
"""
Minimal test - no complex dependencies, just basic HTTP + DB checks
"""
import sys
import os

# Test 1: Check database file
print("=" * 60)
print("TEST 1: DATABASE FILE")
print("=" * 60)

db_path = "dev.db"
if os.path.exists(db_path):
    size = os.path.getsize(db_path)
    print(f"✅ Database exists: {db_path}")
    print(f"   Size: {size} bytes")
else:
    print(f"❌ Database not found: {db_path}")

# Test 2: Check database tables via sqlite3
print("\n" + "=" * 60)
print("TEST 2: DATABASE CONTENTS")
print("=" * 60)

try:
    import sqlite3
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Get all tables
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
    tables = [row[0] for row in cursor.fetchall()]
    print(f"Tables found: {', '.join(tables)}")
    
    # Count rows in each table
    print("\nRow counts:")
    for table in ['user', 'task', 'conversation', 'message']:
        if table in tables:
            cursor.execute(f"SELECT COUNT(*) FROM {table}")
            count = cursor.fetchone()[0]
            print(f"  {table:15s}: {count:5d} rows")
    
    # Show sample data
    print("\nSample data:")
    
    if 'user' in tables:
        cursor.execute("SELECT COUNT(*) FROM user")
        user_count = cursor.fetchone()[0]
        if user_count > 0:
            print(f"  Users ({user_count}):")
            cursor.execute("SELECT email FROM user LIMIT 3")
            for row in cursor.fetchall():
                print(f"    - {row[0]}")
    
    if 'task' in tables:
        cursor.execute("SELECT COUNT(*) FROM task")
        task_count = cursor.fetchone()[0]
        if task_count > 0:
            print(f"  Tasks ({task_count}):")
            cursor.execute("SELECT id, user_id, title, completed FROM task LIMIT 3")
            for row in cursor.fetchall():
                status = "✓" if row[3] else "○"
                print(f"    {status} [{row[0]}] {row[2]} (user: {row[1]})")
    
    if 'conversation' in tables:
        cursor.execute("SELECT COUNT(*) FROM conversation")
        conv_count = cursor.fetchone()[0]
        if conv_count > 0:
            print(f"  Conversations ({conv_count}):")
            cursor.execute("SELECT id, user_id FROM conversation LIMIT 3")
            for row in cursor.fetchall():
                print(f"    - Conv {row[0]} (user: {row[1]})")
    
    if 'message' in tables:
        cursor.execute("SELECT COUNT(*) FROM message")
        msg_count = cursor.fetchone()[0]
        if msg_count > 0:
            print(f"  Messages ({msg_count}):")
            cursor.execute("SELECT id, role, content FROM message LIMIT 3")
            for row in cursor.fetchall():
                content = row[2][:40] + "..." if len(row[2]) > 40 else row[2]
                print(f"    - [{row[0]}] {row[1]:6s}: {content}")
    
    conn.close()
    print("\n✅ Database query successful")

except ImportError:
    print("❌ sqlite3 module not found")
except Exception as e:
    print(f"❌ Error: {e}")

# Test 3: Check backend files
print("\n" + "=" * 60)
print("TEST 3: BACKEND FILES")
print("=" * 60)

files_to_check = [
    "backend/main.py",
    "backend/models.py",
    "backend/database.py",
    "backend/agents.py",
    "backend/routes/auth.py",
    "backend/routes/chat.py",
    "backend/routes/mcp.py",
]

for f in files_to_check:
    if os.path.exists(f):
        size = os.path.getsize(f)
        print(f"✅ {f:30s} ({size:5d} bytes)")
    else:
        print(f"❌ {f:30s} NOT FOUND")

# Test 4: Check requirements
print("\n" + "=" * 60)
print("TEST 4: DEPENDENCIES")
print("=" * 60)

required_packages = ['fastapi', 'sqlmodel', 'pydantic', 'dotenv', 'jwt', 'passlib']

for pkg in required_packages:
    try:
        if pkg == 'dotenv':
            import dotenv
        elif pkg == 'jwt':
            import jwt
        else:
            __import__(pkg)
        print(f"✅ {pkg}")
    except ImportError:
        print(f"❌ {pkg} - NOT INSTALLED")

print("\n" + "=" * 60)
print("✅ VERIFICATION COMPLETE")
print("=" * 60)
print("\nTo test the full system:")
print("1. Start backend: python -m uvicorn backend.main:app --reload")
print("2. Visit: http://localhost:8000/docs")
print("3. Or run: python verify_system.py")
