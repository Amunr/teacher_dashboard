#!/usr/bin/env python3
"""Quick script to reset import data for testing"""

import sqlite3
import sys

def reset_import_data():
    """Reset failed imports and last processed row"""
    try:
        conn = sqlite3.connect('data.db')
        cursor = conn.cursor()
        
        # Clear failed imports
        cursor.execute('DELETE FROM failed_imports')
        print('✅ Cleared failed imports table')
        
        # Reset last processed row to 0 so it starts from the beginning
        cursor.execute('UPDATE sheets_config SET last_row_processed = 0 WHERE id = 2')
        print('✅ Reset last_row_processed to 0')
        
        # Check current stats
        cursor.execute('SELECT COUNT(*) FROM responses')
        responses_count = cursor.fetchone()[0]
        cursor.execute('SELECT COUNT(*) FROM failed_imports')
        failed_count = cursor.fetchone()[0]
        
        print(f'📊 Current responses: {responses_count}')
        print(f'📊 Current failed imports: {failed_count}')
        
        conn.commit()
        conn.close()
        print('🎉 Database reset complete!')
        return True
        
    except Exception as e:
        print(f'❌ Error resetting data: {e}')
        return False

if __name__ == "__main__":
    reset_import_data()
