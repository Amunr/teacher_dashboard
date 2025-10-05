"""
Production validation script for KEF Teacher Dashboard.
Run this script to verify the production setup is working correctly.
"""
import os
import sys
import requests
import time
from pathlib import Path

def check_environment():
    """Check environment configuration."""
    print("🔍 Checking environment configuration...")
    
    env_file = Path('.env')
    if not env_file.exists():
        print("❌ .env file not found. Copy .env.example to .env and configure it.")
        return False
    
    # Check for secret key
    with open(env_file) as f:
        content = f.read()
        if 'change-this-to-a-secure-random-key' in content:
            print("⚠️  WARNING: Default SECRET_KEY detected. Please set a secure key in .env")
            return False
    
    print("✅ Environment configuration looks good")
    return True

def check_database():
    """Check database connectivity."""
    print("🔍 Checking database...")
    
    try:
        from app import create_app
        app = create_app('production')
        
        with app.app_context():
            # Check if database is accessible
            result = app.db_manager.health_check()
            if result:
                print("✅ Database connection successful")
                return True
            else:
                print("❌ Database connection failed")
                return False
                
    except Exception as e:
        print(f"❌ Database check failed: {e}")
        return False

def check_application_start():
    """Check if application starts without errors."""
    print("🔍 Checking application startup...")
    
    try:
        from app import create_app
        app = create_app('production')
        
        # Check if app initializes without errors
        if app:
            print("✅ Application initializes successfully")
            
            # Check if debug mode is off
            if app.debug:
                print("⚠️  WARNING: Debug mode is enabled in production config")
                return False
            else:
                print("✅ Debug mode is disabled")
            
            return True
        else:
            print("❌ Application failed to initialize")
            return False
            
    except Exception as e:
        print(f"❌ Application startup failed: {e}")
        return False

def check_dependencies():
    """Check if all required dependencies are installed."""
    print("🔍 Checking dependencies...")
    
    required_packages = [
        'flask',
        'flask_sqlalchemy',
        'flask_cors',
        'flask_wtf',
        'flask_limiter',
        'python_dotenv',
        'sqlalchemy',
        'werkzeug',
        'jinja2',
        'requests'
    ]
    
    missing_packages = []
    
    for package in required_packages:
        try:
            __import__(package)
        except ImportError:
            # Try alternative import names
            alt_names = {
                'flask_sqlalchemy': 'flask_sqlalchemy',
                'flask_cors': 'flask_cors',
                'flask_wtf': 'flask_wtf',
                'flask_limiter': 'flask_limiter',
                'python_dotenv': 'dotenv'
            }
            
            if package in alt_names:
                try:
                    __import__(alt_names[package])
                    continue
                except ImportError:
                    pass
            
            missing_packages.append(package)
    
    if missing_packages:
        print(f"❌ Missing packages: {', '.join(missing_packages)}")
        print("Run: pip install -r requirements.txt")
        return False
    
    print("✅ All required dependencies are installed")
    return True

def check_files():
    """Check if all required files exist."""
    print("🔍 Checking required files...")
    
    required_files = [
        'run.py',
        'requirements.txt',
        'app/__init__.py',
        'config/config.py',
        'templates/homepage.html',
        'static/js/chart.js'
    ]
    
    missing_files = []
    
    for file_path in required_files:
        if not Path(file_path).exists():
            missing_files.append(file_path)
    
    if missing_files:
        print(f"❌ Missing files: {', '.join(missing_files)}")
        return False
    
    print("✅ All required files are present")
    return True

def main():
    """Run production validation checks."""
    print("=== KEF Teacher Dashboard - Production Validation ===")
    print()
    
    checks = [
        ("Files", check_files),
        ("Dependencies", check_dependencies),
        ("Environment", check_environment),
        ("Database", check_database),
        ("Application", check_application_start)
    ]
    
    passed = 0
    total = len(checks)
    
    for check_name, check_func in checks:
        print(f"Running {check_name} check...")
        if check_func():
            passed += 1
        print()
    
    print("=== Validation Summary ===")
    print(f"Passed: {passed}/{total} checks")
    
    if passed == total:
        print("🎉 All checks passed! Your application is ready for production.")
        print()
        print("To start the application:")
        print("  Development: python run.py")
        print("  Production:  gunicorn --bind 0.0.0.0:5000 --workers 4 run:app")
        return True
    else:
        print("❌ Some checks failed. Please fix the issues above before deploying.")
        return False

if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)