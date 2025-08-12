from app.models.database import DatabaseManager
from config.config import Config
from sqlalchemy import text

db = DatabaseManager(Config().DATABASE_URL)
db.initialize_database()

with db.get_connection() as conn:
    # Check what's in the responses table
    results = conn.execute(text('SELECT "res-id", School, Grade, Teacher, Assessment, Name, Date FROM responses LIMIT 5')).fetchall()
    
    print('Current responses data:')
    for r in results:
        print(f'  res_id: {r[0]}')
        print(f'    School: "{r[1]}"')
        print(f'    Grade: "{r[2]}"')
        print(f'    Teacher: "{r[3]}"')
        print(f'    Assessment: "{r[4]}"')
        print(f'    Name: "{r[5]}"')
        print(f'    Date: {r[6]}')
        print()
    
    # Check what Index_IDs correspond to Grade and Assessment in the layout
    print('Metadata Index_IDs in current layout:')
    meta_results = conn.execute(text("""
        SELECT Index_ID, SubDomain, Name
        FROM questions 
        WHERE Domain = 'MetaData'
        AND year_start <= '2025-07-01' 
        AND year_end >= '2025-07-01'
        ORDER BY Index_ID
    """)).fetchall()
    
    for r in meta_results:
        print(f'  Index_ID {r[0]}: {r[1]} - {r[2]}')
