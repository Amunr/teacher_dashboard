#!/usr/bin/env python3
"""
Cleanup Script for KEF Teacher Dashboard

This script removes unnecessary test files and consolidates the codebase.
It keeps only essential files needed for the application to function.
"""

import os
import shutil
import sys
from pathlib import Path

# Files to keep (essential files)
ESSENTIAL_FILES = {
    # Main application files
    'run.py',
    'requirements.txt',
    'README.md',
    '.gitignore',
    '.env.example',
    
    # Configuration and cleanup
    'clear_responses.py',  # Keep this utility
    'tests.py',           # Our new consolidated test file
    
    # Database files
    'data.db',
    
    # Directories (will be handled separately)
    'app/',
    'config/',
    'static/',
    'templates/',
    'venv/',
    '.git/',
    '__pycache__/',
}

# Files to definitely remove (test/debug files)
FILES_TO_REMOVE = {
    # Test and debug files
    'add_more_students.py',
    'check_config.py',
    'check_data.py',
    'check_data_quality.py',
    'check_dates.py',
    'check_db.py',
    'check_index_mapping.py',
    'check_metadata_questions.py',
    'check_questions.py',
    'check_recent_data.py',
    'check_responses.py',
    'check_tables.py',
    'clear_data.py',
    'comprehensive_system_check.py',
    'comprehensive_test.py',
    'comprehensive_test_fixed.py',
    'create_correct_test_data.py',
    'create_simple_test_data.py',
    'create_test_data.py',
    'debug_csv_content.py',
    'debug_dates.py',
    'debug_mapping.py',
    'debug_poller_single.py',
    'dev.py',
    'dev_data.db',
    'fix_date_range.py',
    'fix_sample_data.py',
    'load_sample_data.py',
    'populate_student_counts.py',
    'quick_test.py',
    'setup_test_environment.py',
    'sheets_poller.py',  # Moved to app/services/
    'simple_test.py',
    'test_both_features.py',
    'test_clean_poller.py',
    'test_dashboard.html',
    'test_data.py',
    'test_data_mapping.py',
    'test_domain_filter.py',
    'test_homepage.py',
    'test_maintenance_api.py',
    'test_maintenance_final.py',
    'test_maintenance_fixes.py',
    'test_maintenance_performance.py',
    'test_new_date_logic.py',
    'test_poller_timeout.py',
    'test_responses.py',
    'test_school_readiness_display.py',
    'test_sheets_integration.py',
    'test_sheets_service.py',
    'test_with_timeout.py',
    'verification_test.py',
    
    # Log and pid files
    'sheets_poller.log',
    'sheets_poller.pid',
    
    # Documentation files (keeping only README.md)
    'GOOGLE_SHEETS_INTEGRATION.md',
    'MAINTENANCE_FIXES_SUMMARY.md',
    'OPTIMIZATION_SUMMARY.md',
    'SCHOOL_READINESS_FIX_SUMMARY.md',
}

# Files to check for usage (might be used)
MAYBE_USED_FILES = {
    'migrate.py',  # Database migration - might be needed
}


