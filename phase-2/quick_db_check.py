#!/usr/bin/env python3
"""Direct database query to verify entries."""
import sqlite3
import os

db_path = "dev.db"
print(f"Checking database: {db_path}")
print(f"Exists: {os.path.exists(db_path)}")

if os.path.exists(db_path):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        # Get table names
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name")
        tables = [row[0] for row in cursor.fetchall()]
        print(f"\nTables: {tables}")
        
        # Count rows in each table
        for table in tables:
            cursor.execute(f"SELECT COUNT(*) FROM {table}")
            count = cursor.fetchone()[0]
            print(f"{table}: {count} rows")
        
        # Show Task details
        print("\n--- TASKS ---")
        cursor.execute("SELECT id, user_id, title, completed FROM task LIMIT 5")
        for row in cursor.fetchall():
            print(f"  ID={row[0]}, user={row[1]}, title={row[2]}, done={row[3]}")
        
        # Show Conversation details
        print("\n--- CONVERSATIONS ---")
        cursor.execute("SELECT id, user_id, title FROM conversation LIMIT 5")
        for row in cursor.fetchall():
            print(f"  ID={row[0]}, user={row[1]}, title={row[2]}")
        
        # Show Message details
        print("\n--- MESSAGES ---")
        cursor.execute("SELECT id, conversation_id, role, content FROM message LIMIT 5")
        for row in cursor.fetchall():
            print(f"  ID={row[0]}, conv={row[1]}, role={row[2]}, content={row[3][:40]}")
    
    finally:
        conn.close()
else:
    print("Database not found!")
