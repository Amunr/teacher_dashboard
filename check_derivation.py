#!/usr/bin/env python3

import sqlite3

def check_if_grade_assessment_should_be_derived():
    """Check if Grade and Assessment should be derived rather than extracted from CSV"""
    
    conn = sqlite3.connect('data.db')
    cursor = conn.cursor()
    
    print("=== CHECKING IF GRADE/ASSESSMENT SHOULD BE DERIVED ===")
    
    # Check all Index_IDs that actually have data
    cursor.execute("""
        SELECT DISTINCT Index_ID 
        FROM responses 
        ORDER BY Index_ID
    """)
    
    actual_index_ids = [row[0] for row in cursor.fetchall()]
    print(f"Index_IDs that actually have response data: {actual_index_ids}")
    
    # Check if there are any responses for metadata Index_IDs 56 and 57
    cursor.execute("""
        SELECT COUNT(*) 
        FROM responses 
        WHERE Index_ID IN (56, 57)
    """)
    
    metadata_responses = cursor.fetchone()[0]
    print(f"Number of responses for Index_IDs 56/57 (Grade/Assessment): {metadata_responses}")
    
    # Check the layout structure to understand the intent
    cursor.execute("""
        SELECT Index_ID, Name, Domain, SubDomain
        FROM questions 
        WHERE Index_ID IN (56, 57)
        ORDER BY Index_ID
    """)
    
    metadata_questions = cursor.fetchall()
    print(f"\nMetadata questions for Grade/Assessment:")
    for index_id, name, domain, subdomain in metadata_questions:
        print(f"  Index_ID {index_id}: '{name}' (Domain: {domain})")
    
    # Check if Grade/Assessment should be static values based on the layout/form
    cursor.execute("""
        SELECT DISTINCT layout_id, layout_name
        FROM questions 
        WHERE layout_id IS NOT NULL
        ORDER BY layout_id
    """)
    
    layouts = cursor.fetchall()
    print(f"\nAvailable layouts:")
    for layout_id, layout_name in layouts:
        print(f"  Layout {layout_id}: '{layout_name}'")
    
    conn.close()

def suggest_solution():
    """Suggest the correct solution for Grade and Assessment population"""
    print(f"\n=== SUGGESTED SOLUTION ===")
    print("Based on the analysis, Grade and Assessment appear to be:")
    print("1. Metadata fields that should be populated for ALL responses")
    print("2. NOT extracted from specific CSV columns")
    print("3. Likely derived from the layout/form structure or set as constants")
    
    print(f"\nPossible approaches:")
    print(f"A. Static values: Set Grade and Assessment based on the layout being used")
    print(f"B. Derived values: Extract from the layout name or questions structure")
    print(f"C. Manual entry: These should be entered when uploading the form")
    print(f"D. Column mapping: These ARE in the CSV but in different columns")
    
    print(f"\nRecommended fix:")
    print(f"1. Check the layout_name to derive Grade and Assessment")
    print(f"2. OR set default values for Grade and Assessment")
    print(f"3. OR map to the correct CSV columns if they exist")

if __name__ == "__main__":
    check_if_grade_assessment_should_be_derived()
    suggest_solution()
