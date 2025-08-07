"""
Development helper script for common tasks.
"""
import os
import sys
import subprocess
from pathlib import Path

def activate_venv():
    """Check if virtual environment is activated."""
    return hasattr(sys, 'real_prefix') or (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix)

def run_app():
    """Run the Flask application."""
    if not activate_venv():
        print("⚠️  Virtual environment not activated!")
        print("   Activate it with: venv\\Scripts\\activate (Windows) or source venv/bin/activate (Unix)")
        return False
    
    print("🚀 Starting KEF Application...")
    try:
        subprocess.run([sys.executable, 'run.py'], check=True)
    except KeyboardInterrupt:
        print("\n🛑 Application stopped by user")
    except subprocess.CalledProcessError as e:
        print(f"❌ Application failed to start: {e}")
        return False
    return True

def install_deps():
    """Install dependencies."""
    print("📦 Installing dependencies...")
    try:
        subprocess.run([sys.executable, '-m', 'pip', 'install', '-r', 'requirements.txt'], check=True)
        print("✅ Dependencies installed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to install dependencies: {e}")
        return False

def run_tests():
    """Run application tests."""
    print("🧪 Running tests...")
    # For now, just do a basic import test
    try:
        from app import create_app
        app = create_app('testing')
        print("✅ Basic import test passed")
        return True
    except Exception as e:
        print(f"❌ Test failed: {e}")
        return False

def check_health():
    """Check application health."""
    print("🔍 Checking application health...")
    try:
        import requests
        response = requests.get('http://localhost:5000/health', timeout=5)
        if response.status_code == 200:
            print("✅ Application is healthy")
            print(f"   Response: {response.json()}")
            return True
        else:
            print(f"⚠️  Application returned status {response.status_code}")
            return False
    except ImportError:
        print("⚠️  'requests' not installed - cannot check health remotely")
        return False
    except Exception as e:
        print(f"❌ Health check failed: {e}")
        return False

def show_structure():
    """Show the project structure."""
    print("📁 Project Structure:")
    print("""
KEF/
├── app/                    # Main application package
│   ├── __init__.py        # Application factory
│   ├── models/            # Database models
│   ├── routes/            # Route blueprints  
│   ├── services/          # Business logic
│   └── utils/             # Utilities
├── config/                # Configuration
├── templates/             # Jinja2 templates
├── static/               # Static assets
├── logs/                 # Application logs
├── run.py               # Application entry point
└── requirements.txt     # Dependencies
""")

def main():
    """Main CLI interface."""
    if len(sys.argv) < 2:
        print("🛠️  KEF Development Helper")
        print("=" * 30)
        print("Usage: python dev.py <command>")
        print("\nCommands:")
        print("  run        - Start the application")
        print("  install    - Install dependencies")
        print("  test       - Run tests")
        print("  health     - Check application health")
        print("  structure  - Show project structure")
        return
    
    command = sys.argv[1].lower()
    
    if command == 'run':
        run_app()
    elif command == 'install':
        install_deps()
    elif command == 'test':
        run_tests()
    elif command == 'health':
        check_health()
    elif command == 'structure':
        show_structure()
    else:
        print(f"❌ Unknown command: {command}")
        print("   Use 'python dev.py' to see available commands")

if __name__ == '__main__':
    main()
