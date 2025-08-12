import sqlite3

conn = sqlite3.connect('dev_data.db')
cursor = conn.cursor()

# Check if sheets_config table exists and get its contents
try:
    cursor.execute("SELECT * FROM sheets_config")
    config = cursor.fetchone()
    if config:
        print("Current sheets configuration:")
        cursor.execute("PRAGMA table_info(sheets_config)")
        columns = [col[1] for col in cursor.fetchall()]
        for i, value in enumerate(config):
            print(f"  {columns[i]}: {value}")
    else:
        print("No sheets configuration found")
except Exception as e:
    print(f"Error reading sheets_config: {e}")

conn.close()
