#!/usr/bin/env python3

import sqlite3

def check_logical_column_mapping():
    """Check if we can deduce Grade and Assessment column positions"""
    
    print("=== LOGICAL COLUMN POSITION ANALYSIS ===")
    print("Based on typical form structure, Grade and Assessment are likely:")
    print("  Grade: Usually comes before or after School/Teacher info")
    print("  Assessment: Usually comes before or after Grade")
    
    # Current known mapping:
    known_mapping = {
        1: "Date",
        3: "Teacher Name", 
        4: "School",
        5: "Student Name"
    }
    
    print(f"\nKnown column mapping: {known_mapping}")
    print("Missing mappings for Grade (Index_ID 56) and Assessment (Index_ID 57)")
    
    # Most logical positions would be:
    print(f"\nMost likely positions:")
    print(f"  Column 2: Could be Grade or Assessment (between Date and Teacher)")
    print(f"  Column 6: Could be Grade or Assessment (after Student Name)")
    print(f"  Column 7: Could be Assessment or Grade (after Grade)")
    
    # Let's check what data exists in responses table for these guessed columns
    conn = sqlite3.connect('data.db')
    cursor = conn.cursor()
    
    # Check sample responses to see pattern
    cursor.execute("""
        SELECT [res-id], Index_ID, Response
        FROM responses 
        WHERE [res-id] = (SELECT MAX([res-id]) FROM responses)
        AND Index_ID IN (1, 2, 3, 4, 5, 6, 7, 8, 9, 10)
        ORDER BY Index_ID
    """)
    
    sample_data = cursor.fetchall()
    print(f"\nSample response data (recent res_id) for first 10 Index_IDs:")
    for res_id, index_id, response in sample_data:
        column_name = known_mapping.get(index_id, f"Unknown Column {index_id}")
        print(f"  Index_ID {index_id} ({column_name}): '{response}'")
    
    conn.close()

def propose_fix():
    """Propose the fix for Grade and Assessment mapping"""
    print(f"\n=== PROPOSED FIX ===")
    print("The fix requires updating the create_response() method to:")
    print("1. Find the correct column positions for Grade and Assessment")
    print("2. Update the hardcoded extraction logic")
    
    print(f"\nCurrent extraction logic:")
    print(f"  school = data.get(4, '')")
    print(f"  teacher = data.get(3, '')")
    print(f"  name = data.get(5, '')")
    
    print(f"\nShould be updated to:")
    print(f"  school = data.get(4, '')")
    print(f"  teacher = data.get(3, '')")  
    print(f"  name = data.get(5, '')")
    print(f"  grade = data.get(X, '')      # Where X is the actual Grade column")
    print(f"  assessment = data.get(Y, '') # Where Y is the actual Assessment column")
    
    print(f"\nAnd remove the broken metadata mapping logic:")
    print(f"  # Remove this broken code:")
    print(f"  # for idx, meta_field in meta_index_map.items():")
    print(f"  #     if meta_field == 'Grade' and idx in data:")
    print(f"  #         grade = str(data[idx])")

if __name__ == "__main__":
    check_logical_column_mapping()
    propose_fix()
