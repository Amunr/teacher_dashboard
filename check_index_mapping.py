#!/usr/bin/env python3
"""
Verify Index_ID to column mapping is correct
"""
import sqlite3

print("Checking Index_ID to column mapping...")

conn = sqlite3.connect('data.db')
cursor = conn.cursor()

# Check questions table to understand expected Index_IDs
cursor.execute('SELECT Index_ID, Domain, SubDomain FROM questions ORDER BY Index_ID')
questions = cursor.fetchall()

print(f"Questions in database (first 10):")
for q in questions[:10]:
    print(f"  Index_ID {q[0]}: {q[1]} -> {q[2]}")

print(f"\nTotal questions: {len(questions)}")

# Check what Index_IDs are actually in the responses from manual import
cursor.execute('SELECT DISTINCT Index_ID FROM responses WHERE [res-id] >= 513 ORDER BY Index_ID')
response_index_ids = cursor.fetchall()

print(f"\nIndex_IDs in recent manual import responses:")
for idx in response_index_ids:
    print(f"  Index_ID: {idx[0]}")

# Check specific response data to see if it makes sense
cursor.execute('''
    SELECT r.Index_ID, r.Response, q.Domain, q.SubDomain 
    FROM responses r 
    JOIN questions q ON r.Index_ID = q.Index_ID 
    WHERE r.[res-id] = 513 
    ORDER BY r.Index_ID 
    LIMIT 10
''')
sample_responses = cursor.fetchall()

print(f"\nSample responses from res-id 513 with question context:")
for sr in sample_responses:
    print(f"  Index_ID {sr[0]}: Response={sr[1]} | {sr[2]} -> {sr[3]}")

conn.close()
print("Mapping check completed.")
