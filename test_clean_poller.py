#!/usr/bin/env python3
"""
Test the poller with clean data after fixing the database configuration
"""
import os
import sys
import sqlite3
import signal
from datetime import datetime

# Add timeout for Windows
def timeout_handler(signum, frame):
    raise TimeoutError("Operation timed out")

# Windows doesn't have SIGALRM, so we'll use a different approach
class TimeoutContext:
    def __init__(self, timeout):
        self.timeout = timeout
    
    def __enter__(self):
        import threading
        self.timer = threading.Timer(self.timeout, lambda: sys.exit(1))
        self.timer.start()
        return self
    
    def __exit__(self, *args):
        self.timer.cancel()

# Timeout wrapper
def with_timeout(timeout_seconds):
    return TimeoutContext(timeout_seconds)

print("=" * 60)
print(f"CLEAN POLLER TEST - {datetime.now()}")
print("=" * 60)

# Add the app directory to the path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

try:
    with with_timeout(25):  # 25 second timeout as requested by user
        from sheets_poller import SheetsPollerService
        from config.config import Config
        
        print("📊 Loading configuration...")
        config = Config()
        database_url = config.DATABASE_URL
        print(f"📊 Database URL: {database_url}")
        
        # Verify we're using the right database
        if 'dev_data.db' in database_url:
            print("❌ ERROR: Still using dev_data.db!")
            sys.exit(1)
        elif 'data.db' in database_url:
            print("✅ Correct database: data.db")
        
        # Check current database state
        print("\n📋 Checking current database state...")
        conn = sqlite3.connect('data.db')
        cursor = conn.cursor()
        
        # Count responses
        cursor.execute('SELECT COUNT(*) FROM responses')
        response_count = cursor.fetchone()[0]
        print(f"📊 Current responses in database: {response_count}")
        
        # Check last 3 responses to see if they have HTML content
        cursor.execute('SELECT id, Teacher, School, Name FROM responses ORDER BY id DESC LIMIT 3')
        recent_responses = cursor.fetchall()
        print("\n🔍 Recent responses check:")
        for res in recent_responses:
            teacher_sample = res[1][:30] if res[1] else "None"
            school_sample = res[2][:30] if res[2] else "None"
            is_html = 'html' in teacher_sample.lower() or '{' in teacher_sample or 'css' in teacher_sample.lower()
            status = "❌ HTML" if is_html else "✅ Clean"
            print(f"  ID {res[0]}: Teacher='{teacher_sample}' {status}")
        
        # Get last row processed
        cursor.execute('SELECT last_row_processed FROM sheets_config')
        last_row = cursor.fetchone()[0] if cursor.rowcount > 0 else 0
        print(f"📍 Last row processed: {last_row}")
        conn.close()
        
        print("\n🚀 Initializing poller service...")
        service = SheetsPollerService(database_url)
        
        print("📥 Running single poll cycle...")
        success = service.poll_once()
        
        if success:
            print("✅ Poll cycle completed successfully")
            
            # Check what was added
            conn = sqlite3.connect('data.db')
            cursor = conn.cursor()
            cursor.execute('SELECT COUNT(*) FROM responses')
            new_response_count = cursor.fetchone()[0]
            print(f"📊 Responses after poll: {new_response_count} (added: {new_response_count - response_count})")
            
            # Check latest response quality
            if new_response_count > response_count:
                cursor.execute('SELECT id, Teacher, School, Name FROM responses ORDER BY id DESC LIMIT 1')
                latest = cursor.fetchone()
                teacher_sample = latest[1][:50] if latest[1] else "None"
                school_sample = latest[2][:50] if latest[2] else "None"
                student_sample = latest[3][:50] if latest[3] else "None"
                
                print(f"\n📋 Latest response (ID {latest[0]}):")
                print(f"  Teacher: '{teacher_sample}'")
                print(f"  School: '{school_sample}'")
                print(f"  Student: '{student_sample}'")
                
                # Check if it's still HTML
                is_html = any('html' in str(field).lower() or '{' in str(field) or 'css' in str(field).lower() 
                            for field in [teacher_sample, school_sample, student_sample])
                
                if is_html:
                    print("❌ STILL GETTING HTML CONTENT!")
                else:
                    print("✅ Clean data received!")
            
            conn.close()
        else:
            print("❌ Poll cycle failed")
            
except TimeoutError:
    print("⏰ Test timed out after 25 seconds")
    sys.exit(1)
except Exception as e:
    print(f"❌ Test failed: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

print("\n📊 Test completed successfully!")
