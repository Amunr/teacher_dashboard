import sqlite3

conn = sqlite3.connect('dev_data.db')
cursor = conn.cursor()

try:
    # Check sheets_config table
    cursor.execute('SELECT COUNT(*) FROM sheets_config')
    count = cursor.fetchone()[0]
    print(f'Total rows in sheets_config table: {count}')

    # Show all config rows
    cursor.execute('SELECT * FROM sheets_config')
    configs = cursor.fetchall()
    print(f'All configurations:')
    for config in configs:
        print(f'  ID: {config[0]}, URL: {config[1][:50] if len(config[1]) > 50 else config[1]}, Active: {config[4]}')

except Exception as e:
    print(f'Error: {e}')

conn.close()
