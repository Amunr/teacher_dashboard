#!/usr/bin/env python3
"""
Check recent import data in the database
"""
import sqlite3

print("Checking recent manual import data...")

conn = sqlite3.connect('data.db')
cursor = conn.cursor()

# Check total responses
cursor.execute('SELECT COUNT(*) FROM responses')
total_count = cursor.fetchone()[0]
print(f"Total responses in database: {total_count}")

# Check responses with res-id >= 513
cursor.execute('SELECT COUNT(*) FROM responses WHERE [res-id] >= 513')
recent_count = cursor.fetchone()[0]
print(f"Responses from recent manual import (res-id >= 513): {recent_count}")

if recent_count > 0:
    print("\nRecent manual import data:")
    cursor.execute('SELECT [res-id], Teacher, School, Name FROM responses WHERE [res-id] >= 513 LIMIT 5')
    recent = cursor.fetchall()
    for r in recent:
        print(f"  res-id {r[0]}: Teacher='{r[1]}', School='{r[2]}', Name='{r[3]}'")
    
    # Check the actual response values
    print("\nSample response values:")
    cursor.execute('SELECT [res-id], Index_ID, Response FROM responses WHERE [res-id] >= 513 LIMIT 10')
    response_vals = cursor.fetchall()
    for rv in response_vals:
        print(f"  res-id {rv[0]}, Index_ID {rv[1]}: Response='{rv[2]}'")

conn.close()
print("Check completed.")
