from app.models.database import DatabaseManager
from config.config import Config
from sqlalchemy import text

db = DatabaseManager(Config().DATABASE_URL)
db.initialize_database()

with db.get_connection() as conn:
    # Check valid Index_IDs for 2025-07-01
    test_date = '2025-07-01'
    valid_ids = conn.execute(text("""
        SELECT Index_ID, Domain, SubDomain, Name
        FROM questions 
        WHERE year_start <= :test_date 
        AND year_end >= :test_date 
        ORDER BY Index_ID
    """), {"test_date": test_date}).fetchall()
    
    print(f'Valid Index_IDs for {test_date}:')
    for row in valid_ids:
        print(f'  Index_ID {row[0]}: {row[1]} > {row[2]} - {row[3]}')
    
    # Check what Index_IDs our test row would have
    print('\nOur test row column mapping:')
    test_columns = [
        "1/7/2025 10:15:12",    # Column A = Index_ID 1
        "John Smith",           # Column B = Index_ID 2
        "Teacher A",            # Column C = Index_ID 3
        "School X",             # Column D = Index_ID 4  
        "Student Name",         # Column E = Index_ID 5
        "4",                    # Column F = Index_ID 6
        "15/12/2010",          # Column G = Index_ID 7
        "5",                    # Column H = Index_ID 8
    ]
    
    for i, value in enumerate(test_columns):
        index_id = i + 1
        print(f'  Index_ID {index_id}: "{value}"')
