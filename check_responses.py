import sqlite3

conn = sqlite3.connect('dev_data.db')
cursor = conn.cursor()

cursor.execute('SELECT COUNT(*) FROM responses')
total = cursor.fetchone()[0]
print(f'Total responses: {total}')

cursor.execute('SELECT COUNT(DISTINCT `res-id`) FROM responses')
unique = cursor.fetchone()[0]
print(f'Unique response IDs: {unique}')

if total > 0:
    cursor.execute('SELECT `res-id`, School, Teacher, Name FROM responses LIMIT 5')
    samples = cursor.fetchall()
    print('Sample responses:')
    for sample in samples:
        print(f'  {sample}')

conn.close()
