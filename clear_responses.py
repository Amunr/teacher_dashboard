#!/usr/bin/env python3
"""
Clear all data from the responses table in data.db
"""
import sqlite3

print("Clearing all data from responses table in data.db...")
conn = sqlite3.connect('data.db')
cursor = conn.cursor()
cursor.execute('DELETE FROM responses')
conn.commit()
print("All responses deleted.")

# Optionally reset the auto-increment counter
try:
    cursor.execute('DELETE FROM sqlite_sequence WHERE name="responses"')
    conn.commit()
    print("Auto-increment counter reset.")
except Exception as e:
    print(f"Could not reset auto-increment: {e}")

conn.close()
print("Done.")
