#!/usr/bin/env python3
"""
Single run version of sheets poller for debugging
"""

import csv
import time
import logging
import requests
import sys
import os
from datetime import datetime, date
from typing import List, Dict, Any, Optional
from io import StringIO

# Add the app directory to the path so we can import models
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.models.database import DatabaseManager, SheetsConfigModel, SheetsImportService
from config.config import Config

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)

logger = logging.getLogger('sheets_poller_single')

def debug_database_state():
    """Debug current database state"""
    import sqlite3
    
    conn = sqlite3.connect('data.db')
    cursor = conn.cursor()
    
    # Check responses count
    cursor.execute('SELECT COUNT(*) FROM responses')
    responses_count = cursor.fetchone()[0]
    logger.info(f"Current responses count: {responses_count}")
    
    # Check questions count for today
    today_str = str(date.today())
    cursor.execute('SELECT COUNT(*) FROM questions WHERE year_start <= ? AND year_end >= ?', (today_str, today_str))
    questions_count = cursor.fetchone()[0]
    logger.info(f"Questions valid for today ({today_str}): {questions_count}")
    
    # Check sample questions
    cursor.execute('SELECT Domain, SubDomain FROM questions WHERE year_start <= ? AND year_end >= ? LIMIT 3', (today_str, today_str))
    sample_questions = cursor.fetchall()
    logger.info(f"Sample questions: {sample_questions}")
    
    # Check sheets config
    cursor.execute('SELECT * FROM sheets_config')
    config = cursor.fetchone()
    if config:
        logger.info(f"Sheets config - URL: {config[1]}, Last row: {config[2]}, Active: {config[3]}")
    else:
        logger.error("No sheets config found!")
        
    conn.close()

def single_poll_run():
    """Run a single poll cycle with extensive debugging"""
    logger.info("=== STARTING SINGLE POLL RUN ===")
    
    debug_database_state()
    
    try:
        db_manager = DatabaseManager('sqlite:///data.db')
        db_manager.initialize_database()
        
        config_model = SheetsConfigModel(db_manager)
        import_service = SheetsImportService(db_manager)
        
        # Get configuration
        config = config_model.get_config()
        if not config:
            logger.error("No sheets configuration found")
            return False
            
        logger.info(f"Config loaded: URL={config['sheet_url']}, last_row={config['last_row_processed']}")
        
        # Fetch CSV data
        logger.info("Fetching CSV data from Google Sheets...")
        response = requests.get(config['sheet_url'], timeout=30)
        response.raise_for_status()
        
        # Increase CSV field size limit
        csv.field_size_limit(1000000)  # 1MB limit
        
        csv_reader = csv.DictReader(StringIO(response.text))
        rows = list(csv_reader)
        
        logger.info(f"Fetched {len(rows)} total rows from sheet")
        
        # Find new rows
        start_row = config['last_row_processed'] + 1
        new_rows = rows[start_row - 1:start_row + 2]  # Process just 3 rows for debugging
        
        logger.info(f"Processing rows {start_row} to {start_row + len(new_rows) - 1}")
        
        if not new_rows:
            logger.info("No new rows to process")
            return True
            
        # Process each row with detailed logging
        processed_count = 0
        for i, row_data in enumerate(new_rows):
            current_row = start_row + i
            logger.info(f"\n--- PROCESSING ROW {current_row} ---")
            logger.info(f"Raw row data: {dict(row_data)}")
            
            try:
                # Process the row
                result = import_service.process_row_data(row_data, row_number=current_row)
                
                if result:
                    processed_count += 1
                    logger.info(f"Row {current_row} processed successfully")
                else:
                    logger.warning(f"Row {current_row} failed to process")
                    
            except Exception as e:
                logger.error(f"Error processing row {current_row}: {e}")
                import traceback
                traceback.print_exc()
        
        # Update last processed row
        if processed_count > 0:
            new_last_row = start_row + len(new_rows) - 1
            config_model.update_last_row_processed(new_last_row)
            logger.info(f"Updated last_row_processed to {new_last_row}")
        
        logger.info(f"=== POLL COMPLETE: {processed_count} rows processed ===")
        
        # Check final database state
        debug_database_state()
        
        return True
        
    except Exception as e:
        logger.error(f"Poll failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    single_poll_run()
