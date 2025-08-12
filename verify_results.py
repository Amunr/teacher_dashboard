from app.models.database import DatabaseManager
from config.config import Config
from sqlalchemy import text

db = DatabaseManager(Config().DATABASE_URL)
db.initialize_database()

with db.get_connection() as conn:
    results = conn.execute(text('SELECT "res-id", Date, Index_ID, Response FROM responses ORDER BY "res-id" DESC LIMIT 10')).fetchall()
    
    print('Latest responses:')
    for r in results:
        print(f'  res_id: {r[0]}, Date: {r[1]}, Index_ID: {r[2]}, Response: {r[3]}')
