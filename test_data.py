#!/usr/bin/env python3
"""Test script to check current data in the database."""

import sqlite3

def check_database(db_name):
    print(f'\n=== Checking {db_name} ===')
    try:
        conn = sqlite3.connect(db_name)
        cursor = conn.cursor()

        # Check what tables exist
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = cursor.fetchall()
        print('Available tables:', [t[0] for t in tables])
        
        if not tables:
            print('No tables found in this database')
            conn.close()
            return
        
        # Check Response table if it exists
        table_names = [t[0] for t in tables]
        response_table = None
        for name in table_names:
            if 'response' in name.lower():
                response_table = name
                break
        
        if response_table:
            print(f'\nUsing table: {response_table}')
            
            # Check schema
            cursor.execute(f"PRAGMA table_info({response_table})")
            schema = cursor.fetchall()
            print(f'\n{response_table} table schema:')
            for col in schema:
                print(f'  {col[1]} {col[2]}')

            # Count total rows
            cursor.execute(f'SELECT COUNT(*) FROM {response_table}')
            total_rows = cursor.fetchone()[0]
            print(f'\nTotal rows in {response_table}: {total_rows}')
            
            if total_rows > 0:
                # Check some sample responses
                cursor.execute(f'SELECT * FROM {response_table} LIMIT 5')
                responses = cursor.fetchall()
                print(f'\nSample data from {response_table}:')
                for i, resp in enumerate(responses):
                    print(f'Row {i+1}: {resp}')

                # Count response value distribution if Response column exists
                cursor.execute(f"PRAGMA table_info({response_table})")
                columns = [col[1] for col in cursor.fetchall()]
                if 'Response' in columns:
                    cursor.execute(f'SELECT Response, COUNT(*) as count FROM {response_table} GROUP BY Response')
                    distribution = cursor.fetchall()
                    print(f'\nResponse value distribution:')
                    for value, count in distribution:
                        print(f'  {value}: {count} responses')

        conn.close()
    except Exception as e:
        print(f'Error checking {db_name}: {e}')

def main():
    # Check both databases
    check_database('data.db')
    check_database('dev_data.db')

if __name__ == '__main__':
    main()
