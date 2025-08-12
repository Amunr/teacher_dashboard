#!/usr/bin/env python3
"""
Check data quality in database
"""
import sqlite3
import sys
from datetime import datetime

timeout_seconds = 30
start_time = datetime.now()

def check_timeout():
    elapsed = (datetime.now() - start_time).total_seconds()
    if elapsed > timeout_seconds:
        print(f'Timeout after {elapsed:.1f} seconds')
        sys.exit(1)
    return elapsed

try:
    check_timeout()
    conn = sqlite3.connect('data.db', timeout=10)
    cursor = conn.cursor()
    
    print('=== CHECKING DATA QUALITY IN data.db ===')
    
    # Check responses with metadata
    check_timeout()
    cursor.execute('''SELECT [res-id], School, Grade, Teacher, Assessment, Name, Date, COUNT(*) as response_count 
                     FROM responses 
                     GROUP BY [res-id] 
                     ORDER BY [res-id] DESC LIMIT 5''')
    responses = cursor.fetchall()
    
    print('\nResponse records by res-id:')
    for row in responses:
        res_id, school, grade, teacher, assessment, name, date_val, count = row
        print(f'  Res-ID {res_id}: School="{school}", Grade="{grade}", Teacher="{teacher}", Assessment="{assessment}", Name="{name}", Date="{date_val}", Responses={count}')
    
    # Check actual response values (scores)
    check_timeout()
    cursor.execute('''SELECT [res-id], Index_ID, Response 
                     FROM responses 
                     WHERE [res-id] = (SELECT MAX([res-id]) FROM responses) 
                     ORDER BY Index_ID LIMIT 10''')
    latest_responses = cursor.fetchall()
    
    print(f'\nSample response values from latest res-id:')
    for row in latest_responses:
        res_id, index_id, response_val = row
        print(f'  Res-ID {res_id}, Index_ID {index_id}: Response="{response_val}"')
    
    # Check questions to see what we should be matching against
    check_timeout()
    cursor.execute('''SELECT Index_ID, Domain, Subdomain 
                     FROM questions 
                     WHERE Index_ID IN (17, 18, 19, 20, 21) 
                     ORDER BY Index_ID''')
    sample_questions = cursor.fetchall()
    
    print(f'\nSample questions structure:')
    for row in sample_questions:
        index_id, domain, subdomain = row
        print(f'  Index_ID {index_id}: {domain} -> {subdomain}')
    
    # Check for any non-empty metadata
    check_timeout()
    cursor.execute('''SELECT [res-id], School, Grade, Teacher, Assessment, Name 
                     FROM responses 
                     WHERE School != '' OR Grade != '' OR Teacher != '' OR Assessment != '' OR Name != ''
                     GROUP BY [res-id] 
                     LIMIT 5''')
    non_empty_metadata = cursor.fetchall()
    
    print(f'\nRecords with non-empty metadata:')
    if non_empty_metadata:
        for row in non_empty_metadata:
            res_id, school, grade, teacher, assessment, name = row
            print(f'  Res-ID {res_id}: School="{school}", Grade="{grade}", Teacher="{teacher}", Assessment="{assessment}", Name="{name}"')
    else:
        print('  ⚠️  No records found with non-empty metadata')
    
    conn.close()
    
    elapsed = check_timeout()
    print(f'\nData quality check completed in {elapsed:.1f} seconds')
    
except Exception as e:
    elapsed = (datetime.now() - start_time).total_seconds()
    print(f'Error after {elapsed:.1f} seconds: {e}')
    sys.exit(1)
