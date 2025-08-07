"""
Main application entry point.
"""
import os
from app import create_app
from config import get_config

# Create Flask application
config_name = os.environ.get('FLASK_ENV', 'development')
app = create_app(config_name)

if __name__ == '__main__':
    # Development server configuration
    debug_mode = app.config.get('DEBUG', False)
    host = os.environ.get('FLASK_HOST', '0.0.0.0')
    port = int(os.environ.get('FLASK_PORT', 5000))
    
    app.logger.info(f'Starting KEF application in {config_name} mode')
    app.logger.info(f'Debug mode: {debug_mode}')
    app.logger.info(f'Server: {host}:{port}')
    
    app.run(
        debug=debug_mode,
        host=host,
        port=port,
        threaded=True
    )
