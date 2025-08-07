"""
Application factory and initialization.
"""
import os
import logging
from flask import Flask
from typing import Optional

from .models import DatabaseManager, LayoutModel, ResponseModel
from .services import LayoutService
from .routes import dashboard_bp, layout_bp
from config import get_config


def create_app(config_name: str = None) -> Flask:
    """
    Create and configure Flask application.
    
    Args:
        config_name: Configuration environment name
        
    Returns:
        Configured Flask application
    """
    app = Flask(__name__, 
                template_folder='../templates',
                static_folder='../static')
    
    # Load configuration
    config_class = get_config(config_name)
    app.config.from_object(config_class)
    
    # Initialize configuration
    config_class.init_app(app)
    
    # Initialize logging
    _setup_logging(app)
    
    # Initialize database
    _initialize_database(app)
    
    # Initialize services
    _initialize_services(app)
    
    # Register blueprints
    _register_blueprints(app)
    
    # Register error handlers
    _register_error_handlers(app)
    
    # Setup security
    _setup_security(app)
    
    app.logger.info('KEF Application initialized successfully')
    return app


def _setup_logging(app: Flask) -> None:
    """Configure application logging."""
    if app.config.get('DEVELOPMENT'):
        # Development logging
        logging.basicConfig(
            level=logging.DEBUG,
            format='%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'
        )
    else:
        # Production logging
        if not os.path.exists('logs'):
            os.makedirs('logs')
        
        from logging.handlers import RotatingFileHandler
        file_handler = RotatingFileHandler(
            f'logs/{app.name}.log',
            maxBytes=10240000,
            backupCount=10
        )
        file_handler.setFormatter(logging.Formatter(
            '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'
        ))
        file_handler.setLevel(logging.INFO)
        app.logger.addHandler(file_handler)
        app.logger.setLevel(logging.INFO)


def _initialize_database(app: Flask) -> None:
    """Initialize database connection and models."""
    try:
        # Create database manager
        db_manager = DatabaseManager(
            database_url=app.config['DATABASE_URL'],
            engine_options=app.config.get('SQLALCHEMY_ENGINE_OPTIONS', {})
        )
        
        # Initialize database
        db_manager.initialize_database()
        
        # Store in app context
        app.db_manager = db_manager
        
        # Create model instances
        app.layout_model = LayoutModel(db_manager)
        app.response_model = ResponseModel(db_manager)
        
        app.logger.info('Database initialized successfully')
        
    except Exception as e:
        app.logger.error(f'Database initialization failed: {e}')
        raise


def _initialize_services(app: Flask) -> None:
    """Initialize service layer."""
    try:
        # Create service instances
        app.layout_service = LayoutService(app.layout_model)
        
        app.logger.info('Services initialized successfully')
        
    except Exception as e:
        app.logger.error(f'Service initialization failed: {e}')
        raise


def _register_blueprints(app: Flask) -> None:
    """Register Flask blueprints."""
    app.register_blueprint(dashboard_bp)
    app.register_blueprint(layout_bp)
    
    app.logger.info('Blueprints registered successfully')


def _register_error_handlers(app: Flask) -> None:
    """Register global error handlers."""
    
    @app.errorhandler(404)
    def not_found(error):
        return {'error': 'Not found'}, 404
    
    @app.errorhandler(500)
    def internal_error(error):
        app.logger.error(f'Internal error: {error}')
        return {'error': 'Internal server error'}, 500
    
    @app.errorhandler(Exception)
    def handle_exception(error):
        app.logger.error(f'Unhandled exception: {error}')
        return {'error': 'An unexpected error occurred'}, 500


def _setup_security(app: Flask) -> None:
    """Setup security configurations."""
    
    # Security headers
    @app.after_request
    def add_security_headers(response):
        response.headers['X-Content-Type-Options'] = 'nosniff'
        response.headers['X-Frame-Options'] = 'DENY'
        response.headers['X-XSS-Protection'] = '1; mode=block'
        
        if app.config.get('SESSION_COOKIE_SECURE'):
            response.headers['Strict-Transport-Security'] = 'max-age=31536000; includeSubDomains'
        
        return response
    
    # CSRF setup would go here if using Flask-WTF
    # Rate limiting setup would go here if using Flask-Limiter
    
    app.logger.info('Security configurations applied')


def _setup_extensions(app: Flask) -> None:
    """Setup Flask extensions (if any)."""
    # This is where you would initialize extensions like:
    # - Flask-WTF for CSRF protection
    # - Flask-Limiter for rate limiting
    # - Flask-CORS for CORS handling
    # - Flask-Cache for caching
    pass
