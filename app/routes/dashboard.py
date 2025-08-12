"""
Dashboard and main application routes.
"""
from flask import Blueprint, render_template, current_app, request, jsonify, send_from_directory
from typing import Dict, Any
import logging
from datetime import date, datetime, timedelta
import os

from ..services import LayoutService, DashboardService
from ..services.sheets_service import SheetsManagementService
from ..utils import log_operation

logger = logging.getLogger(__name__)
dashboard_bp = Blueprint('dashboard', __name__)


@dashboard_bp.route('/test')
def test_dashboard():
    """Test dashboard page."""
    return send_from_directory('.', 'test_dashboard.html')


@dashboard_bp.route('/debug')
def debug_dashboard():
    """Debug dashboard page."""
    return render_template('debug_dashboard.html')


@dashboard_bp.route('/')
def home() -> str:
    """
    Render the main dashboard homepage.
    
    Returns:
        Rendered homepage template
    """
    try:
        log_operation('dashboard_home_accessed')
        
        # Get initial dashboard data for server-side rendering
        dashboard_service = DashboardService(current_app.db_manager)
        filters = {
            'start_date': datetime.now() - timedelta(days=365),
            'end_date': datetime.now()
        }
        initial_data = dashboard_service.get_dashboard_data(filters)
        current_app.logger.info(f"Initial data keys: {list(initial_data.keys()) if initial_data else 'None'}")
        
        return render_template('homepage.html', initial_data=initial_data)
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


# Google Sheets Integration API Routes

@dashboard_bp.route('/api/sheets/config', methods=['GET'])
def get_sheets_config():
    """Get current Google Sheets configuration."""
    try:
        sheets_service = SheetsManagementService(current_app.db_manager)
        config = sheets_service.get_config()
        
        if config:
            # Don't expose sensitive data, just the essentials
            safe_config = {
                'sheet_url': config['sheet_url'],
                'poll_interval': config['poll_interval'],
                'last_row_processed': config['last_row_processed'],
                'is_active': config['is_active'],
                'updated_at': str(config['updated_at'])
            }
            return jsonify(safe_config)
        else:
            return jsonify({'configured': False})
            
    except Exception as e:
        logger.error(f"Failed to get sheets config: {e}")
        return jsonify({'error': str(e)}), 500


@dashboard_bp.route('/api/sheets/config', methods=['POST'])
def update_sheets_config():
    """Update Google Sheets configuration."""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        sheet_url = data.get('sheet_url', '').strip()
        poll_interval = data.get('poll_interval', 30)
        
        if not sheet_url:
            return jsonify({'error': 'Sheet URL is required'}), 400
        
        try:
            poll_interval = int(poll_interval)
            if poll_interval < 1:
                return jsonify({'error': 'Poll interval must be at least 1 minute'}), 400
        except (ValueError, TypeError):
            return jsonify({'error': 'Poll interval must be a valid number'}), 400
        
        sheets_service = SheetsManagementService(current_app.db_manager)
        result = sheets_service.update_config(sheet_url, poll_interval)
        
        if result['success']:
            log_operation('sheets_config_updated', {'sheet_url': sheet_url, 'poll_interval': poll_interval})
            return jsonify(result)
        else:
            return jsonify(result), 400
            
    except Exception as e:
        logger.error(f"Failed to update sheets config: {e}")
        return jsonify({'error': str(e)}), 500


@dashboard_bp.route('/api/sheets/test', methods=['POST'])
def test_sheets_connection():
    """Test connection to a Google Sheet."""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        sheet_url = data.get('sheet_url', '').strip()
        
        if not sheet_url:
            return jsonify({'error': 'Sheet URL is required'}), 400
        
        sheets_service = SheetsManagementService(current_app.db_manager)
        result = sheets_service.test_sheet_connection(sheet_url)
        
        return jsonify(result)
        
    except Exception as e:
        logger.error(f"Failed to test sheet connection: {e}")
        return jsonify({'error': str(e)}), 500


