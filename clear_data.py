#!/usr/bin/env python3
"""
Clear responses table and create fresh test data
"""

import os
import sys
import sqlite3

# Add the current directory to Python path
sys.path.insert(0, os.path.dirname(__file__))

def clear_responses():
    """Clear the responses table"""
    db_path = 'dev_data.db'
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Clear responses table
        cursor.execute('DELETE FROM responses')
        conn.commit()
        
        # Check count
        cursor.execute('SELECT COUNT(*) FROM responses')
        count = cursor.fetchone()[0]
        
        print(f"✅ Responses table cleared. Current count: {count}")
        
        conn.close()
        
    except Exception as e:
        print(f"❌ Error clearing responses: {e}")

if __name__ == "__main__":
    clear_responses()
