#!/usr/bin/env python3
"""
Quick fix for sample data - generate responses directly in the database with correct 1-4 scores
"""

import sqlite3
import random
from datetime import datetime, date

def fix_sample_data():
    """Fix the sample data by creating correct 1-4 scale responses"""
    
    # Connect to the development database
    conn = sqlite3.connect('dev_data.db')
    cursor = conn.cursor()
    
    print("🔧 Fixing sample data with correct 1-4 scale responses...")
    
    # Clear existing responses
    cursor.execute('DELETE FROM responses')
    print("✅ Cleared existing responses")
    
    # Get the questions (Index_IDs 7-64 are the domain questions)
    cursor.execute('SELECT Index_ID, Domain, SubDomain FROM questions WHERE Index_ID BETWEEN 7 AND 64')
    questions = cursor.fetchall()
    print(f"📝 Found {len(questions)} domain questions")
    
    # Student names and demographics
    first_names = ['Emma', 'Liam', 'Olivia', 'Noah', 'Ava', 'Ethan', 'Sophia', 'Mason', 'Isabella', 'William',
                   'Mia', 'James', 'Charlotte', 'Benjamin', 'Amelia', 'Lucas', 'Harper', 'Henry', 'Evelyn', 'Alexander',
                   'Abigail', 'Michael', 'Emily', 'Daniel', 'Elizabeth', 'Jacob', 'Sofia', 'Logan', 'Avery', 'Jackson',
                   'Ella', 'Levi', 'Madison', 'Sebastian', 'Scarlett', 'Mateo', 'Victoria', 'Jack', 'Aria', 'Owen',
                   'Grace', 'Theodore', 'Chloe', 'Aiden', 'Camila', 'Samuel', 'Penelope', 'Joseph', 'Riley', 'John']
    
    last_names = ['Smith', 'Johnson', 'Williams', 'Brown', 'Jones', 'Garcia', 'Miller', 'Davis', 'Rodriguez', 'Martinez',
                  'Hernandez', 'Lopez', 'Gonzalez', 'Wilson', 'Anderson', 'Thomas', 'Taylor', 'Moore', 'Jackson', 'Martin',
                  'Lee', 'Perez', 'Thompson', 'White', 'Harris', 'Sanchez', 'Clark', 'Ramirez', 'Lewis', 'Robinson']
    
    schools = ['Lincoln Elementary', 'Washington Primary', 'Roosevelt School', 'Jefferson Academy', 'Madison Elementary']
    grades = ['Pre-K', 'Kindergarten', 'Grade 1', 'Grade 2']
    teachers = ['Ms. Anderson', 'Mr. Johnson', 'Ms. Garcia', 'Mr. Thompson', 'Ms. Rodriguez', 'Mr. Davis']
    assessments = ['Fall Assessment 2024', 'Winter Assessment 2024', 'Spring Assessment 2024']
    
    # Generate 50 students
    students = [(f"{random.choice(first_names)} {random.choice(last_names)}", 
                random.choice(schools), 
                random.choice(grades), 
                random.choice(teachers), 
                random.choice(assessments)) for _ in range(50)]
    
    assessment_date = datetime.now().strftime('%Y-%m-%d')
    
    # Create responses for each student
    response_records = []
    for res_id, (student_name, school, grade, teacher, assessment) in enumerate(students, 1):
        
        # Determine student performance level
        if res_id <= 15:  # Top 30% - high performers
            base_weights = [5, 15, 35, 45]  # Mostly 3s and 4s
        elif res_id <= 35:  # Middle 40% - average performers  
            base_weights = [10, 30, 40, 20]  # Mix of 2, 3, 4
        elif res_id <= 45:  # Next 20% - below average
            base_weights = [30, 40, 25, 5]  # Mix of 1, 2, 3
        else:  # Bottom 10% - struggling students
            base_weights = [50, 35, 15, 0]  # Mostly 1s and 2s
        
        # Generate responses for all domain questions
        for index_id, domain, subdomain in questions:
            # Small random variation in performance per question
            weights = base_weights.copy()
            if random.random() < 0.1:  # 10% chance of variation
                # Shift performance slightly
                if random.random() < 0.5:
                    # Better performance
                    weights = [max(0, w-5) for w in weights[:-1]] + [weights[-1] + 15]
                else:
                    # Worse performance  
                    weights = [weights[0] + 15] + [max(0, w-5) for w in weights[1:]]
            
            # Generate score (1-4 scale)
            score = random.choices([1, 2, 3, 4], weights=weights)[0]
            
            response_records.append((
                res_id,           # res-id
                school,           # School
                grade,            # Grade  
                teacher,          # Teacher
                assessment,       # Assessment
                student_name,     # Name
                assessment_date,  # Date
                index_id,         # Index_ID
                score            # Response (1-4 scale)
            ))
    
    # Insert all responses
    cursor.executemany('''
        INSERT INTO responses (
            [res-id], School, Grade, Teacher, Assessment, Name, Date, Index_ID, Response
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', response_records)
    
    conn.commit()
    
    # Verify the data
    cursor.execute('SELECT MIN(Response), MAX(Response), AVG(Response), COUNT(*) FROM responses')
    min_resp, max_resp, avg_resp, count = cursor.fetchone()
    
    print(f"✅ Created {count} response records")
    print(f"📊 Response range: {min_resp} to {max_resp} (should be 1-4)")
    print(f"📈 Average response: {avg_resp:.2f}")
    
    conn.close()
    print("🎉 Sample data fixed successfully!")

if __name__ == "__main__":
    fix_sample_data()
