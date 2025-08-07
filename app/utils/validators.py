"""
Data validation utilities.
"""
from typing import Dict, Any, List
import re
from datetime import datetime, date

from .exceptions import ValidationError


def validate_date_range(start_date: date, end_date: date) -> bool:
    """
    Validate that start_date is before end_date.
    
    Args:
        start_date: Start date
        end_date: End date
        
    Returns:
        True if valid, False otherwise
    """
    return start_date < end_date


def validate_layout_data(layout_data: Dict[str, Any]) -> None:
    """
    Validate layout data structure and content.
    
    Args:
        layout_data: Layout data to validate
        
    Raises:
        ValidationError: If validation fails
    """
    errors = {}
    
    # Validate layout name
    if not layout_data.get('layout_name'):
        errors['layout_name'] = 'Layout name is required'
    elif len(layout_data['layout_name']) > 255:
        errors['layout_name'] = 'Layout name must be less than 255 characters'
    
    # Validate dates
    start_date = layout_data.get('layout_start_date')
    end_date = layout_data.get('layout_end_date')
    
    if start_date and not _is_valid_date(start_date):
        errors['layout_start_date'] = 'Invalid start date format (YYYY-MM-DD expected)'
    
    if end_date and not _is_valid_date(end_date):
        errors['layout_end_date'] = 'Invalid end date format (YYYY-MM-DD expected)'
    
    if start_date and end_date and _is_valid_date(start_date) and _is_valid_date(end_date):
        start_dt = datetime.strptime(start_date, '%Y-%m-%d')
        end_dt = datetime.strptime(end_date, '%Y-%m-%d')
        if start_dt >= end_dt:
            errors['layout_end_date'] = 'End date must be after start date'
    
    # Validate domains
    domains = layout_data.get('domains', [])
    if not domains:
        errors['domains'] = 'At least one domain is required'
    else:
        for i, domain in enumerate(domains):
            domain_errors = _validate_domain(domain)
            if domain_errors:
                errors[f'domain_{i}'] = domain_errors
    
    # Validate metadata
    metadata = layout_data.get('metadata_list', [])
    if metadata:
        for i, meta in enumerate(metadata):
            meta_errors = _validate_metadata(meta)
            if meta_errors:
                errors[f'metadata_{i}'] = meta_errors
    
    if errors:
        raise ValidationError('Validation failed', errors=errors)


def validate_form_input(form_data: Dict[str, Any], required_fields: List[str] = None) -> None:
    """
    Validate form input data.
    
    Args:
        form_data: Form data to validate
        required_fields: List of required field names
        
    Raises:
        ValidationError: If validation fails
    """
    errors = {}
    required_fields = required_fields or []
    
    # Check required fields
    for field in required_fields:
        if not form_data.get(field):
            errors[field] = f'{field} is required'
    
    # Validate specific field formats
    for field, value in form_data.items():
        if field.endswith('_id') and value:
            try:
                int(value)
            except ValueError:
                errors[field] = f'{field} must be a valid integer'
        
        if field.endswith('_date') and value:
            if not _is_valid_date(value):
                errors[field] = f'{field} must be a valid date (YYYY-MM-DD)'
    
    if errors:
        raise ValidationError('Form validation failed', errors=errors)


def sanitize_string(value: str, max_length: int = None) -> str:
    """
    Sanitize string input by removing dangerous characters.
    
    Args:
        value: String to sanitize
        max_length: Maximum allowed length
        
    Returns:
        Sanitized string
    """
    if not isinstance(value, str):
        return str(value)
    
    # Remove potential script tags and other dangerous content
    value = re.sub(r'<script[^>]*>.*?</script>', '', value, flags=re.IGNORECASE | re.DOTALL)
    value = re.sub(r'<.*?>', '', value)  # Remove HTML tags
    value = value.strip()
    
    # Limit length if specified
    if max_length and len(value) > max_length:
        value = value[:max_length]
    
    return value


def validate_id(value: Any, field_name: str = 'ID') -> int:
    """
    Validate and convert ID value to integer.
    
    Args:
        value: Value to validate
        field_name: Field name for error messages
        
    Returns:
        Valid integer ID
        
    Raises:
        ValidationError: If validation fails
    """
    try:
        id_value = int(value)
        if id_value <= 0:
            raise ValidationError(f'{field_name} must be a positive integer')
        return id_value
    except (ValueError, TypeError):
        raise ValidationError(f'{field_name} must be a valid integer')


def _validate_domain(domain: Dict[str, Any]) -> Dict[str, str]:
    """Validate domain data structure."""
    errors = {}
    
    if not domain.get('name'):
        errors['name'] = 'Domain name is required'
    elif len(domain['name']) > 255:
        errors['name'] = 'Domain name must be less than 255 characters'
    
    # Validate subdomains
    subdomains = domain.get('subdomains', [])
    if not subdomains:
        errors['subdomains'] = 'At least one subdomain is required'
    else:
        for i, subdomain in enumerate(subdomains):
            subdomain_errors = _validate_subdomain(subdomain)
            if subdomain_errors:
                errors[f'subdomain_{i}'] = subdomain_errors
    
    return errors


def _validate_subdomain(subdomain: Dict[str, Any]) -> Dict[str, str]:
    """Validate subdomain data structure."""
    errors = {}
    
    if not subdomain.get('name'):
        errors['name'] = 'Subdomain name is required'
    elif len(subdomain['name']) > 255:
        errors['name'] = 'Subdomain name must be less than 255 characters'
    
    # Validate questions
    questions = subdomain.get('questions', [])
    if not questions:
        errors['questions'] = 'At least one question is required'
    else:
        for i, question in enumerate(questions):
            question_errors = _validate_question(question)
            if question_errors:
                errors[f'question_{i}'] = question_errors
    
    return errors


def _validate_question(question: Dict[str, Any]) -> Dict[str, str]:
    """Validate question data structure."""
    errors = {}
    
    if not question.get('name'):
        errors['name'] = 'Question name is required'
    elif len(question['name']) > 255:
        errors['name'] = 'Question name must be less than 255 characters'
    
    question_id = question.get('question_id')
    if question_id is not None:
        try:
            int(question_id)
        except (ValueError, TypeError):
            errors['question_id'] = 'Question ID must be a valid integer'
    
    return errors


def _validate_metadata(metadata: Dict[str, Any]) -> Dict[str, str]:
    """Validate metadata structure."""
    errors = {}
    
    if not metadata.get('name'):
        errors['name'] = 'Metadata name is required'
    elif len(metadata['name']) > 255:
        errors['name'] = 'Metadata name must be less than 255 characters'
    
    question_id = metadata.get('question_id')
    if question_id is not None:
        try:
            int(question_id)
        except (ValueError, TypeError):
            errors['question_id'] = 'Metadata question ID must be a valid integer'
    
    return errors


def _is_valid_date(date_str: str) -> bool:
    """Check if string is a valid date in YYYY-MM-DD format."""
    try:
        datetime.strptime(date_str, '%Y-%m-%d')
        return True
    except (ValueError, TypeError):
        return False
