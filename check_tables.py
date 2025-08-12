import sqlite3

conn = sqlite3.connect('data.db')
cursor = conn.cursor()
cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
tables = [row[0] for row in cursor.fetchall()]
print('Tables:', tables)

# Check if layouts and questions tables exist
for table in ['layouts', 'questions', 'responses', 'sheets_config']:
    if table in tables:
        cursor.execute(f"SELECT COUNT(*) FROM {table}")
        count = cursor.fetchone()[0]
        print(f'{table}: {count} records')
    else:
        print(f'{table}: NOT FOUND')

conn.close()
