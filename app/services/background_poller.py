"""
Background scheduler for Google Sheets polling within Flask app.
Simple, reliable approach using threading.
"""
import threading
import time
import logging
from datetime import datetime
from typing import Optional
from app.services.sheets_service import SheetsManagementService

logger = logging.getLogger(__name__)

class FlaskBackgroundPoller:
    """Simple background poller that runs within the Flask app process."""
    
    def __init__(self, db_manager):
        self.db_manager = db_manager
        self.polling_thread: Optional[threading.Thread] = None
        self.stop_event = threading.Event()
        self.is_running = False
        
    def start_polling(self):
        """Start the background polling thread."""
        if self.is_running:
            logger.info("Polling already running")
            return True
            
        self.stop_event.clear()
        self.polling_thread = threading.Thread(target=self._poll_loop, daemon=True)
        self.polling_thread.start()
        self.is_running = True
        logger.info("Background polling started")
        return True
        
    def stop_polling(self):
        """Stop the background polling thread."""
        if not self.is_running:
            return
            
        self.stop_event.set()
        if self.polling_thread and self.polling_thread.is_alive():
            self.polling_thread.join(timeout=5)
        self.is_running = False
        logger.info("Background polling stopped")
        
    def _poll_loop(self):
        """Main polling loop that runs in background thread."""
        logger.info("Starting background polling loop")
        
        while not self.stop_event.is_set():
            try:
                # Get current configuration
                sheets_service = SheetsManagementService(self.db_manager)
                config = sheets_service.get_config()
                
                if not config:
                    logger.debug("No configuration found, waiting...")
                    time.sleep(60)  # Check every minute for config
                    continue
                    
                if not config.get('is_active', False):
                    logger.debug("Polling disabled, waiting...")
                    time.sleep(60)  # Check every minute for activation
                    continue
                
                # Get poll interval (default 5 minutes)
                poll_interval_minutes = config.get('poll_interval', 5)
                poll_interval_seconds = poll_interval_minutes * 60
                
                logger.info(f"Polling cycle starting (interval: {poll_interval_minutes} minutes)")
                
                # Execute the same logic as manual import
                try:
                    result = sheets_service.manual_import()
                    if result['success']:
                        logger.info(f"Auto-import successful: {result['message']}")
                    else:
                        logger.warning(f"Auto-import failed: {result.get('error', 'Unknown error')}")
                except Exception as e:
                    logger.error(f"Auto-import error: {e}")
                
                # Wait for next cycle (with early exit if stop requested)
                logger.info(f"Next poll in {poll_interval_minutes} minutes...")
                for _ in range(poll_interval_seconds):
                    if self.stop_event.is_set():
                        return
                    time.sleep(1)
                    
            except Exception as e:
                logger.error(f"Polling loop error: {e}")
                # Wait a bit before retrying
                time.sleep(30)
                
        logger.info("Polling loop ended")
        
    def get_status(self):
        """Get current polling status."""
        return {
            'running': self.is_running,
            'thread_alive': self.polling_thread.is_alive() if self.polling_thread else False
        }

# Global instance
background_poller: Optional[FlaskBackgroundPoller] = None

def initialize_background_poller(db_manager):
    """Initialize the global background poller instance."""
    global background_poller
    background_poller = FlaskBackgroundPoller(db_manager)
    return background_poller

def get_background_poller() -> Optional[FlaskBackgroundPoller]:
    """Get the global background poller instance."""
    return background_poller
