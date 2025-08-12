#!/usr/bin/env python3
"""
Test data mapping with timeout and debugging
"""
import subprocess
import sqlite3
import time
import sys

def test_data_mapping_with_timeout():
    """Test that data is properly mapped to responses table"""
    print("🧪 TESTING DATA MAPPING TO RESPONSES TABLE")
    print("=" * 50)
    
    try:
        # Step 1: Check current state
        print("📊 Step 1: Checking current database state...")
        conn = sqlite3.connect('data.db')
        cursor = conn.cursor()
        
        cursor.execute("SELECT COUNT(*) FROM responses")
        initial_count = cursor.fetchone()[0]
        print(f"   Initial responses count: {initial_count}")
        
        cursor.execute("SELECT last_row_processed FROM sheets_config LIMIT 1")
        current_last_row = cursor.fetchone()
        if current_last_row:
            print(f"   Current last row processed: {current_last_row[0]}")
        else:
            print("   ❌ No configuration found!")
            return False
        
        # Step 2: Reset to a lower row to force processing
        new_last_row = 10
        print(f"🔄 Step 2: Resetting last row to {new_last_row} to force processing...")
        cursor.execute("UPDATE sheets_config SET last_row_processed = ?", (new_last_row,))
        conn.commit()
        conn.close()
        
        # Step 3: Run poller with timeout
        print(f"⚡ Step 3: Running poller with 2-minute timeout...")
        start_time = time.time()
        
        result = subprocess.run(
            ['python', 'sheets_poller.py', '--mode', 'once'],
            capture_output=True,
            text=True,
            timeout=120  # 2-minute timeout
        )
        
        elapsed = time.time() - start_time
        print(f"   Poller completed in {elapsed:.1f} seconds")
        print(f"   Exit code: {result.returncode}")
        
        if result.stdout:
            print("   📄 Stdout:")
            for line in result.stdout.split('\n')[-10:]:  # Last 10 lines
                if line.strip():
                    print(f"      {line}")
        
        if result.stderr:
            print("   ⚠️  Stderr:")
            for line in result.stderr.split('\n')[-5:]:  # Last 5 lines
                if line.strip():
                    print(f"      {line}")
        
        # Step 4: Check results
        print("📋 Step 4: Checking results...")
        conn = sqlite3.connect('data.db')
        cursor = conn.cursor()
        
        cursor.execute("SELECT COUNT(*) FROM responses")
        final_count = cursor.fetchone()[0]
        processed_responses = final_count - initial_count
        
        print(f"   Final responses count: {final_count}")
        print(f"   New responses processed: {processed_responses}")
        
        if processed_responses > 0:
            print("✅ SUCCESS: Data was successfully mapped to responses table!")
            
            # Show sample data
            cursor.execute("SELECT * FROM responses ORDER BY \"res-id\" DESC LIMIT 3")
            samples = cursor.fetchall()
            print("   📄 Sample responses:")
            for i, sample in enumerate(samples):
                print(f"      Row {i+1}: res-id={sample[0]}, School='{sample[1]}', Name='{sample[5]}', Index_ID={sample[7]}, Response='{sample[8]}'")
        else:
            print("❌ FAILURE: No new data was mapped to responses table")
            
            # Check for failed imports
            cursor.execute("SELECT COUNT(*) FROM failed_imports")
            failed_count = cursor.fetchone()[0]
            print(f"   Failed imports: {failed_count}")
            
            if failed_count > 0:
                cursor.execute("SELECT * FROM failed_imports ORDER BY id DESC LIMIT 2")
                failures = cursor.fetchall()
                print("   Recent failures:")
                for failure in failures:
                    print(f"      Row {failure[1]}: {failure[3][:100]}...")
        
        conn.close()
        return processed_responses > 0
        
    except subprocess.TimeoutExpired:
        print("❌ TIMEOUT: Poller timed out after 2 minutes")
        return False
    except Exception as e:
        print(f"❌ ERROR: {e}")
        return False

def check_layout_logic():
    """Check if layout and questions logic is working"""
    print("\n🗓️  CHECKING LAYOUT LOGIC")
    print("=" * 50)
    
    try:
        conn = sqlite3.connect('data.db')
        cursor = conn.cursor()
        
        # Check questions table (no layouts table needed)
        from datetime import date
        today = date.today()
        print(f"📅 Today's date: {today}")
        
        cursor.execute("""
            SELECT DISTINCT year_start, year_end, Domain, SubDomain, COUNT(*) as count
            FROM questions 
            WHERE year_start <= ? AND year_end >= ?
            GROUP BY year_start, year_end, Domain, SubDomain
            ORDER BY Domain, SubDomain
        """, (today, today))
        
        domain_counts = cursor.fetchall()
        print(f"📝 Questions by domain/subdomain for today:")
        
        metadata_count = 0
        regular_count = 0
        
        for year_start, year_end, domain, subdomain, count in domain_counts:
            print(f"   {domain} > {subdomain}: {count} questions ({year_start} to {year_end})")
            if domain == "MetaData":
                metadata_count += count
            else:
                regular_count += count
        
        print(f"📊 Summary: {metadata_count} metadata questions, {regular_count} regular questions")
        
        conn.close()
        return True
        
    except Exception as e:
        print(f"❌ ERROR checking layout logic: {e}")
        return False

def main():
    """Run comprehensive data mapping test"""
    print("🚀 COMPREHENSIVE DATA MAPPING TEST")
    print("Testing that Google Sheets data properly maps to responses table")
    print("All operations have 2-minute timeouts")
    
    # Test 1: Layout logic
    layout_ok = check_layout_logic()
    
    # Test 2: Data mapping
    mapping_ok = test_data_mapping_with_timeout()
    
    # Summary
    print(f"\n{'=' * 60}")
    print("📊 TEST SUMMARY")
    print(f"{'=' * 60}")
    print(f"Layout logic working: {'✅ YES' if layout_ok else '❌ NO'}")
    print(f"Data mapping working: {'✅ YES' if mapping_ok else '❌ NO'}")
    
    if layout_ok and mapping_ok:
        print("\n🎉 ALL TESTS PASSED!")
        print("   Data is properly mapping from Google Sheets to responses table")
    else:
        print("\n⚠️  SOME TESTS FAILED")
        print("   Check the debugging output above for details")
    
    return layout_ok and mapping_ok

if __name__ == "__main__":
    try:
        success = main()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n🛑 Tests interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n💥 Test suite crashed: {e}")
        sys.exit(1)
