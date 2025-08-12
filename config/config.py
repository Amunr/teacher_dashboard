"""
Application configuration classes and settings.
"""
import os
from typing import Type
from dotenv import load_dotenv

# Load environment variables from .env file if it exists
load_dotenv()


class Config:
    """Base configuration class with common settings."""
    
    # Flask settings
    SECRET_KEY: str = os.environ.get('SECRET_KEY') or 'dev-key-change-in-production'
    
    # Database settings
    DATABASE_URL: str = os.environ.get('DATABASE_URL') or 'sqlite:///data.db'
    SQLALCHEMY_TRACK_MODIFICATIONS: bool = False
    SQLALCHEMY_ENGINE_OPTIONS = {
        'pool_pre_ping': True,
        'pool_recycle': 300,
        'connect_args': {
            'check_same_thread': False,
            'timeout': 20
        }
    }
    
    # Security settings
    WTF_CSRF_ENABLED: bool = True
    WTF_CSRF_TIME_LIMIT: int = 3600  # 1 hour
    
    # Session settings
    SESSION_COOKIE_SECURE: bool = False  # Set to True in production with HTTPS
    SESSION_COOKIE_HTTPONLY: bool = True
    SESSION_COOKIE_SAMESITE: str = 'Lax'
    PERMANENT_SESSION_LIFETIME: int = 1800  # 30 minutes
    
    # Rate limiting
    RATELIMIT_STORAGE_URL: str = os.environ.get('REDIS_URL') or 'memory://'
    RATELIMIT_DEFAULT: str = "200 per day, 50 per hour"
    
    # Application settings
    MAX_CONTENT_LENGTH: int = 16 * 1024 * 1024  # 16MB max file size
    JSONIFY_PRETTYPRINT_REGULAR: bool = False
    
    # Logging
    LOG_LEVEL: str = os.environ.get('LOG_LEVEL') or 'INFO'
    LOG_FILE: str = os.environ.get('LOG_FILE') or 'app.log'
    
    @staticmethod
    def init_app(app) -> None:
        """Initialize the Flask application with this configuration."""
        pass


class DevelopmentConfig(Config):
    """Development environment configuration."""
    
    DEBUG: bool = True
    DEVELOPMENT: bool = True
    
    # Database
    DATABASE_URL: str = os.environ.get('DEV_DATABASE_URL') or 'sqlite:///data.db'
    
    # Security (relaxed for development)
    WTF_CSRF_ENABLED: bool = False
    SESSION_COOKIE_SECURE: bool = False
    
    # Logging
    LOG_LEVEL: str = 'DEBUG'
    
    @staticmethod
    def init_app(app) -> None:
        """Initialize development-specific settings."""
        import logging
        logging.basicConfig(level=logging.DEBUG)


class ProductionConfig(Config):
    """Production environment configuration."""
    
    DEBUG: bool = False
    DEVELOPMENT: bool = False
    
    # Security (strict for production)
    SESSION_COOKIE_SECURE: bool = True
    WTF_CSRF_ENABLED: bool = True
    
    # Database connection pooling for production
    SQLALCHEMY_ENGINE_OPTIONS = {
        'pool_size': 10,
        'pool_timeout': 20,
        'pool_recycle': 3600,
        'pool_pre_ping': True,
        'max_overflow': 20
    }
    
    @staticmethod
    def init_app(app) -> None:
        """Initialize production-specific settings."""
        import logging
        from logging.handlers import RotatingFileHandler
        
        # File logging
        if not os.path.exists('logs'):
            os.mkdir('logs')
        
        file_handler = RotatingFileHandler(
            'logs/kef_app.log', 
            maxBytes=10240000, 
            backupCount=10
        )
        file_handler.setFormatter(logging.Formatter(
            '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'
        ))
        file_handler.setLevel(logging.INFO)
        app.logger.addHandler(file_handler)
        app.logger.setLevel(logging.INFO)
        app.logger.info('KEF Application startup')


class TestingConfig(Config):
    """Testing environment configuration."""
    
    TESTING: bool = True
    WTF_CSRF_ENABLED: bool = False
    DATABASE_URL: str = 'sqlite:///:memory:'
    
    @staticmethod
    def init_app(app) -> None:
        """Initialize testing-specific settings."""
        import logging
        logging.disable(logging.CRITICAL)


# Configuration mapping
config_map = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}


def get_config(config_name: str = None) -> Type[Config]:
    """
    Get configuration class based on environment.
    
    Args:
        config_name: Configuration environment name
        
    Returns:
        Configuration class
    """
    if config_name is None:
        config_name = os.environ.get('FLASK_ENV', 'default')
    
    return config_map.get(config_name, DevelopmentConfig)
