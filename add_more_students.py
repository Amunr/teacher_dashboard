import sqlite3
import random
from datetime import date

conn = sqlite3.connect('dev_data.db')
cursor = conn.cursor()

# Get current max ID
cursor.execute('SELECT MAX("res-id") FROM responses')
max_id = cursor.fetchone()[0] or 0

print(f'Adding more students starting from ID {max_id + 1}')

# Add 5 more students
grades_pool = ['A', 'B', 'C', 'D', 'E']
weights = [0.2, 0.3, 0.3, 0.15, 0.05]
schools = ['Lincoln Elementary', 'Washington Middle']
grades = ['K', '1', '2', '3']
teachers = ['Ms. Smith', 'Mr. Johnson']
today = date.today()

students = ['Test Student 1', 'Test Student 2', 'Test Student 3', 'Test Student 4', 'Test Student 5']

for i, student in enumerate(students):
    res_id = max_id + 1 + i
    school = random.choice(schools)
    grade = random.choice(grades)
    teacher = random.choice(teachers)
    
    # Add responses for questions 7-25
    for question_id in range(7, 26):
        response_grade = random.choices(grades_pool, weights=weights)[0]
        cursor.execute("""
            INSERT INTO responses 
            ("res-id", "School", "Grade", "Teacher", "Assessment", "Name", "Date", "Index_ID", "Response")
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            res_id, school, grade, teacher, 'Assessment', student,
            today.strftime('%Y-%m-%d'), question_id, response_grade
        ))

conn.commit()

# Check new count
cursor.execute('SELECT COUNT(DISTINCT "res-id") FROM responses')
total_students = cursor.fetchone()[0]
print(f'Now have {total_students} students')

conn.close()
