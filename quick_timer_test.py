#!/usr/bin/env python3

import time
import requests

print("Testing auto import timer for 2.5 minutes...")

for i in range(5):  # Check every 30 seconds for 2.5 minutes
    try:
        r = requests.get('http://localhost:5000/api/sheets/service/detailed-status')
        if r.status_code == 200:
            data = r.json()
            cycle_count = data['status_data']['cycle_count']
            minutes_left = data['minutes_until_next_run']
            next_time = data['next_run_time']
            print(f"Check {i+1}: Cycles completed: {cycle_count}, Next run in {minutes_left} min at {next_time}")
        else:
            print(f"Check {i+1}: Status check failed")
    except Exception as e:
        print(f"Check {i+1}: Error: {e}")
    
    if i < 4:  # Don't sleep after the last check
        time.sleep(30)

print("Timer test complete!")
