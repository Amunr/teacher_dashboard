#!/usr/bin/env python3
"""
Test script to create sample data and verify functionality.
Run this from the project root directory.
"""

import os
import sys
from datetime import date, timedelta
import random

# Add the current directory to Python path
sys.path.insert(0, os.path.dirname(__file__))

# Import from the app
from app.models.database import DatabaseManager, ResponseModel, StudentCountModel
from config.config import DevelopmentConfig


def create_test_data():
    """Create comprehensive test data for the dashboard."""
    
    print("🚀 Creating test data for KEF Dashboard...")
    
    # Initialize database
    try:
        db_manager = DatabaseManager(
            database_url=DevelopmentConfig.DATABASE_URL,
            engine_options={}
        )
        db_manager.initialize_database()
        print("✅ Database initialized successfully")
        
    except Exception as e:
        print(f"❌ Failed to initialize database: {e}")
        return
    
    # Create student count model and add test data
    print("\n📊 Creating student count entries...")
    student_count_model = StudentCountModel(db_manager)
    
    today = date.today()
    student_counts = [
        {
            'start_date': date(2024, 1, 1),
            'end_date': date(2024, 12, 31),
            'total_students': 450,
            'description': '2024 Academic Year'
        },
        {
            'start_date': today - timedelta(days=365),
            'end_date': today,
            'total_students': 380,
            'description': 'Last 12 months'
        },
        {
            'start_date': today - timedelta(days=180),
            'end_date': today,
            'total_students': 365,
            'description': 'Current Semester'
        }
    ]
    
    for count_data in student_counts:
        try:
            count_id = student_count_model.create_student_count(**count_data)
            print(f"✅ Created student count {count_id}: {count_data['total_students']} students")
        except Exception as e:
            print(f"⚠️  Student count already exists or error: {e}")
    
    # Create response model and add test responses
    print("\n📝 Creating sample responses...")
    response_model = ResponseModel(db_manager)
    
    # Sample data arrays
    schools = ["Lincoln Elementary", "Washington Middle", "Roosevelt High", "Jefferson Elementary", "Madison School"]
    grades = ["K", "1", "2", "3", "4", "5", "6", "7", "8"]
    teachers = ["Ms. Smith", "Mr. Johnson", "Mrs. Davis", "Ms. Wilson", "Mr. Brown", "Ms. Garcia", "Mr. Taylor"]
    students = [
        "John Doe", "Jane Smith", "Mike Johnson", "Sarah Wilson", "Chris Brown",
        "Emma Davis", "Alex Garcia", "Lily Chen", "Noah Martinez", "Olivia Taylor",
        "Ethan Anderson", "Sophia Williams", "Liam Jones", "Isabella Miller", "Mason Wilson"
    ]
    assessments = ["Pre-Assessment", "Mid-Term", "Final Assessment", "Progress Check"]
    
    # Generate responses for different time periods to create realistic data
    date_ranges = [
        (today - timedelta(days=30), today),  # Last month
        (today - timedelta(days=90), today - timedelta(days=60)),  # 2-3 months ago
        (today - timedelta(days=180), today - timedelta(days=150))  # 5-6 months ago
    ]
    
    created_responses = 0
    
    for date_range in date_ranges:
        start_date, end_date = date_range
        
        # Create 15-20 responses for each date range
        for i in range(random.randint(15, 25)):
            try:
                # Generate a random date within the range
                days_diff = (end_date - start_date).days
                random_days = random.randint(0, days_diff)
                response_date = start_date + timedelta(days=random_days)
                
                # Create response data
                response_data = {
                    # Note: These index IDs should match your actual question layout
                    # For testing, we'll use generic IDs and hope they map to existing questions
                    1: random.choice(schools),      # School
                    2: random.choice(grades),       # Grade  
                    3: random.choice(teachers),     # Teacher
                    4: random.choice(assessments),  # Assessment
                    5: random.choice(students),     # Student name
                    6: response_date.strftime('%Y-%m-%d'),  # Date
                }
                
                # Add random scores for domain questions (assuming index IDs 7-25)
                for question_id in range(7, 26):
                    response_data[question_id] = random.randint(1, 4)  # Score 1-4
                
                res_id = response_model.create_response(response_data)
                created_responses += 1
                
                if created_responses % 10 == 0:
                    print(f"✅ Created {created_responses} responses...")
                    
            except Exception as e:
                print(f"⚠️  Could not create response: {e}")
                # Continue with other responses
                continue
    
    print(f"\n✅ Created {created_responses} total responses")
    
    # Test dashboard data retrieval
    print("\n📊 Testing dashboard data retrieval...")
    try:
        dashboard_data = response_model.get_dashboard_data()
        print(f"Students assessed: {dashboard_data['total_students_assessed']}")
        print(f"Total students: {dashboard_data['total_students']}")
        print(f"Average score: {dashboard_data['average_score']}%")
        print(f"Domains found: {len(dashboard_data['domain_scores'])}")
        print(f"Glowing skills: {len(dashboard_data['glowing_skills'])}")
        print(f"Growing skills: {len(dashboard_data['growing_skills'])}")
        
    except Exception as e:
        print(f"⚠️  Error testing dashboard data: {e}")
    
    print("\n🎉 Test data creation completed!")
    print("\n🌐 You can now test the dashboard at:")
    print("   - Main Dashboard: http://127.0.0.1:5000")
    print("   - Maintenance Page: http://127.0.0.1:5000/maintenance")
    print("   - API Endpoint: http://127.0.0.1:5000/api/dashboard-data")


if __name__ == "__main__":
    create_test_data()
