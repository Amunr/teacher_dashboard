import sqlite3
import subprocess
import sys
import time
from datetime import date

def run_with_timeout(command, timeout_seconds=30):
    """Run command with timeout - Windows compatible"""
    try:
        print(f"Running command with {timeout_seconds}s timeout: {command}")
        
        # Start process
        process = subprocess.Popen(
            command,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            shell=True
        )
        
        # Wait for completion or timeout
        try:
            stdout, stderr = process.communicate(timeout=timeout_seconds)
            return stdout, stderr, process.returncode
        except subprocess.TimeoutExpired:
            print(f"TIMEOUT: Process killed after {timeout_seconds} seconds")
            process.terminate()
            time.sleep(2)
            if process.poll() is None:
                process.kill()
                time.sleep(1)
            return "", f"Timeout after {timeout_seconds} seconds", -1
            
    except Exception as e:
        return "", str(e), -1

def check_database_state():
    """Check current database state"""
    conn = sqlite3.connect('data.db')
    cursor = conn.cursor()
    
    # Check responses count
    cursor.execute('SELECT COUNT(*) FROM responses')
    responses_count = cursor.fetchone()[0]
    
    # Check last row processed
    cursor.execute('SELECT last_row_processed FROM sheets_config')
    last_row = cursor.fetchone()[0]
    
    # Check questions for today
    today_str = str(date.today())
    cursor.execute('SELECT COUNT(*) FROM questions WHERE year_start <= ? AND year_end >= ?', (today_str, today_str))
    questions_count = cursor.fetchone()[0]
    
    conn.close()
    
    return responses_count, last_row, questions_count

print("=== BEFORE POLLER RUN ===")
responses_before, last_row_before, questions = check_database_state()
print(f"Responses in DB: {responses_before}")
print(f"Last row processed: {last_row_before}")
print(f"Questions for today: {questions}")

# Reset last row to 1 to force processing
print("\n=== RESETTING LAST ROW TO 1 ===")
conn = sqlite3.connect('data.db')
conn.execute('UPDATE sheets_config SET last_row_processed = 1')
conn.commit()
conn.close()

print("\n=== RUNNING POLLER WITH 30 SECOND TIMEOUT ===")
stdout, stderr, returncode = run_with_timeout("python sheets_poller.py", 30)

print("STDOUT:")
print(stdout)
if stderr:
    print("STDERR:")
    print(stderr)

print(f"\nReturn code: {returncode}")

print("\n=== AFTER POLLER RUN ===")
responses_after, last_row_after, _ = check_database_state()
print(f"Responses in DB: {responses_after}")
print(f"Last row processed: {last_row_after}")
print(f"New responses created: {responses_after - responses_before}")
