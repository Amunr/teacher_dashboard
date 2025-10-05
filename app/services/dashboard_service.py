"""
Dashboard service for handling data aggregation and business logic.
"""
from typing import Dict, Any, List, Optional
from datetime import date, datetime, timedelta
import logging

from ..models.database import DatabaseManager, ResponseModel, StudentCountModel
from ..utils.validators import validate_date_range

logger = logging.getLogger(__name__)


class DashboardService:
    """Service for dashboard data operations."""
    
    def __init__(self, db_manager: DatabaseManager):
        self.db_manager = db_manager
        self.response_model = ResponseModel(db_manager)
        self.student_count_model = StudentCountModel(db_manager)
    
    def get_dashboard_data(self, filters: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Get comprehensive dashboard data with filtering.
        
        Args:
            filters: Dictionary of filter criteria
            
        Returns:
            Complete dashboard data dictionary
        """
        try:
            # Validate and normalize filters
            normalized_filters = self._normalize_filters(filters or {})
            
            # Get core dashboard metrics
            dashboard_data = self.response_model.get_dashboard_data(normalized_filters)
            
            # Add filter options for frontend
            dashboard_data['filter_options'] = self.response_model.get_filter_options()
            
            # Add current filter state
            dashboard_data['current_filters'] = normalized_filters
            
            return dashboard_data
            
        except Exception as e:
            logger.error(f"Failed to get dashboard data: {e}")
            raise
    
    def get_student_list(self, filters: Dict[str, Any] = None, page: int = 1, per_page: int = 50) -> Dict[str, Any]:
        """
        Get paginated student list with scores.
        
        Args:
            filters: Dictionary of filter criteria
            page: Page number (1-based)
            per_page: Records per page
            
        Returns:
            Dictionary with student data and pagination info
        """
        try:
            normalized_filters = self._normalize_filters(filters or {})
            offset = (page - 1) * per_page
            
            # Get responses with filtering applied
            # If student name filter is applied, get more data to ensure we have enough students
            limit_multiplier = 50 if 'student_name' in normalized_filters else 10
            responses = self.response_model.get_responses(
                filters=normalized_filters,
                limit=per_page * limit_multiplier,
                offset=0
            )
            
            # Group responses by student (res_id)
            student_data = {}
            domain_questions = {}
            
            for response in responses:
                res_id = response['res-id']
                domain = response['Domain']
                
                if res_id not in student_data:
                    student_data[res_id] = {
                        'res_id': res_id,
                        'name': response['Name'],
                        'school': response['School'],
                        'grade': response['Grade'],
                        'teacher': response['Teacher'],
                        'assessment': response['Assessment'],
                        'date': response['Date'],
                        'domain_scores': {},
                        'total_score': 0,
                        'total_questions': 0
                    }
                
                if domain not in student_data[res_id]['domain_scores']:
                    student_data[res_id]['domain_scores'][domain] = {
                        'score': 0,
                        'questions': 0
                    }
                
                # Convert response to numeric value (handle both characters and numbers)
                response_value = self._convert_response_to_numeric(response['Response'])
                
                student_data[res_id]['domain_scores'][domain]['score'] += response_value
                student_data[res_id]['domain_scores'][domain]['questions'] += 1
                student_data[res_id]['total_score'] += response_value
                student_data[res_id]['total_questions'] += 1
                
                # Track unique domains
                if domain not in domain_questions:
                    domain_questions[domain] = set()
                domain_questions[domain].add(response['Index_ID'])            # Calculate percentage scores
            students = []
            for student in student_data.values():
                # Calculate overall percentage (max score per question is 1)
                if student['total_questions'] > 0:
                    max_possible_score = student['total_questions'] * 1
                    student['percentage'] = round((student['total_score'] / max_possible_score) * 100, 1)
                else:
                    student['percentage'] = 0
                
                # Calculate domain percentages (max score per question is 1)
                for domain_data in student['domain_scores'].values():
                    if domain_data['questions'] > 0:
                        max_possible_score = domain_data['questions'] * 1
                        domain_data['percentage'] = round((domain_data['score'] / max_possible_score) * 100, 1)
                    else:
                        domain_data['percentage'] = 0
                
                students.append(student)
            
            # Sort by percentage (highest first)
            students.sort(key=lambda x: x['percentage'], reverse=True)
            
            # Apply pagination to final student list
            total_students = len(students)
            start_idx = offset
            end_idx = start_idx + per_page
            paginated_students = students[start_idx:end_idx]
            
            return {
                'students': paginated_students,
                'domains': list(domain_questions.keys()),
                'pagination': {
                    'page': page,
                    'per_page': per_page,
                    'total': total_students,
                    'pages': (total_students + per_page - 1) // per_page
                }
            }
            
        except Exception as e:
            logger.error(f"Failed to get student list: {e}")
            raise
    
    def create_student_count(self, start_date: date, end_date: date, total_students: int, description: str = None) -> int:
        """
        Create a new student count entry with validation.
        
        Args:
            start_date: Start date of the range
            end_date: End date of the range
            total_students: Total number of students
            description: Optional description
            
        Returns:
            Created record ID
        """
        try:
            # Validate date range
            if not validate_date_range(start_date, end_date):
                raise ValueError("Invalid date range: start_date must be before end_date")
            
            if total_students < 0:
                raise ValueError("Total students must be non-negative")
            
            return self.student_count_model.create_student_count(
                start_date, end_date, total_students, description
            )
            
        except Exception as e:
            logger.error(f"Failed to create student count: {e}")
            raise
    
    def update_student_count(self, count_id: int, start_date: date, end_date: date, 
                           total_students: int, description: str = None) -> None:
        """
        Update a student count entry with validation.
        
        Args:
            count_id: ID of the record to update
            start_date: Start date of the range
            end_date: End date of the range
            total_students: Total number of students
            description: Optional description
        """
        try:
            # Validate date range
            if not validate_date_range(start_date, end_date):
                raise ValueError("Invalid date range: start_date must be before end_date")
            
            if total_students < 0:
                raise ValueError("Total students must be non-negative")
            
            self.student_count_model.update_student_count(
                count_id, start_date, end_date, total_students, description
            )
            
        except Exception as e:
            logger.error(f"Failed to update student count: {e}")
            raise
    
    def delete_student_count(self, count_id: int) -> None:
        """Delete a student count entry."""
        try:
            self.student_count_model.delete_student_count(count_id)
        except Exception as e:
            logger.error(f"Failed to delete student count: {e}")
            raise
    
    def get_all_student_counts(self) -> List[Dict[str, Any]]:
        """Get all student count entries."""
        try:
            return self.student_count_model.get_all_student_counts()
        except Exception as e:
            logger.error(f"Failed to get student counts: {e}")
            raise
    
    def delete_responses(self, res_ids: List[int]) -> int:
        """
        Delete responses by res_id.
        
        Args:
            res_ids: List of res_id values to delete
            
        Returns:
            Number of deleted records
        """
        try:
            return self.response_model.delete_responses(res_ids)
        except Exception as e:
            logger.error(f"Failed to delete responses: {e}")
            raise
    
    def get_maintenance_data(self, page: int = 1, per_page: int = 100) -> Dict[str, Any]:
        """
        Get data for maintenance view.
        
        Args:
            page: Page number (1-based)
            per_page: Records per page
            
        Returns:
            Dictionary with maintenance data
        """
        try:
            offset = (page - 1) * per_page
            
            # Get responses ordered by most recent first
            filters = {'order_by': 'res-id', 'order_direction': 'DESC'}
            responses = self.response_model.get_responses(filters=filters, limit=per_page, offset=offset)
            
            # Get orphaned responses
            orphaned = self.response_model.get_orphaned_responses()
            
            # Get student counts
            student_counts = self.get_all_student_counts()
            
            # Count total responses efficiently without loading all data
            with self.db_manager.get_connection() as conn:
                from sqlalchemy import select, func
                count_query = select(func.count()).select_from(self.db_manager.responses_table)
                total_responses = conn.execute(count_query).scalar()
            
            return {
                'responses': responses,
                'orphaned_responses': orphaned,
                'student_counts': student_counts,
                'pagination': {
                    'page': page,
                    'per_page': per_page,
                    'total': total_responses,
                    'pages': (total_responses + per_page - 1) // per_page
                }
            }
            
        except Exception as e:
            logger.error(f"Failed to get maintenance data: {e}")
            raise
    
    def _normalize_filters(self, filters: Dict[str, Any]) -> Dict[str, Any]:
        """
        Normalize and validate filter values.
        
        Args:
            filters: Raw filter dictionary
            
        Returns:
            Normalized filter dictionary
        """
        normalized = {}
        
        # Handle date filters
        if 'start_date' in filters:
            if isinstance(filters['start_date'], str):
                try:
                    normalized['start_date'] = datetime.strptime(filters['start_date'], '%Y-%m-%d').date()
                except ValueError:
                    logger.warning(f"Invalid start_date format: {filters['start_date']}")
            elif isinstance(filters['start_date'], date):
                normalized['start_date'] = filters['start_date']
        
        if 'end_date' in filters:
            if isinstance(filters['end_date'], str):
                try:
                    normalized['end_date'] = datetime.strptime(filters['end_date'], '%Y-%m-%d').date()
                except ValueError:
                    logger.warning(f"Invalid end_date format: {filters['end_date']}")
            elif isinstance(filters['end_date'], date):
                normalized['end_date'] = filters['end_date']
        
        # Set default date range to a wider range if not provided
        # Only set defaults for dashboard data, not for student list filtering
        if 'start_date' not in normalized or 'end_date' not in normalized:
            today = date.today()
            if 'start_date' not in normalized:
                # Use a wider date range to include more data
                normalized['start_date'] = today - timedelta(days=365*3)  # 3 years back
            if 'end_date' not in normalized:
                # Extend to future to include upcoming assessments
                normalized['end_date'] = today + timedelta(days=365)  # 1 year forward
        
        # Handle string filters
        string_filters = ['school', 'grade', 'teacher', 'assessment', 'student_name', 'domain']
        for filter_name in string_filters:
            if filter_name in filters and filters[filter_name]:
                normalized[filter_name] = str(filters[filter_name]).strip()
        
        return normalized
    
    def _convert_response_to_numeric(self, response_value: Any) -> float:
        """
        Convert response value to numeric score.
        Response values should already be numeric (0, 0.5, 1) from the database.
        
        Args:
            response_value: Response value (should be numeric)
            
        Returns:
            Numeric score value (0, 0.5, or 1)
        """
        # If already a number, return it
        if isinstance(response_value, (int, float)):
            return float(response_value)
        
        # Try to parse as number
        if isinstance(response_value, str):
            try:
                return float(response_value)
            except (ValueError, TypeError):
                # Default to 0 for invalid responses
                return 0.0
        
        # Default for any other type
        return 0.0