@dashboard_bp.route('/api/sheets/stats', methods=['GET'])
def get_sheets_stats():
    """Get Google Sheets import statistics."""
    try:
        sheets_service = SheetsManagementService(current_app.db_manager)
        stats = sheets_service.get_import_stats()
        return jsonify(stats)
        
    except Exception as e:
        logger.error(f"Failed to get sheets stats: {e}")
        return jsonify({'error': str(e)}), 500


@dashboard_bp.route('/api/sheets/deactivate', methods=['POST'])
def deactivate_sheets_config():
    """Deactivate Google Sheets configuration."""
    try:
        sheets_service = SheetsManagementService(current_app.db_manager)
        result = sheets_service.deactivate_config()
        
        if result['success']:
            log_operation('sheets_config_deactivated')
        
        return jsonify(result)
        
    except Exception as e:
        logger.error(f"Failed to deactivate sheets config: {e}")
        return jsonify({'error': str(e)}), 500


@dashboard_bp.route('/api/sheets/failed-imports', methods=['GET'])
def get_failed_imports():
    """Get list of failed imports."""
    try:
        sheets_service = SheetsManagementService(current_app.db_manager)
        failed_imports = sheets_service.get_failed_imports()
        return jsonify({'failed_imports': failed_imports})
        
    except Exception as e:
        logger.error(f"Failed to get failed imports: {e}")
        return jsonify({'error': str(e)}), 500


@dashboard_bp.route('/api/sheets/failed-imports/<int:failed_import_id>/retry', methods=['POST'])
def retry_failed_import(failed_import_id: int):
    """Retry a specific failed import."""
    try:
        sheets_service = SheetsManagementService(current_app.db_manager)
        result = sheets_service.retry_failed_import(failed_import_id)
        
        if result['success']:
            log_operation('failed_import_retried', {'failed_import_id': failed_import_id, 'res_id': result.get('res_id')})
        
        return jsonify(result)
        
    except Exception as e:
        logger.error(f"Failed to retry import {failed_import_id}: {e}")
        return jsonify({'error': str(e)}), 500


@dashboard_bp.route('/api/sheets/failed-imports/<int:failed_import_id>', methods=['DELETE'])
def delete_failed_import(failed_import_id: int):
    """Delete a failed import record."""
    try:
        sheets_service = SheetsManagementService(current_app.db_manager)
        result = sheets_service.delete_failed_import(failed_import_id)
        
        if result['success']:
            log_operation('failed_import_deleted', {'failed_import_id': failed_import_id})
        
        return jsonify(result)
        
    except Exception as e:
        logger.error(f"Failed to delete failed import {failed_import_id}: {e}")
        return jsonify({'error': str(e)}), 500


