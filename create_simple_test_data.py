#!/usr/bin/env python3
"""
Create proper test data with character responses (A, B, C, D, E)
"""

import os
import sys
import sqlite3
from datetime import date, timedelta
import random

def create_test_responses():
    """Create test responses with character grades"""
    db_path = 'dev_data.db'
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Clear existing responses
        cursor.execute('DELETE FROM responses')
        
        # Sample data
        schools = ["Lincoln Elementary", "Washington Middle", "Roosevelt High", "Jefferson Elementary"]
        grades = ["K", "1", "2", "3", "4", "5"]
        teachers = ["Ms. Smith", "Mr. Johnson", "Mrs. Davis", "Ms. Wilson", "Mr. Brown"]
        students = [
            "John Doe", "Jane Smith", "Mike Johnson", "Sarah Wilson", "Chris Brown",
            "Emma Davis", "Alex Garcia", "Lily Chen", "Noah Martinez", "Olivia Taylor",
            "Ethan Anderson", "Sophia Williams", "Liam Jones", "Isabella Miller", "Mason Wilson",
            "Ava Perez", "Mia Jones", "Emily Rodriguez", "Jacob Thompson", "Charlotte Lee"
        ]
        grades_pool = ['A', 'B', 'C', 'D', 'E']
        weights = [0.2, 0.3, 0.3, 0.15, 0.05]  # More A's and B's, fewer E's
        
        # Create 25 student responses
        today = date.today()
        for i, student in enumerate(students[:25]):
            res_id = i + 1
            school = random.choice(schools)
            grade = random.choice(grades)
            teacher = random.choice(teachers)
            response_date = today - timedelta(days=random.randint(1, 30))
            
            # Create responses for questions 7-25 (domain questions)
            for question_id in range(7, 26):
                # Use weighted random choice for more realistic grades
                response_grade = random.choices(grades_pool, weights=weights)[0]
                
                cursor.execute("""
                    INSERT INTO responses 
                    ("res-id", "School", "Grade", "Teacher", "Assessment", "Name", "Date", "Index_ID", "Response")
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    res_id,
                    school,
                    grade, 
                    teacher,
                    "Assessment",
                    student,
                    response_date.strftime('%Y-%m-%d'),
                    question_id,
                    response_grade
                ))
        
        conn.commit()
        
        # Check results
        cursor.execute('SELECT COUNT(*) FROM responses')
        count = cursor.fetchone()[0]
        
        cursor.execute('SELECT COUNT(DISTINCT "res-id") FROM responses')
        student_count = cursor.fetchone()[0]
        
        print(f"✅ Created {count} responses for {student_count} students")
        
        # Show sample data
        cursor.execute('''
            SELECT "res-id", Name, School, Grade, Response 
            FROM responses 
            WHERE "res-id" IN (1, 2) 
            ORDER BY "res-id", Index_ID 
            LIMIT 10
        ''')
        
        print("\n📋 Sample responses:")
        for row in cursor.fetchall():
            print(f"  Student {row[0]} ({row[1]}): {row[4]} grade")
        
        conn.close()
        
    except Exception as e:
        print(f"❌ Error creating test data: {e}")

if __name__ == "__main__":
    create_test_responses()
