"""
Dashboard and main application routes.
"""
from flask import Blueprint, render_template, current_app
from typing import Dict, Any
import logging

from ..services import LayoutService
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
