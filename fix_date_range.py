import sqlite3
from datetime import date, datetime

# Option 1: Extend the date range to include current date
conn = sqlite3.connect('data.db')
cursor = conn.cursor()

# Check current range
cursor.execute('SELECT MIN(year_start), MAX(year_end) FROM questions')
current_range = cursor.fetchone()
print(f'Current date range: {current_range[0]} to {current_range[1]}')

# Extend to include current date and future
new_end_date = '2026-12-31'
cursor.execute('UPDATE questions SET year_end = ?', (new_end_date,))
print(f'Updated year_end to: {new_end_date}')

# Verify the update
cursor.execute('SELECT COUNT(*) FROM questions WHERE year_start <= ? AND year_end >= ?', (str(date.today()), str(date.today())))
count = cursor.fetchone()[0]
print(f'Questions now found for today: {count}')

conn.commit()
conn.close()

print('Date range extended successfully!')
