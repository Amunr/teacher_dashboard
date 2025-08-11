import sqlite3

# Try both databases
for db_name in ['data.db', 'dev_data.db', 'dev.db']:
    try:
        print(f"\n=== Checking {db_name} ===")
        conn = sqlite3.connect(db_name)
        cursor = conn.cursor()

        # Check tables
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = [row[0] for row in cursor.fetchall()]
        print("Tables:", tables)

        # Check specific table data
        if 'responses' in tables:
            cursor.execute("SELECT MIN(Response), MAX(Response), AVG(Response) FROM responses")
            print("Response range:", cursor.fetchone())
            
            cursor.execute("SELECT Response FROM responses LIMIT 10")
            print("Sample responses:", [row[0] for row in cursor.fetchall()])
        
        if 'layouts' in tables:
            cursor.execute("SELECT COUNT(*) FROM layouts")
            print("Layout count:", cursor.fetchone()[0])
            
        conn.close()
    except Exception as e:
        print(f"Error with {db_name}: {e}")
