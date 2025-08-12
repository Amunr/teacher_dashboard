#!/usr/bin/env python3

import sqlite3

def check_grade_assessment_mapping():
    """Check Index_ID to column mapping for Grade and Assessment"""
    conn = sqlite3.connect('data.db')
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT Index_ID, Name, SubDomain, Domain
        FROM questions 
        WHERE SubDomain IN ('Grade', 'Assessment')
        ORDER BY Index_ID
    """)
    
    results = cursor.fetchall()
    print("Grade/Assessment mapping:")
    for index_id, name, subdomain, domain in results:
        print(f"  Index_ID {index_id}: Name='{name}', SubDomain='{subdomain}', Domain='{domain}'")
    
    # Also check what columns contain data
    cursor.execute("""
        SELECT DISTINCT Index_ID, Name, SubDomain
        FROM questions 
        WHERE Domain = 'MetaData'
        ORDER BY Index_ID
    """)
    
    metadata_results = cursor.fetchall()
    print("\nAll MetaData fields:")
    for index_id, name, subdomain in metadata_results:
        print(f"  Index_ID {index_id}: Name='{name}', SubDomain='{subdomain}'")
    
    conn.close()

if __name__ == "__main__":
    check_grade_assessment_mapping()
