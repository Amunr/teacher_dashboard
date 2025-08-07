#!/usr/bin/env python3
"""
Script to populate test student count data.
"""

import sys
import os
from datetime import date, timedelta

# Add the app directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'app'))

from models.database import DatabaseManager, StudentCountModel
from config.config import DevelopmentConfig


def create_sample_student_counts(db_manager: DatabaseManager) -> None:
    """Create sample student count entries."""
    
    student_count_model = StudentCountModel(db_manager)
    
    today = date.today()
    
    # Sample student count entries for different periods
    sample_counts = [
        {
            'start_date': date(2024, 1, 1),
            'end_date': date(2024, 12, 31),
            'total_students': 450,
            'description': '2024 Academic Year - Total Enrollment'
        },
        {
            'start_date': date(2024, 9, 1),
            'end_date': date(2025, 6, 30),
            'total_students': 425,
            'description': '2024-25 School Year - Current Enrollment'
        },
        {
            'start_date': today - timedelta(days=365),
            'end_date': today,
            'total_students': 380,
            'description': 'Last 12 months - Active Students'
        },
        {
            'start_date': today - timedelta(days=180),
            'end_date': today,
            'total_students': 365,
            'description': 'Last 6 months - Current Semester'
        },
        {
            'start_date': today - timedelta(days=90),
            'end_date': today,
            'total_students': 355,
            'description': 'Last 3 months - Current Quarter'
        }
    ]
    
    created_ids = []
    
    for count_data in sample_counts:
        try:
            count_id = student_count_model.create_student_count(
                start_date=count_data['start_date'],
                end_date=count_data['end_date'],
                total_students=count_data['total_students'],
                description=count_data['description']
            )
            created_ids.append(count_id)
            print(f"✅ Created student count {count_id}: {count_data['total_students']} students "
                  f"({count_data['start_date']} to {count_data['end_date']})")
            
        except Exception as e:
            print(f"❌ Error creating student count: {e}")
    
    print(f"\n✅ Created {len(created_ids)} student count entries")
    
    # Test retrieval
    try:
        all_counts = student_count_model.get_all_student_counts()
        print(f"\n📊 Total student count entries in database: {len(all_counts)}")
        
        for count in all_counts[-3:]:  # Show last 3 entries
            print(f"  - {count['total_students']} students "
                  f"({count['start_date']} to {count['end_date']}): {count['description']}")
            
    except Exception as e:
        print(f"❌ Error retrieving student counts: {e}")


def main():
    """Main function to run the student count population."""
    
    print("🚀 Populating test student count data...")
    
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
    
    # Create sample student counts
    create_sample_student_counts(db_manager)
    
    print("\n🎉 Student count data population completed!")


if __name__ == "__main__":
    main()
