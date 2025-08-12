#!/usr/bin/env python3
"""
Check metadata questions in database
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
    
    print('=== CHECKING METADATA QUESTIONS ===')
    
    # Check if any questions have Domain = 'MetaData'
    check_timeout()
    cursor.execute("SELECT * FROM questions WHERE Domain = 'MetaData' OR Domain = 'metadata'")
    metadata_questions = cursor.fetchall()
    
    print(f'\nMetadata questions found: {len(metadata_questions)}')
    for row in metadata_questions:
        print(f'  {row}')
    
    # Check all unique domains
    check_timeout()
    cursor.execute("SELECT DISTINCT Domain FROM questions ORDER BY Domain")
    domains = cursor.fetchall()
    
    print(f'\nAll domains in questions table:')
    for domain in domains:
        print(f'  "{domain[0]}"')
    
    # Show sample questions with structure
    check_timeout()
    cursor.execute("SELECT Index_ID, Domain, SubDomain, Name FROM questions ORDER BY Index_ID LIMIT 10")
    sample_questions = cursor.fetchall()
    
    print(f'\nSample questions structure:')
    for row in sample_questions:
        index_id, domain, subdomain, name = row
        print(f'  Index_ID {index_id}: Domain="{domain}", SubDomain="{subdomain}", Name="{name[:50]}..."')
    
    conn.close()
    
    elapsed = check_timeout()
    print(f'\nMetadata check completed in {elapsed:.1f} seconds')
    
except Exception as e:
    elapsed = (datetime.now() - start_time).total_seconds()
    print(f'Error after {elapsed:.1f} seconds: {e}')
    sys.exit(1)
