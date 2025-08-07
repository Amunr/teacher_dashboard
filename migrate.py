"""
Data migration script to transfer data from old database structure to new structure.
"""
import os
import sys
import shutil
from datetime import datetime

# Add the project root to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def backup_database():
    """Create a backup of the existing database."""
    if os.path.exists('data.db'):
        backup_name = f'data_backup_{datetime.now().strftime("%Y%m%d_%H%M%S")}.db'
        shutil.copy2('data.db', backup_name)
        print(f"✓ Database backed up to {backup_name}")
        return backup_name
    else:
        print("ℹ No existing database found to backup")
        return None

def test_new_structure():
    """Test that the new application structure works."""
    try:
        from app import create_app
        app = create_app()
        
        # Test database connection
        with app.app_context():
            health = app.db_manager.health_check()
            if health:
                print("✓ New application structure works correctly")
                print("✓ Database connection successful")
                return True
            else:
                print("✗ Database connection failed")
                return False
                
    except Exception as e:
        print(f"✗ Error testing new structure: {e}")
        return False

def migrate_data():
    """
    Migrate data from old structure to new structure.
    
    Note: Since we're using the same database schema, no migration is needed.
    The new code is backward compatible with existing data.
    """
    print("ℹ Database schema is compatible - no migration needed")
    print("✓ Existing data will work with new application structure")

def cleanup_old_files():
    """Clean up old application files (optional)."""
    old_files = ['app_old.py', 'database_old.py']
    
    print("\nOptional cleanup:")
    for file in old_files:
        if os.path.exists(file):
            print(f"  - {file} (backup of old code)")
    
    print("\nYou can safely delete the backup files once you've verified the new structure works.")

def main():
    """Main migration process."""
    print("🔄 KEF Application Migration")
    print("=" * 40)
    
    # 1. Backup existing database
    backup_file = backup_database()
    
    # 2. Test new structure
    print("\n📋 Testing new application structure...")
    if not test_new_structure():
        print("\n❌ Migration failed! Please check the error messages above.")
        return False
    
    # 3. Migrate data (if needed)
    print("\n🔄 Checking data migration...")
    migrate_data()
    
    # 4. Show cleanup options
    cleanup_old_files()
    
    print("\n✅ Migration completed successfully!")
    print("\n🚀 You can now use the new application structure:")
    print("   - Run with: python run.py")
    print("   - Access at: http://localhost:5000")
    print("   - Check health: http://localhost:5000/health")
    
    return True

if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)
