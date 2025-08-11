"""
Service layer for Google Sheets integration within the Flask application.
"""

from typing import Dict, List, Any, Optional
from datetime import date
import logging
import requests
import csv
from io import StringIO

from app.models.database import (
    DatabaseManager, SheetsConfigModel, FailedImportsModel, 
    SheetsImportService, ResponseModel
)

logger = logging.getLogger(__name__)


class SheetsManagementService:
    """Service for managing Google Sheets integration from the Flask app."""
    
    def __init__(self, db_manager: DatabaseManager):
        self.db_manager = db_manager
        self.config_model = SheetsConfigModel(db_manager)
        self.failed_imports_model = FailedImportsModel(db_manager)
        self.import_service = SheetsImportService(db_manager)
        self.response_model = ResponseModel(db_manager)
    
    def get_config(self) -> Optional[Dict[str, Any]]:
        """Get current Google Sheets configuration."""
        return self.config_model.get_config()
    
    def update_config(self, sheet_url: str, poll_interval: int) -> Dict[str, Any]:
        """
        Update Google Sheets configuration.
        
        Args:
            sheet_url: Google Sheets URL
            poll_interval: Polling interval in minutes
            
        Returns:
            Configuration status
        """
        try:
            # Validate the URL by trying to convert it
            csv_url = self.import_service.convert_sheets_url_to_csv(sheet_url)
            
            # Test if the sheet is accessible
            try:
                response = requests.get(csv_url, timeout=10)
                response.raise_for_status()
            except requests.exceptions.RequestException as e:
                return {
                    'success': False,
                    'error': f'Cannot access Google Sheet: {str(e)}. Make sure the sheet is publicly viewable.'
                }
            
            # Create or update configuration
            config_id = self.config_model.create_or_update_config(sheet_url, poll_interval)
            
            return {
                'success': True,
                'config_id': config_id,
                'message': 'Configuration updated successfully'
            }
            
        except Exception as e:
            logger.error(f"Failed to update sheets config: {e}")
            return {
                'success': False,
                'error': f'Failed to update configuration: {str(e)}'
            }
    
    def get_failed_imports(self) -> List[Dict[str, Any]]:
        """Get all unresolved failed imports."""
        return self.failed_imports_model.get_failed_imports(include_resolved=False)
    
    def retry_failed_import(self, failed_import_id: int) -> Dict[str, Any]:
        """
        Retry a specific failed import by re-fetching the row from Google Sheets.
        
        Args:
            failed_import_id: ID of the failed import to retry
            
        Returns:
            Retry result
        """
        try:
            # Get the failed import record
            failed_imports = self.failed_imports_model.get_failed_imports(include_resolved=True)
            failed_import = next((fi for fi in failed_imports if fi['id'] == failed_import_id), None)
            
            if not failed_import:
                return {
                    'success': False,
                    'error': 'Failed import record not found'
                }
            
            sheet_row_number = failed_import['sheet_row_number']
            
            # Get current configuration
            config = self.get_config()
            if not config:
                return {
                    'success': False,
                    'error': 'No active Google Sheets configuration found'
                }
            
            # Fetch the specific row from Google Sheets
            try:
                csv_url = self.import_service.convert_sheets_url_to_csv(config['sheet_url'])
                response = requests.get(csv_url, timeout=30)
                response.raise_for_status()
                
                # Parse CSV and get the specific row
                csv_content = response.text
                csv_reader = csv.reader(StringIO(csv_content))
                rows = list(csv_reader)
                
                if sheet_row_number > len(rows):
                    return {
                        'success': False,
                        'error': f'Row {sheet_row_number} not found in current sheet (sheet has {len(rows)} rows)'
                    }
                
                # Get the row data (convert to 0-based indexing)
                row_data = rows[sheet_row_number - 1]
                
                # Process the row
                res_id = self.import_service.process_sheet_row(row_data, sheet_row_number)
                
                # Mark the failed import as resolved
                self.failed_imports_model.mark_resolved(failed_import_id)
                
                return {
                    'success': True,
                    'res_id': res_id,
                    'message': f'Successfully processed row {sheet_row_number}, created res_id {res_id}'
                }
                
            except Exception as e:
                # Increment retry count
                self.failed_imports_model.retry_failed_import(failed_import_id)
                
                return {
                    'success': False,
                    'error': f'Failed to retry import: {str(e)}'
                }
                
        except Exception as e:
            logger.error(f"Failed to retry import {failed_import_id}: {e}")
            return {
                'success': False,
                'error': f'System error: {str(e)}'
            }
    
    def test_sheet_connection(self, sheet_url: str) -> Dict[str, Any]:
        """
        Test connection to a Google Sheet.
        
        Args:
            sheet_url: Google Sheets URL to test
            
        Returns:
            Test result
        """
        try:
            # Convert URL
            csv_url = self.import_service.convert_sheets_url_to_csv(sheet_url)
            
            # Test connection
            response = requests.get(csv_url, timeout=10)
            response.raise_for_status()
            
            # Parse a few rows to check structure
            csv_content = response.text
            csv_reader = csv.reader(StringIO(csv_content))
            rows = list(csv_reader)
            
            return {
                'success': True,
                'message': f'Successfully connected to sheet',
                'total_rows': len(rows),
                'csv_url': csv_url,
                'sample_data': rows[:3] if rows else []  # First 3 rows as sample
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': f'Connection test failed: {str(e)}'
            }
    
    def get_import_stats(self) -> Dict[str, Any]:
        """Get statistics about imports."""
        try:
            config = self.get_config()
            failed_imports = self.get_failed_imports()
            
            stats = {
                'is_configured': config is not None,
                'last_row_processed': config['last_row_processed'] if config else 0,
                'poll_interval': config['poll_interval'] if config else 0,
                'sheet_url': config['sheet_url'] if config else '',
                'failed_imports_count': len(failed_imports),
                'is_active': config['is_active'] if config else False
            }
            
            return stats
            
        except Exception as e:
            logger.error(f"Failed to get import stats: {e}")
            return {
                'is_configured': False,
                'last_row_processed': 0,
                'poll_interval': 0,
                'sheet_url': '',
                'failed_imports_count': 0,
                'is_active': False
            }
    
    def deactivate_config(self) -> Dict[str, Any]:
        """Deactivate the current configuration."""
        try:
            self.config_model.deactivate_config()
            return {
                'success': True,
                'message': 'Configuration deactivated successfully'
            }
        except Exception as e:
            logger.error(f"Failed to deactivate config: {e}")
            return {
                'success': False,
                'error': f'Failed to deactivate configuration: {str(e)}'
            }
    
    def delete_failed_import(self, failed_import_id: int) -> Dict[str, Any]:
        """Delete a failed import record."""
        try:
            self.failed_imports_model.delete_failed_import(failed_import_id)
            return {
                'success': True,
                'message': 'Failed import record deleted successfully'
            }
        except Exception as e:
            logger.error(f"Failed to delete failed import {failed_import_id}: {e}")
            return {
                'success': False,
                'error': f'Failed to delete record: {str(e)}'
            }
    
    def manual_import(self) -> Dict[str, Any]:
        """Trigger a manual import from Google Sheets."""
        try:
            config = self.config_model.get_config()
            if not config:
                return {
                    'success': False,
                    'error': 'No Google Sheets configuration found'
                }
            
            if not config['sheet_url']:
                return {
                    'success': False,
                    'error': 'No sheet URL configured'
                }
            
            # Use the import service to process new rows
            import_service = SheetsImportService(self.db_manager)
            result = import_service.fetch_and_process_new_rows(
                config['sheet_url'],
                config['last_row_processed']
            )
            
            if result['success']:
                # Update last_row_processed
                new_last_row = config['last_row_processed'] + result.get('processed_rows', 0)
                self.config_model.update_last_row_processed(new_last_row)
                
                return {
                    'success': True,
                    'processed_rows': result.get('processed_rows', 0),
                    'message': f'Successfully imported {result.get("processed_rows", 0)} new rows'
                }
            else:
                return {
                    'success': False,
                    'error': result.get('error', 'Import failed')
                }
                
        except Exception as e:
            logger.error(f"Manual import failed: {e}")
            return {
                'success': False,
                'error': f'Manual import failed: {str(e)}'
            }
    
    def retry_all_failed_imports(self) -> Dict[str, Any]:
        """Retry all failed imports."""
        try:
            failed_imports = self.failed_imports_model.get_failed_imports()
            retried_count = 0
            
            for failed_import in failed_imports:
                try:
                    # Use the import service to retry the import
                    import_service = SheetsImportService(self.db_manager)
                    result = import_service.process_row_data(
                        failed_import['row_data'],
                        failed_import['row_number']
                    )
                    
                    if result['success']:
                        # Delete the failed import record
                        self.failed_imports_model.delete_failed_import(failed_import['id'])
                        retried_count += 1
                        
                except Exception as e:
                    logger.error(f"Failed to retry import {failed_import['id']}: {e}")
                    continue
            
            return {
                'success': True,
                'retried_count': retried_count,
                'message': f'Successfully retried {retried_count} failed imports'
            }
            
        except Exception as e:
            logger.error(f"Retry all failed imports failed: {e}")
            return {
                'success': False,
                'error': f'Retry operation failed: {str(e)}'
            }
    
    def delete_all_failed_imports(self) -> Dict[str, Any]:
        """Delete all failed import records."""
        try:
            failed_imports = self.failed_imports_model.get_failed_imports()
            deleted_count = len(failed_imports)
            
            for failed_import in failed_imports:
                self.failed_imports_model.delete_failed_import(failed_import['id'])
            
            return {
                'success': True,
                'deleted_count': deleted_count,
                'message': f'Successfully deleted {deleted_count} failed import records'
            }
            
        except Exception as e:
            logger.error(f"Delete all failed imports failed: {e}")
            return {
                'success': False,
                'error': f'Delete operation failed: {str(e)}'
            }
