from app.models.database import DatabaseManager
from config.config import Config
from sqlalchemy import text

db = DatabaseManager(Config().DATABASE_URL)
db.initialize_database()  # Initialize the database first

with db.get_connection() as conn:
    layouts = conn.execute(text("""
        SELECT DISTINCT year_start, year_end, COUNT(Index_ID) as question_count 
        FROM questions 
        WHERE Domain != 'MetaData' 
        GROUP BY year_start, year_end 
        ORDER BY year_start
    """)).fetchall()
    
    print('Available layouts:')
    for layout in layouts:
        print(f'  {layout[0]} to {layout[1]}: {layout[2]} questions')
    
    # Check if 2025-07-01 falls within any layout
    test_date = '2025-07-01'
    valid = conn.execute(text("""
        SELECT COUNT(DISTINCT Index_ID) as valid_questions
        FROM questions 
        WHERE year_start <= :test_date 
        AND year_end >= :test_date 
        AND Domain != 'MetaData'
    """), {"test_date": test_date}).fetchone()
    
    print(f'\nFor date {test_date}: {valid[0]} valid questions found')
