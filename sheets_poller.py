#!/usr/bin/env python3
"""
Google Sheets Polling Service

Standalone service that polls Google Sheets for new data and imports it into the database.
This service runs independently of the Flask application.
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
        logging.FileHandler('sheets_poller.log'),
        logging.StreamHandler(sys.stdout)
    ]
)

logger = logging.getLogger('sheets_poller')


class SheetsPollerService:
    """Main service class for polling Google Sheets."""
    
    def __init__(self, database_url: str):
        """
        Initialize the poller service.
        
        Args:
            database_url: Database connection URL
        """
        self.db_manager = DatabaseManager(database_url)
        self.db_manager.initialize_database()
        
        self.config_model = SheetsConfigModel(self.db_manager)
        self.import_service = SheetsImportService(self.db_manager)
        
        logger.info("Sheets Poller Service initialized")
    
    def get_sheet_data(self, csv_url: str) -> List[List[str]]:
        """
        Fetch data from Google Sheets CSV export.
        
        Args:
            csv_url: CSV export URL
            
        Returns:
            List of rows, each row is a list of cell values
        """
        try:
            logger.info(f"Fetching data from: {csv_url}")
            
            response = requests.get(csv_url, timeout=30)
            response.raise_for_status()
            
            # Parse CSV data
            csv_content = response.text
            csv_reader = csv.reader(StringIO(csv_content))
            rows = list(csv_reader)
            
            logger.info(f"Fetched {len(rows)} rows from Google Sheets")
            return rows
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to fetch sheet data: {e}")
            raise
        except Exception as e:
            logger.error(f"Failed to parse CSV data: {e}")
            raise
    
    def process_new_rows(self, config: Dict[str, Any]) -> int:
        """
        Process new rows from the Google Sheet.
        
        Args:
            config: Sheets configuration dictionary
            
        Returns:
            Number of rows successfully processed
        """
        try:
            # Convert URL to CSV format
            csv_url = self.import_service.convert_sheets_url_to_csv(config['sheet_url'])
            
            # Fetch sheet data
            rows = self.get_sheet_data(csv_url)
            
            if not rows:
                logger.info("No data found in sheet")
                return 0
            
            last_row_processed = config['last_row_processed']
            total_rows = len(rows)
            
            logger.info(f"Sheet has {total_rows} rows, last processed: {last_row_processed}")
            
            # ALWAYS skip the first row (header) - start from row 2
            # If last_row_processed is 0, we start from row 2 (index 1)
            # If last_row_processed is > 0, we start from the next row after it
            start_row = max(2, last_row_processed + 1)  # Start from row 2 or after last processed
            
            if start_row > total_rows:
                logger.info("No new rows to process")
                return 0
            
            # Get new rows to process (convert to 0-based indexing)
            new_rows = rows[start_row - 1:]  
            
            logger.info(f"Processing {len(new_rows)} new rows (starting from row {start_row}, skipping header)")
            
            processed_count = 0
            last_successful_row = last_row_processed
            
            for i, row_data in enumerate(new_rows):
                current_row_number = start_row + i
                
                try:
                    # Skip empty rows
                    if not any(cell.strip() for cell in row_data if cell):
                        logger.debug(f"Skipping empty row {current_row_number}")
                        last_successful_row = current_row_number
                        continue
                    
                    # Process the row
                    res_id = self.import_service.process_sheet_row(row_data, current_row_number)
                    processed_count += 1
                    last_successful_row = current_row_number
                    
                    logger.info(f"Successfully processed row {current_row_number}, created res_id {res_id}")
                    
                except Exception as e:
                    logger.error(f"Failed to process row {current_row_number}: {e}")
                    # Continue processing other rows even if one fails
                    continue
            
            # Update the last processed row in the database
            if last_successful_row > last_row_processed:
                self.config_model.update_last_row_processed(last_successful_row)
                logger.info(f"Updated last processed row to {last_successful_row}")
            
            logger.info(f"Processing complete: {processed_count} rows processed successfully")
            return processed_count
            
        except Exception as e:
            logger.error(f"Failed to process new rows: {e}")
            raise
    
    def poll_once(self) -> bool:
        """
        Perform one polling cycle.
        
        Returns:
            True if polling was successful, False otherwise
        """
        try:
            # Get configuration
            config = self.config_model.get_config()
            
            if not config:
                logger.warning("No active Google Sheets configuration found")
                return False
            
            if not config['is_active']:
                logger.warning("Google Sheets configuration is inactive")
                return False
            
            logger.info(f"Starting poll cycle for sheet: {config['sheet_url']}")
            
            # Process new rows
            processed_count = self.process_new_rows(config)
            
            if processed_count > 0:
                logger.info(f"Poll cycle complete: {processed_count} new rows processed")
            else:
                logger.info("Poll cycle complete: no new rows found")
            
            return True
            
        except Exception as e:
            logger.error(f"Poll cycle failed: {e}")
            return False
    
    def run_continuous(self):
        """
        Run the poller in continuous mode.
        """
        logger.info("Starting continuous polling mode")
        
        while True:
            try:
                # Get current configuration for poll interval
                config = self.config_model.get_config()
                
                if config and config['is_active']:
                    poll_interval = config['poll_interval']
                    
                    # Perform polling
                    success = self.poll_once()
                    
                    if success:
                        logger.info(f"Sleeping for {poll_interval} minutes until next poll")
                    else:
                        logger.warning(f"Poll failed, retrying in {poll_interval} minutes")
                    
                    # Sleep for the configured interval (convert minutes to seconds)
                    time.sleep(poll_interval * 60)
                    
                else:
                    logger.info("No active configuration, sleeping for 5 minutes")
                    time.sleep(5 * 60)  # Sleep for 5 minutes when no config
                    
            except KeyboardInterrupt:
                logger.info("Received interrupt signal, shutting down gracefully")
                break
            except Exception as e:
                logger.error(f"Unexpected error in continuous mode: {e}")
                logger.info("Sleeping for 5 minutes before retry")
                time.sleep(5 * 60)
        
        logger.info("Poller service stopped")
    
    def run_once(self):
        """
        Run the poller once and exit.
        """
        logger.info("Running single poll cycle")
        
        success = self.poll_once()
        
        if success:
            logger.info("Single poll cycle completed successfully")
            return True
        else:
            logger.error("Single poll cycle failed")
            return False


def main():
    """Main entry point for the service."""
    import argparse
    
    parser = argparse.ArgumentParser(description='Google Sheets Polling Service')
    parser.add_argument(
        '--mode', 
        choices=['continuous', 'once'], 
        default='continuous',
        help='Run mode: continuous polling or single poll'
    )
    parser.add_argument(
        '--database-url',
        default=None,
        help='Database URL (defaults to config)'
    )
    
    args = parser.parse_args()
    
    try:
        # Get database URL
        if args.database_url:
            database_url = args.database_url
        else:
            # Try to load from config
            try:
                config = Config()
                database_url = config.SQLALCHEMY_DATABASE_URI
            except Exception as e:
                logger.error(f"Failed to load database URL from config: {e}")
                database_url = "sqlite:///dev_data.db"  # Fallback
                logger.warning(f"Using fallback database URL: {database_url}")
        
        # Initialize service
        service = SheetsPollerService(database_url)
        
        # Run based on mode
        if args.mode == 'continuous':
            service.run_continuous()
        else:
            success = service.run_once()
            sys.exit(0 if success else 1)
            
    except Exception as e:
        logger.error(f"Failed to start service: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
