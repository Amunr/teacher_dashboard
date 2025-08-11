import sqlite3

conn = sqlite3.connect('dev_data.db')
cursor = conn.cursor()

cursor.execute('SELECT COUNT(DISTINCT "res-id") FROM responses')
students = cursor.fetchone()[0]

cursor.execute('SELECT COUNT(*) FROM responses')
total_responses = cursor.fetchone()[0]

cursor.execute('SELECT DISTINCT "res-id", Name FROM responses ORDER BY "res-id" LIMIT 10')
sample_students = cursor.fetchall()

print(f'Students: {students}')
print(f'Total responses: {total_responses}')
print('\nSample students:')
for student in sample_students:
    print(f'  {student[0]}: {student[1]}')

conn.close()