@dashboard_bp.route('/api/sheets/import', methods=['POST'])
def manual_import():
    """Trigger a manual import from Google Sheets"""
    try:
        sheets_service = SheetsManagementService(current_app.db_manager)
        result = sheets_service.manual_import()
        
        if result['success']:
            log_operation('manual_import_triggered', {'processed_rows': result.get('processed_rows', 0)})
        
        return jsonify(result)
        
    except Exception as e:
        logger.error(f"Error during manual import: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500


@dashboard_bp.route('/api/sheets/retry-failed', methods=['POST'])
def retry_all_failed():
    """Retry all failed imports"""
    try:
        sheets_service = SheetsManagementService(current_app.db_manager)
        result = sheets_service.retry_all_failed_imports()
        
        if result['success']:
            log_operation('retry_all_failed', {'retried_count': result.get('retried_count', 0)})
        
        return jsonify(result)
        
    except Exception as e:
        logger.error(f"Error retrying failed imports: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500


@dashboard_bp.route('/api/sheets/retry-failed/<int:failed_import_id>', methods=['POST'])
def retry_single_failed(failed_import_id):
    """Retry a specific failed import"""
    try:
        sheets_service = SheetsManagementService(current_app.db_manager)
        result = sheets_service.retry_failed_import(failed_import_id)
        
        if result['success']:
            log_operation('retry_failed_import', {'failed_import_id': failed_import_id})
        
        return jsonify(result)
        
    except Exception as e:
        logger.error(f"Error retrying failed import {failed_import_id}: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500


@dashboard_bp.route('/api/sheets/failed-imports', methods=['DELETE'])
def delete_all_failed_imports():
    """Delete all failed import records"""
    try:
        sheets_service = SheetsManagementService(current_app.db_manager)
        result = sheets_service.delete_all_failed_imports()
        
        if result['success']:
            log_operation('delete_all_failed_imports', {'deleted_count': result.get('deleted_count', 0)})
        
        return jsonify(result)
        
    except Exception as e:
        logger.error(f"Error deleting all failed imports: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500


@dashboard_bp.errorhandler(404)
def not_found(error) -> str:
    """Handle 404 errors."""
    return render_template('error.html', message="Page not found"), 404


@dashboard_bp.errorhandler(500)
def internal_error(error) -> str:
    """Handle 500 errors."""
    logger.error(f"Internal server error: {error}")
    return render_template('error.html', message="Internal server error"), 500


@dashboard_bp.route('/api/sheets/service/start', methods=['POST'])
def start_sheets_service():
    """Start the sheets polling service"""
    try:
        import subprocess
        import os
        import platform
        
        # Get the config to determine polling interval
        sheets_service = SheetsManagementService(current_app.db_manager)
        config = sheets_service.get_config()
        poll_interval = config.get('poll_interval', 2) if config else 2  # Default to 2 minutes as user requested
        
        # Convert minutes to seconds for the poller
        interval_seconds = poll_interval * 60
        
        # Get the path to the poller.py script (FIXED: use poller.py instead of sheets_poller.py)
        script_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'poller.py')
        
        # Use virtual environment Python if available
        venv_python = os.path.join(os.path.dirname(script_path), 'venv', 'Scripts', 'python.exe')
        python_cmd = venv_python if os.path.exists(venv_python) else 'python'
        
        # Start the service in background with specified interval
        process = subprocess.Popen(
            [python_cmd, script_path, '--interval', str(interval_seconds)],
            cwd=os.path.dirname(script_path),
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            creationflags=subprocess.CREATE_NO_WINDOW if platform.system() == "Windows" else 0
        )
        
        logger.info(f"Started sheets service with PID: {process.pid}, interval: {poll_interval} minutes")
        return jsonify({
            'success': True,
            'message': f'Sheets service started with PID: {process.pid}, polling every {poll_interval} minutes',
            'pid': process.pid,
            'poll_interval': poll_interval
        })
        
    except Exception as e:
        logger.error(f"Failed to start sheets service: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@dashboard_bp.route('/api/sheets/service/stop', methods=['POST'])
def stop_sheets_service():
    """Stop the sheets polling service"""
    try:
        import psutil
        import os
        
        # Find poller.py processes (FIXED: look for poller.py instead of sheets_poller.py)
        stopped_count = 0
        for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
            try:
                if proc.info['cmdline'] and 'poller.py' in ' '.join(proc.info['cmdline']):
                    proc.terminate()
                    stopped_count += 1
                    logger.info(f"Terminated sheets service process {proc.info['pid']}")
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue
        
        if stopped_count > 0:
            return jsonify({
                'success': True,
                'message': f'Stopped {stopped_count} sheets service process(es)'
            })
        else:
            return jsonify({
                'success': True,
                'message': 'No sheets service processes found running'
            })
            
    except ImportError:
        # Fallback if psutil not available
        return jsonify({
            'success': False,
            'error': 'psutil package required for service management'
        }), 500
    except Exception as e:
        logger.error(f"Failed to stop sheets service: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@dashboard_bp.route('/api/sheets/service/status', methods=['GET'])
def get_sheets_service_status():
    """Get the status of the sheets polling service with detailed timing info"""
    try:
        import psutil
        import time
        from datetime import datetime, timedelta
        
        # Get config to determine polling interval
        sheets_service = SheetsManagementService(current_app.db_manager)
        config = sheets_service.get_config()
        poll_interval_minutes = config.get('poll_interval', 2) if config else 2
        
        # Find poller.py processes (FIXED: look for poller.py instead of sheets_poller.py)
        running_processes = []
        for proc in psutil.process_iter(['pid', 'name', 'cmdline', 'create_time']):
            try:
                if proc.info['cmdline'] and 'poller.py' in ' '.join(proc.info['cmdline']):
                    start_time = datetime.fromtimestamp(proc.info['create_time'])
                    current_time = datetime.now()
                    
                    # Calculate next run time based on polling interval
                    elapsed_time = current_time - start_time
                    total_seconds_elapsed = elapsed_time.total_seconds()
                    interval_seconds = poll_interval_minutes * 60
                    
                    # Calculate how many cycles have completed
                    cycles_completed = int(total_seconds_elapsed // interval_seconds)
                    next_cycle_start = start_time + timedelta(seconds=(cycles_completed + 1) * interval_seconds)
                    
                    # Calculate time until next run
                    time_until_next = next_cycle_start - current_time
                    minutes_until_next = max(0, int(time_until_next.total_seconds() / 60))
                    
                    running_processes.append({
                        'pid': proc.info['pid'],
                        'started': proc.info['create_time'],
                        'started_formatted': start_time.strftime('%Y-%m-%d %H:%M:%S'),
                        'uptime_minutes': int(elapsed_time.total_seconds() / 60),
                        'poll_interval_minutes': poll_interval_minutes,
                        'cycles_completed': cycles_completed,
                        'next_run': next_cycle_start.strftime('%Y-%m-%d %H:%M:%S'),
                        'minutes_until_next_run': minutes_until_next
                    })
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue
        
        is_running = len(running_processes) > 0
        status_message = f"Service is {'running' if is_running else 'stopped'}"
        
        if is_running:
            proc = running_processes[0]  # Get first process info
            status_message += f" - next run in {proc['minutes_until_next_run']} minutes"
        
        return jsonify({
            'success': True,
            'running': is_running,
            'processes': running_processes,
            'count': len(running_processes),
            'status_message': status_message,
            'poll_interval_minutes': poll_interval_minutes
        })
        
    except ImportError:
        # Fallback if psutil not available
        return jsonify({
            'success': False,
            'error': 'psutil package required for service status'
        }), 500
    except Exception as e:
        logger.error(f"Failed to get sheets service status: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@dashboard_bp.route('/api/sheets/config/status', methods=['GET'])
def get_sheets_config_status():
    """Get configuration status for maintenance UI"""
    try:
        sheets_service = SheetsManagementService(current_app.db_manager)
        config = sheets_service.get_config()
        
        if config:
            return jsonify({
                'configured': True,
                'active': config.get('is_active', False),
                'sheet_url': config.get('sheet_url', ''),
                'poll_interval': config.get('poll_interval', 30),
                'last_row_processed': config.get('last_row_processed', 0)
            })
        else:
            return jsonify({
                'configured': False,
                'active': False
            })
            
    except Exception as e:
        logger.error(f"Failed to get config status: {e}")
        return jsonify({'error': str(e)}), 500


@dashboard_bp.route('/api/sheets/service/detailed-status', methods=['GET'])
def get_detailed_service_status():
    """Get detailed service status including next run time from status file"""
    try:
        import json
        import os
        from datetime import datetime
        
        # Try to read status file created by poller
        status_file = 'poller_status.json'
        status_data = {}
        
        if os.path.exists(status_file):
            try:
                with open(status_file, 'r') as f:
                    status_data = json.load(f)
            except:
                pass
        
        # Also check if process is actually running
        import psutil
        process_running = False
        running_pid = None
        
        for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
            try:
                if proc.info['cmdline'] and 'poller.py' in ' '.join(proc.info['cmdline']):
                    process_running = True
                    running_pid = proc.info['pid']
                    break
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue
        
        # Calculate time until next run if we have status data
        minutes_until_next = None
        next_run_formatted = None
        
        if status_data.get('next_run_time'):
            try:
                next_run = datetime.fromisoformat(status_data['next_run_time'].replace('Z', '+00:00'))
                current_time = datetime.now()
                time_diff = next_run - current_time
                minutes_until_next = max(0, int(time_diff.total_seconds() / 60))
                next_run_formatted = next_run.strftime('%H:%M:%S')
            except:
                pass
        
        # Get config for poll interval
        sheets_service = SheetsManagementService(current_app.db_manager)
        config = sheets_service.get_config()
        poll_interval = config.get('poll_interval', 2) if config else 2
        
        result = {
            'success': True,
            'process_running': process_running,
            'running_pid': running_pid,
            'poll_interval_minutes': poll_interval,
            'status_file_exists': os.path.exists(status_file),
            'minutes_until_next_run': minutes_until_next,
            'next_run_time': next_run_formatted,
            'status_data': status_data
        }
        
        # Create status message
        if process_running:
            if minutes_until_next is not None:
                result['status_message'] = f"Running - next poll in {minutes_until_next} minutes at {next_run_formatted}"
            else:
                result['status_message'] = f"Running - polling every {poll_interval} minutes"
        else:
            result['status_message'] = "Stopped"
        
        return jsonify(result)
        
    except Exception as e:
        logger.error(f"Failed to get detailed service status: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@dashboard_bp.route('/api/sheets/test-connection', methods=['GET'])
def test_connection():
    """Test connection to configured Google Sheet"""
    try:
        sheets_service = SheetsManagementService(current_app.db_manager)
        config = sheets_service.get_config()
        
        if not config or not config.get('sheet_url'):
            return jsonify({
                'success': False,
                'error': 'No sheet configured'
            }), 400
        
        result = sheets_service.test_sheet_connection(config['sheet_url'])
        return jsonify(result)
        
    except Exception as e:
        logger.error(f"Failed to test connection: {e}")
        return jsonify({'error': str(e)}), 500


@dashboard_bp.route('/api/sheets/config/last-row', methods=['POST'])
def set_config_last_row():
    """Set the last processed row in config"""
    try:
        data = request.get_json()
        if not data or 'last_row' not in data:
            return jsonify({
                'success': False,
                'error': 'last_row is required'
            }), 400
        
        last_row = int(data['last_row'])
        if last_row < 1:
            return jsonify({
                'success': False,
                'error': 'last_row must be at least 1 (to protect header row)'
            }), 400
        
        # Update the configuration
        sheets_service = SheetsManagementService(current_app.db_manager)
        result = sheets_service.update_last_processed_row(last_row)
        
        if result['success']:
            logger.info(f"Set last processed row to {last_row}")
            return jsonify({
                'success': True,
                'message': f'Last processed row set to {last_row}'
            })
        else:
            return jsonify({
                'success': False,
                'error': result.get('error', 'Failed to update last processed row')
            }), 500
            
    except ValueError:
        return jsonify({
            'success': False,
            'error': 'last_row must be a valid integer'
        }), 400
    except Exception as e:
        logger.error(f"Failed to set last processed row: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@dashboard_bp.route('/api/sheets/set-last-row', methods=['POST'])
def set_last_row():
    """Manually set the last processed row for testing"""
    try:
        data = request.get_json()
        if not data or 'row_number' not in data:
            return jsonify({
                'success': False,
                'error': 'row_number is required'
            }), 400
        
        row_number = int(data['row_number'])
        if row_number < 0:
            return jsonify({
                'success': False,
                'error': 'row_number must be non-negative'
            }), 400
        
        # Update the configuration
        config_service = SheetsManagementService(current_app.db_manager)
        result = config_service.update_last_processed_row(row_number)
        
        if result['success']:
            logger.info(f"Manually set last processed row to {row_number}")
            return jsonify({
                'success': True,
                'message': f'Last processed row set to {row_number}'
            })
        else:
            return jsonify({
                'success': False,
                'error': result.get('error', 'Failed to update last processed row')
            }), 500
            
    except ValueError:
        return jsonify({
            'success': False,
            'error': 'row_number must be a valid integer'
        }), 400
    except Exception as e:
        logger.error(f"Failed to set last processed row: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500
