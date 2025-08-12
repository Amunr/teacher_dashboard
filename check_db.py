import sqlite3

conn = sqlite3.connect('dev_data.db')
cursor = conn.cursor()

# Get all tables
cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
tables = cursor.fetchall()
print("Available tables:", [t[0] for t in tables])

# Check if we have any data
for table in tables:
    table_name = table[0]
    try:
        cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
        count = cursor.fetchone()[0]
        print(f"Table '{table_name}': {count} rows")
    except Exception as e:
        print(f"Error checking table '{table_name}': {e}")

conn.close()
