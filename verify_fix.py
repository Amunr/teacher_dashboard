#!/usr/bin/env python3

import sqlite3

def verify_existing_responses():
    """Check if existing responses still work and show Grade/Assessment status"""
    
    conn = sqlite3.connect('data.db')
    cursor = conn.cursor()
    
    print("=== VERIFICATION OF EXISTING RESPONSES ===")
    
    # Check recent responses
    cursor.execute("""
        SELECT [res-id], School, Grade, Teacher, Assessment, Name, Date
        FROM responses 
        WHERE [res-id] >= 185
        GROUP BY [res-id]
        ORDER BY [res-id] DESC
        LIMIT 5
    """)
    
    recent_responses = cursor.fetchall()
    print("Recent responses:")
    for res_id, school, grade, teacher, assessment, name, date in recent_responses:
        print(f"  res_id {res_id}: School='{school}', Grade='{grade}', Teacher='{teacher}', Assessment='{assessment}', Name='{name}', Date='{date}'")
    
    # Check if new responses have Grade/Assessment populated
    cursor.execute("""
        SELECT COUNT(*) 
        FROM responses 
        WHERE [res-id] = 187 AND (Grade != '' OR Assessment != '')
    """)
    
    populated_count = cursor.fetchone()[0]
    print(f"\nNew response (res_id 187) with populated Grade/Assessment: {populated_count} records")
    
    # Show the fix status
    if populated_count > 0:
        print("✅ SUCCESS: The Grade and Assessment fix is working!")
        print("   New responses now properly populate Grade and Assessment fields.")
    else:
        print("❌ Issue: Grade and Assessment are still not populated in new responses.")
    
    conn.close()

def show_maintenance_view_sample():
    """Show what the maintenance view would display"""
    
    conn = sqlite3.connect('data.db')
    cursor = conn.cursor()
    
    print(f"\n=== MAINTENANCE VIEW PREVIEW ===")
    
    cursor.execute("""
        SELECT [res-id], School, Grade, Teacher, Assessment, Name, Date
        FROM responses 
        WHERE [res-id] IN (186, 187)
        GROUP BY [res-id]
        ORDER BY [res-id]
    """)
    
    maintenance_data = cursor.fetchall()
    print("How responses appear in maintenance view:")
    for res_id, school, grade, teacher, assessment, name, date in maintenance_data:
        status = "✅ Grade/Assessment populated" if grade and assessment else "❌ Grade/Assessment empty"
        print(f"  res_id {res_id}: Grade='{grade}', Assessment='{assessment}' - {status}")
    
    conn.close()

if __name__ == "__main__":
    verify_existing_responses()
    show_maintenance_view_sample()
