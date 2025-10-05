"""
Main application entry point.
"""
import os
from app import create_app

# Create Flask application
config_name = os.environ.get('FLASK_ENV', 'production')
app = create_app(config_name)

if __name__ == '__main__':
    # Server configuration
    host = os.environ.get('FLASK_HOST', '0.0.0.0')
    port = int(os.environ.get('FLASK_PORT', 5000))
    
    app.logger.info(f'Starting KEF Teacher Dashboard in {config_name} mode')
    app.logger.info(f'Server: {host}:{port}')
    
    app.run(
        host=host,
        port=port,
        threaded=True
    )
