"""
Utility helper functions.
"""
import time
from typing import Any, Dict, List
from datetime import datetime, date
import logging

logger = logging.getLogger(__name__)


def generate_unique_id() -> int:
    """Generate a unique ID based on current timestamp."""
    return int(time.time() * 1000)


def safe_int_conversion(value: Any, default: int = 0) -> int:
    """
    Safely convert value to integer.
    
    Args:
        value: Value to convert
        default: Default value if conversion fails
        
    Returns:
        Integer value or default
    """
    try:
        return int(value)
    except (ValueError, TypeError):
        return default


def safe_string_conversion(value: Any, default: str = '') -> str:
    """
    Safely convert value to string.
    
    Args:
        value: Value to convert
        default: Default value if conversion fails
        
    Returns:
        String value or default
    """
    try:
        return str(value) if value is not None else default
    except Exception:
        return default


def parse_date_string(date_str: str) -> date:
    """
    Parse date string in YYYY-MM-DD format.
    
    Args:
        date_str: Date string to parse
        
    Returns:
        Date object or None if parsing fails
    """
    try:
        return datetime.strptime(date_str, '%Y-%m-%d').date()
    except (ValueError, TypeError):
        return None


def format_date_for_display(date_obj: date) -> str:
    """
    Format date object for display.
    
    Args:
        date_obj: Date object to format
        
    Returns:
        Formatted date string
    """
    try:
        return date_obj.strftime('%Y-%m-%d') if date_obj else ''
    except (ValueError, TypeError):
        return ''


def flatten_layout_for_database(layout: Dict[str, Any], layout_id: int = None) -> List[Dict[str, Any]]:
    """
    Convert layout structure to flat database records.
    
    Args:
        layout: Layout structure
        layout_id: Optional layout ID for updates
        
    Returns:
        List of database records
    """
    records = []
    
    # Process domains and questions
    for domain in layout.get('domains', []):
        domain_name = domain.get('name', '')
        for subdomain in domain.get('subdomains', []):
            subdomain_name = subdomain.get('name', '')
            for question in subdomain.get('questions', []):
                record = {
                    'year_start': layout.get('layout_start_date'),
                    'year_end': layout.get('layout_end_date'),
                    'Domain': domain_name,
                    'SubDomain': subdomain_name,
                    'Index_ID': question.get('question_id', 0),
                    'Name': question.get('name', ''),
                    'Date edited': layout.get('layout_start_date'),
                    'layout_name': layout.get('layout_name', 'New Layout')
                }
                if layout_id is not None:
                    record['layout_id'] = layout_id
                records.append(record)
    
    # Process metadata
    for metadata in layout.get('metadata_list', []):
        record = {
            'year_start': layout.get('layout_start_date'),
            'year_end': layout.get('layout_end_date'),
            'Domain': 'MetaData',
            'SubDomain': '',
            'Index_ID': metadata.get('question_id', 0),
            'Name': metadata.get('name', ''),
            'Date edited': layout.get('layout_start_date'),
            'layout_name': layout.get('layout_name', 'New Layout')
        }
        if layout_id is not None:
            record['layout_id'] = layout_id
        records.append(record)
    
    return records


def log_operation(operation: str, details: Dict[str, Any] = None) -> None:
    """
    Log application operations.
    
    Args:
        operation: Operation description
        details: Additional operation details
    """
    details = details or {}
    logger.info(f"Operation: {operation}", extra=details)


def create_response_context(message: str, status: str = 'success', data: Any = None) -> Dict[str, Any]:
    """
    Create standardized response context.
    
    Args:
        message: Response message
        status: Response status (success, error, warning)
        data: Additional response data
        
    Returns:
        Response context dictionary
    """
    return {
        'message': message,
        'status': status,
        'data': data,
        'timestamp': datetime.now().isoformat()
    }
