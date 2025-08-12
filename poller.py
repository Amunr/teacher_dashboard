#!/usr/bin/env python3
"""
Standalone Google Sheets Poller

This script runs the Google Sheets polling service independently of the Flask application.
It uses the reorganized app structure.
"""

import sys
import os
import argparse
import logging
import time
from pathlib import Path

# Add the current directory to Python path
sys.path.insert(0, str(Path(__file__).parent))

from app.models.database import DatabaseManager
from app.services.sheets_service import SheetsManagementService
from config.config import Config

def setup_logging(log_file: str = 'sheets_poller.log'):
    """Setup logging for the poller."""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_file),
            logging.StreamHandler(sys.stdout)
        ]
    )
    return logging.getLogger('sheets_poller')

def poll_once(db_manager: DatabaseManager) -> dict:
    """
    Poll sheets once and return results.
    
    Args:
        db_manager: Database manager instance
        
    Returns:
        Dictionary with polling results
    """
    sheets_service = SheetsManagementService(db_manager)
    
    # Get current configuration
    config = sheets_service.get_config()
    if not config:
        return {
            'status': 'error',
            'message': 'No Google Sheets configuration found'
        }
    
    if not config.get('enabled', False):
        return {
            'status': 'skipped',
            'message': 'Google Sheets polling is disabled'
        }
    
    try:
        # Trigger import
        result = sheets_service.import_data()
        return {
            'status': 'success',
            'message': f"Import completed: {result['message']}",
            'details': result
        }
    except Exception as e:
        return {
            'status': 'error',
            'message': f"Import failed: {str(e)}"
        }

def poll_continuously(db_manager: DatabaseManager, interval: int = 300):
    """
    Poll sheets continuously at specified intervals.
    
    Args:
        db_manager: Database manager instance
        interval: Polling interval in seconds
    """
    logger = logging.getLogger('sheets_poller')
    logger.info(f"Starting continuous polling every {interval} seconds...")
    
    while True:
        try:
            result = poll_once(db_manager)
            logger.info(f"Polling result: {result}")
            
        except KeyboardInterrupt:
            logger.info("Polling stopped by user")
            break
        except Exception as e:
            logger.error(f"Unexpected error during polling: {e}")
        
        # Wait for next cycle
        try:
            time.sleep(interval)
        except KeyboardInterrupt:
            logger.info("Polling stopped by user")
            break

def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description='Google Sheets Poller for KEF Teacher Dashboard',
        epilog='Examples:\n'
               '  python poller.py --once           # Run once\n'
               '  python poller.py --interval 60    # Poll every minute\n'
               '  python poller.py                  # Poll every 5 minutes (default)',
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    parser.add_argument(
        '--once', 
        action='store_true',
        help='Run once instead of continuous polling'
    )
    parser.add_argument(
        '--interval', 
        type=int, 
        default=300,
        help='Polling interval in seconds (default: 300 = 5 minutes)'
    )
    parser.add_argument(
        '--log-file',
        default='sheets_poller.log',
        help='Log file path (default: sheets_poller.log)'
    )
    parser.add_argument(
        '--config',
        help='Path to configuration file (uses default config if not specified)'
    )
    
    args = parser.parse_args()
    
    # Setup logging
    logger = setup_logging(args.log_file)
    
    try:
        # Initialize database
        if args.config:
            # Load custom config if specified
            # This would need to be implemented if custom configs are needed
            logger.warning("Custom config not yet implemented, using default")
        
        # Use default configuration
        config = Config()
        db_manager = DatabaseManager(config.DATABASE_URL)
        db_manager.initialize_database()
        
        logger.info("Database initialized successfully")
        
        if args.once:
            # Single run
            logger.info("Running single polling cycle...")
            result = poll_once(db_manager)
            logger.info(f"Polling completed: {result}")
            
            # Exit with appropriate code
            if result['status'] == 'success':
                print(f"✅ {result['message']}")
                sys.exit(0)
            elif result['status'] == 'skipped':
                print(f"⚠️ {result['message']}")
                sys.exit(0)
            else:
                print(f"❌ {result['message']}")
                sys.exit(1)
        else:
            # Continuous polling
            poll_continuously(db_manager, args.interval)
            
    except Exception as e:
        logger.error(f"Failed to start poller: {e}")
        print(f"❌ Failed to start poller: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
