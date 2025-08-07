"""
Dashboard and main application routes.
"""
from flask import Blueprint, render_template, current_app, request, jsonify
from typing import Dict, Any
import logging
from datetime import date, datetime

from ..services import LayoutService, DashboardService
from ..utils import log_operation

logger = logging.getLogger(__name__)
dashboard_bp = Blueprint('dashboard', __name__)


@dashboard_bp.route('/')
def home() -> str:
    """
    Render the main dashboard homepage.
    
    Returns:
        Rendered homepage template
    """
    try:
        log_operation('dashboard_home_accessed')
        return render_template('homepage.html')
    except Exception as e:
        logger.error(f"Error rendering homepage: {e}")
        current_app.logger.error(f"Homepage error: {e}")
        return render_template('error.html', message="Failed to load dashboard"), 500


@dashboard_bp.route('/api/dashboard-data')
def get_dashboard_data() -> Dict[str, Any]:
    """
    API endpoint to get dashboard data with filtering.
    
    Returns:
        JSON response with dashboard metrics and charts data
    """
    try:
        dashboard_service = DashboardService(current_app.db_manager)
        
        # Extract filters from query parameters
        filters = {}
        if request.args.get('school'):
            filters['school'] = request.args.get('school')
        if request.args.get('grade'):
            filters['grade'] = request.args.get('grade')
        if request.args.get('teacher'):
            filters['teacher'] = request.args.get('teacher')
        if request.args.get('assessment'):
            filters['assessment'] = request.args.get('assessment')
        if request.args.get('student_name'):
            filters['student_name'] = request.args.get('student_name')
        if request.args.get('domain'):
            filters['domain'] = request.args.get('domain')
        if request.args.get('start_date'):
            filters['start_date'] = request.args.get('start_date')
        if request.args.get('end_date'):
            filters['end_date'] = request.args.get('end_date')
        
        data = dashboard_service.get_dashboard_data(filters)
        return jsonify(data)
        
    except Exception as e:
        logger.error(f"Error getting dashboard data: {e}")
        return jsonify({'error': str(e)}), 500


@dashboard_bp.route('/api/student-list')
def get_student_list() -> Dict[str, Any]:
    """
    API endpoint to get paginated student list with scores.
    
    Returns:
        JSON response with student data and pagination info
    """
    try:
        dashboard_service = DashboardService(current_app.db_manager)
        
        # Extract pagination parameters
        page = int(request.args.get('page', 1))
        per_page = int(request.args.get('per_page', 50))
        
        # Extract filters from query parameters
        filters = {}
        for filter_name in ['school', 'grade', 'teacher', 'assessment', 'student_name', 'domain', 'start_date', 'end_date']:
            if request.args.get(filter_name):
                filters[filter_name] = request.args.get(filter_name)
        
        data = dashboard_service.get_student_list(filters, page, per_page)
        return jsonify(data)
        
    except Exception as e:
        logger.error(f"Error getting student list: {e}")
        return jsonify({'error': str(e)}), 500


@dashboard_bp.route('/maintenance')
def maintenance() -> str:
    """
    Render the maintenance view for managing responses and student counts.
    
    Returns:
        Rendered maintenance template
    """
    try:
        log_operation('maintenance_accessed')
        dashboard_service = DashboardService(current_app.db_manager)
        
        page = int(request.args.get('page', 1))
        data = dashboard_service.get_maintenance_data(page=page)
        
        return render_template('maintenance.html', **data)
        
    except Exception as e:
        logger.error(f"Error rendering maintenance page: {e}")
        return render_template('error.html', message="Failed to load maintenance page"), 500


@dashboard_bp.route('/api/maintenance/delete-responses', methods=['POST'])
def delete_responses() -> Dict[str, Any]:
    """
    API endpoint to delete responses by res_id.
    
    Returns:
        JSON response with deletion status
    """
    try:
        dashboard_service = DashboardService(current_app.db_manager)
        data = request.get_json()
        
        if not data or 'res_ids' not in data:
            return jsonify({'error': 'res_ids required'}), 400
        
        res_ids = data['res_ids']
        if not isinstance(res_ids, list) or not res_ids:
            return jsonify({'error': 'res_ids must be a non-empty list'}), 400
        
        deleted_count = dashboard_service.delete_responses(res_ids)
        
        return jsonify({
            'success': True,
            'deleted_count': deleted_count,
            'message': f'Deleted {deleted_count} response records'
        })
        
    except Exception as e:
        logger.error(f"Error deleting responses: {e}")
        return jsonify({'error': str(e)}), 500


