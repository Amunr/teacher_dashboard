import sqlite3
from datetime import date

conn = sqlite3.connect('data.db')
cursor = conn.cursor()

today = date.today()
print(f'Today: {today} (type: {type(today)})')

# Check sample questions
cursor.execute('SELECT year_start, year_end, Domain, SubDomain FROM questions LIMIT 3')
sample = cursor.fetchall()
print(f'Sample questions:')
for row in sample:
    print(f'  {row[0]} to {row[1]} (types: {type(row[0])}, {type(row[1])})')

# Test query with string conversion
today_str = str(today)
print(f'Today as string: {today_str}')

cursor.execute('SELECT COUNT(*) FROM questions WHERE year_start <= ? AND year_end >= ?', (today_str, today_str))
count = cursor.fetchone()[0]
print(f'Questions found with string date: {count}')

# Also check the sheets config last row
cursor.execute('SELECT last_row_processed FROM sheets_config')
last_row = cursor.fetchone()[0]
print(f'Current last_row_processed: {last_row}')

conn.close()