def check_file_usage(filepath: str) -> bool:
    """
    Check if a file is imported or used anywhere in the app.
    
    Args:
        filepath: Path to the file to check
        
    Returns:
        True if the file appears to be used, False otherwise
    """
    filename = os.path.basename(filepath)
    module_name = filename.replace('.py', '')
    
    # Search for imports in app directory
    app_dir = Path('app')
    if app_dir.exists():
        for py_file in app_dir.rglob('*.py'):
            try:
                with open(py_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                    if (f'import {module_name}' in content or 
                        f'from {module_name}' in content or
                        filename in content):
                        return True
            except Exception:
                continue
    
    # Check main files
    for main_file in ['run.py', 'app/__init__.py']:
        if os.path.exists(main_file):
            try:
                with open(main_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                    if (f'import {module_name}' in content or 
                        f'from {module_name}' in content or
                        filename in content):
                        return True
            except Exception:
                continue
    
    return False


def backup_directory():
    """Create a backup of the current directory."""
    import time
    backup_name = f"KEF_backup_{int(time.time())}"
    print(f"Creating backup: {backup_name}")
    
    # Create backup (excluding venv and git)
    os.makedirs(backup_name, exist_ok=True)
    
    for item in os.listdir('.'):
        if item not in ['venv', '.git', backup_name]:
            src = item
            dst = os.path.join(backup_name, item)
            
            if os.path.isdir(src):
                shutil.copytree(src, dst)
            else:
                shutil.copy2(src, dst)
    
    print(f"✅ Backup created: {backup_name}")
    return backup_name


def cleanup_files(dry_run: bool = True):
    """
    Clean up unnecessary files.
    
    Args:
        dry_run: If True, only show what would be removed without actually removing
    """
    print("=" * 60)
    print("KEF Teacher Dashboard - File Cleanup")
    print("=" * 60)
    
    # Get current directory contents
    current_files = set()
    for item in os.listdir('.'):
        if os.path.isfile(item):
            current_files.add(item)
    
    # Files to remove
    to_remove = FILES_TO_REMOVE.intersection(current_files)
    
    # Check maybe-used files
    maybe_remove = []
    for file in MAYBE_USED_FILES:
        if file in current_files:
            if not check_file_usage(file):
                maybe_remove.append(file)
                print(f"📋 {file} - appears unused, will be removed")
            else:
                print(f"📋 {file} - appears to be used, keeping")
    
    to_remove.update(maybe_remove)
    
    print(f"\n📊 Summary:")
    print(f"Total files in directory: {len(current_files)}")
    print(f"Files to remove: {len(to_remove)}")
    print(f"Files to keep: {len(current_files) - len(to_remove)}")
    
    if to_remove:
        print(f"\n🗑️ Files to remove:")
        for file in sorted(to_remove):
            size = os.path.getsize(file) if os.path.exists(file) else 0
            print(f"  - {file} ({size} bytes)")
    
    if not dry_run:
        print(f"\n🗑️ Removing files...")
        removed_count = 0
        for file in to_remove:
            try:
                if os.path.exists(file):
                    os.remove(file)
                    print(f"  ✅ Removed: {file}")
                    removed_count += 1
            except Exception as e:
                print(f"  ❌ Failed to remove {file}: {e}")
        
        print(f"\n✅ Cleanup completed! Removed {removed_count} files.")
    else:
        print(f"\n⚠️ This was a dry run. Use --execute to actually remove files.")


def reorganize_structure():
    """Suggest or implement structural improvements."""
    print("\n" + "=" * 60)
    print("STRUCTURAL REORGANIZATION SUGGESTIONS")
    print("=" * 60)
    
    suggestions = [
        "✅ Created consolidated tests.py file",
        "📝 Move sheets_poller.py logic into app/services/sheets_service.py",
        "📝 Ensure all services are properly imported in app/services/__init__.py",
        "📝 Consider moving utilities scripts to a 'scripts/' directory",
        "📝 Clean up __pycache__ directories periodically",
    ]
    
    for suggestion in suggestions:
        print(suggestion)


if __name__ == "__main__":
    import argparse
    import time
    
    parser = argparse.ArgumentParser(description='Clean up KEF codebase')
    parser.add_argument('--execute', action='store_true',
                       help='Actually remove files (default is dry run)')
    parser.add_argument('--backup', action='store_true',
                       help='Create backup before cleanup')
    
    args = parser.parse_args()
    
    if args.backup:
        backup_directory()
    
    cleanup_files(dry_run=not args.execute)
    reorganize_structure()
    
    print(f"\n💡 Next steps:")
    print(f"1. Run 'python tests.py' to verify everything works")
    print(f"2. Test the application with 'python run.py'")
    print(f"3. Check that Google Sheets integration still works")
    print(f"4. Review app/services/sheets_service.py for sheets polling functionality")