@dashboard_bp.route('/api/maintenance/student-counts', methods=['GET'])
def get_student_counts() -> Dict[str, Any]:
    """
    API endpoint to get all student count entries.
    
    Returns:
        JSON response with student counts
    """
    try:
        dashboard_service = DashboardService(current_app.db_manager)
        counts = dashboard_service.get_all_student_counts()
        return jsonify(counts)
        
    except Exception as e:
        logger.error(f"Error getting student counts: {e}")
        return jsonify({'error': str(e)}), 500


@dashboard_bp.route('/api/maintenance/student-counts', methods=['POST'])
def create_student_count() -> Dict[str, Any]:
    """
    API endpoint to create a new student count entry.
    
    Returns:
        JSON response with creation status
    """
    try:
        dashboard_service = DashboardService(current_app.db_manager)
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'Request data required'}), 400
        
        required_fields = ['start_date', 'end_date', 'total_students']
        for field in required_fields:
            if field not in data:
                return jsonify({'error': f'{field} is required'}), 400
        
        start_date = datetime.strptime(data['start_date'], '%Y-%m-%d').date()
        end_date = datetime.strptime(data['end_date'], '%Y-%m-%d').date()
        total_students = int(data['total_students'])
        description = data.get('description', '')
        
        count_id = dashboard_service.create_student_count(
            start_date, end_date, total_students, description
        )
        
        return jsonify({
            'success': True,
            'id': count_id,
            'message': 'Student count created successfully'
        })
        
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        logger.error(f"Error creating student count: {e}")
        return jsonify({'error': str(e)}), 500


@dashboard_bp.route('/api/maintenance/student-counts/<int:count_id>', methods=['PUT'])
def update_student_count(count_id: int) -> Dict[str, Any]:
    """
    API endpoint to update a student count entry.
    
    Args:
        count_id: ID of the student count to update
        
    Returns:
        JSON response with update status
    """
    try:
        dashboard_service = DashboardService(current_app.db_manager)
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'Request data required'}), 400
        
        required_fields = ['start_date', 'end_date', 'total_students']
        for field in required_fields:
            if field not in data:
                return jsonify({'error': f'{field} is required'}), 400
        
        start_date = datetime.strptime(data['start_date'], '%Y-%m-%d').date()
        end_date = datetime.strptime(data['end_date'], '%Y-%m-%d').date()
        total_students = int(data['total_students'])
        description = data.get('description', '')
        
        dashboard_service.update_student_count(
            count_id, start_date, end_date, total_students, description
        )
        
        return jsonify({
            'success': True,
            'message': 'Student count updated successfully'
        })
        
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        logger.error(f"Error updating student count: {e}")
        return jsonify({'error': str(e)}), 500


@dashboard_bp.route('/api/maintenance/student-counts/<int:count_id>', methods=['DELETE'])
def delete_student_count(count_id: int) -> Dict[str, Any]:
    """
    API endpoint to delete a student count entry.
    
    Args:
        count_id: ID of the student count to delete
        
    Returns:
        JSON response with deletion status
    """
    try:
        dashboard_service = DashboardService(current_app.db_manager)
        dashboard_service.delete_student_count(count_id)
        
        return jsonify({
            'success': True,
            'message': 'Student count deleted successfully'
        })
        
    except Exception as e:
        logger.error(f"Error deleting student count: {e}")
        return jsonify({'error': str(e)}), 500


@dashboard_bp.route('/health')
def health_check() -> Dict[str, Any]:
    """
    Health check endpoint for monitoring.
    
    Returns:
        JSON response with health status
    """
    try:
        # Check database connectivity
        db_healthy = current_app.db_manager.health_check()
        
        status = {
            'status': 'healthy' if db_healthy else 'unhealthy',
            'database': 'connected' if db_healthy else 'disconnected',
            'version': '1.0.0'
        }
        
        return status, 200 if db_healthy else 503
        
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return {
            'status': 'unhealthy',
            'error': str(e)
        }, 503


@dashboard_bp.errorhandler(404)
def not_found(error) -> str:
    """Handle 404 errors."""
    return render_template('error.html', message="Page not found"), 404


@dashboard_bp.errorhandler(500)
def internal_error(error) -> str:
    """Handle 500 errors."""
    logger.error(f"Internal server error: {error}")
    return render_template('error.html', message="Internal server error"), 500
