import sqlite3
import os

# Check if dev.db exists
db_path = 'dev.db'
if not os.path.exists(db_path):
    print(f"ERROR: Database file '{db_path}' not found!")
    exit(1)

conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# Get all tables
cursor.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name;")
tables = cursor.fetchall()

print("\n" + "="*80)
print("DATABASE STATE REPORT - dev.db")
print("="*80)

if not tables:
    print("No tables found in database!")
    conn.close()
    exit(0)

target_tables = ['user', 'task', 'conversation', 'message']
found_tables = {table[0] for table in tables}

print(f"\nTotal tables in database: {len(tables)}")
print(f"Target tables to check: {target_tables}")
print(f"Found: {list(found_tables)}")

# Check each target table
for table_name in target_tables:
    print(f"\n{'-'*80}")
    print(f"TABLE: {table_name.upper()}")
    print(f"{'-'*80}")
    
    if table_name not in found_tables:
        print(f"❌ Table '{table_name}' does NOT exist")
        continue
    
    # Count rows
    cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
    count = cursor.fetchone()[0]
    print(f"✅ Table exists | Total rows: {count}")
    
    if count == 0:
        print("   (No data)")
        continue
    
    # Get column names
    cursor.execute(f"PRAGMA table_info({table_name})")
    columns = [col[1] for col in cursor.fetchall()]
    print(f"   Columns: {', '.join(columns)}")
    
    # Get first 5 rows
    cursor.execute(f"SELECT * FROM {table_name} LIMIT 5")
    rows = cursor.fetchall()
    
    print(f"\n   First {min(5, len(rows))} rows:")
    for i, row in enumerate(rows, 1):
        print(f"   {i}. {row}")

print(f"\n" + "="*80)
print("END OF REPORT")
print("="*80 + "\n")

conn.close()
