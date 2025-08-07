#!/usr/bin/env python3
"""
External script to test response creation functionality.
This simulates how responses would be inserted via Google Sheets API.
"""

import sys
import os
import json
from datetime import date
from typing import Dict, Any, List

# Add the app directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'app'))

from models.database import DatabaseManager, ResponseModel
from config.config import DevelopmentConfig


def create_sample_response(db_manager: DatabaseManager) -> None:
    """Create a sample response for testing."""
    
    response_model = ResponseModel(db_manager)
    
    # Sample response data (simulating form submission)
    # This represents answers to questions with index_ids 1-20
    sample_response_data = {
        1: 1,   # Metadata: School -> "Test School"
        2: 1,   # Metadata: Grade -> "Grade 1"
        3: 1,   # Metadata: Teacher -> "Ms. Smith"
        4: 1,   # Metadata: Assessment -> "Pre-Assessment"
        5: 1,   # Metadata: Name -> "John Doe"
        6: 1,   # Metadata: Date -> today
        7: 3,   # Domain question 1 (score out of 4)
        8: 2,   # Domain question 2
        9: 4,   # Domain question 3
        10: 1,  # Domain question 4
        11: 3,  # Domain question 5
        12: 2,  # Domain question 6
        13: 4,  # Domain question 7
        14: 3,  # Domain question 8
        15: 1,  # Domain question 9
        16: 2,  # Domain question 10
        17: 4,  # Domain question 11
        18: 3,  # Domain question 12
        19: 2,  # Domain question 13
        20: 1   # Domain question 14
    }
    
    try:
        res_id = response_model.create_response(sample_response_data)
        print(f"✅ Successfully created response with res_id: {res_id}")
        return res_id
    except Exception as e:
        print(f"❌ Error creating response: {e}")
        return None


def create_multiple_sample_responses(db_manager: DatabaseManager, count: int = 5) -> List[int]:
    """Create multiple sample responses for testing."""
    
    response_model = ResponseModel(db_manager)
    created_res_ids = []
    
    schools = ["Lincoln Elementary", "Washington Middle", "Roosevelt High", "Jefferson Elementary"]
    grades = ["K", "1", "2", "3", "4", "5"]
    teachers = ["Ms. Smith", "Mr. Johnson", "Mrs. Davis", "Ms. Wilson", "Mr. Brown"]
    students = ["John Doe", "Jane Smith", "Mike Johnson", "Sarah Wilson", "Chris Brown", 
               "Emma Davis", "Alex Garcia", "Lily Chen", "Noah Martinez", "Olivia Taylor"]
    
    import random
    
    for i in range(count):
        # Generate random response data
        response_data = {
            1: random.choice(schools),      # School
            2: random.choice(grades),       # Grade  
            3: random.choice(teachers),     # Teacher
            4: "Assessment " + str(i+1),    # Assessment
            5: random.choice(students),     # Student name
            6: str(date.today()),           # Date
        }
        
        # Add random scores for questions 7-20 (assuming these are domain questions)
        for question_id in range(7, 21):
            response_data[question_id] = random.randint(1, 4)  # Score 1-4
        
        try:
            res_id = response_model.create_response(response_data)
            created_res_ids.append(res_id)
            print(f"✅ Created response {i+1}/{count} with res_id: {res_id}")
        except Exception as e:
            print(f"❌ Error creating response {i+1}: {e}")
    
    return created_res_ids


def test_response_retrieval(db_manager: DatabaseManager) -> None:
    """Test response retrieval with filtering."""
    
    response_model = ResponseModel(db_manager)
    
    print("\n📊 Testing response retrieval...")
    
    try:
        # Get all responses
        all_responses = response_model.get_responses()
        print(f"Total responses in database: {len(all_responses)}")
        
        # Test filtering
        filters = {
            'school': 'Lincoln',
            'start_date': date(2025, 1, 1),
            'end_date': date.today()
        }
        
        filtered_responses = response_model.get_responses(filters=filters)
        print(f"Filtered responses (school=Lincoln): {len(filtered_responses)}")
        
        # Test dashboard data
        dashboard_data = response_model.get_dashboard_data(filters)
        print(f"Dashboard data - Students assessed: {dashboard_data['total_students_assessed']}")
        print(f"Dashboard data - Average score: {dashboard_data['average_score']}%")
        print(f"Dashboard data - Domains found: {len(dashboard_data['domain_scores'])}")
        
    except Exception as e:
        print(f"❌ Error retrieving responses: {e}")


def main():
    """Main function to run tests."""
    
    print("🚀 Starting response creation tests...")
    
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
    
    # Test single response creation
    print("\n📝 Creating single sample response...")
    create_sample_response(db_manager)
    
    # Test multiple response creation
    print("\n📝 Creating multiple sample responses...")
    created_ids = create_multiple_sample_responses(db_manager, count=10)
    print(f"\n✅ Created {len(created_ids)} responses: {created_ids}")
    
    # Test retrieval
    test_response_retrieval(db_manager)
    
    print("\n🎉 Test completed!")


if __name__ == "__main__":
    main()
