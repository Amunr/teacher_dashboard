#!/usr/bin/env python3
"""
Script to create a complete test environment with layouts and responses.
"""

import os
import sys
from datetime import date, timedelta
import random

# Add the current directory to Python path
sys.path.insert(0, os.path.dirname(__file__))

from app.models.database import DatabaseManager, LayoutModel, ResponseModel, StudentCountModel
from config.config import DevelopmentConfig


def create_sample_layout(layout_model: LayoutModel) -> int:
    """Create a sample layout with questions."""
    
    print("📋 Creating sample layout...")
    
    # Sample layout data
    today = date.today()
    year_start = date(today.year, 1, 1)
    year_end = date(today.year, 12, 31)
    
    layout_data = []
    index_id = 1
    
    # Metadata questions
    metadata_questions = [
        {"Domain": "MetaData", "SubDomain": "School", "Name": "School Name"},
        {"Domain": "MetaData", "SubDomain": "Grade", "Name": "Grade Level"},
        {"Domain": "MetaData", "SubDomain": "Teacher", "Name": "Teacher Name"},
        {"Domain": "MetaData", "SubDomain": "Assessment", "Name": "Assessment Type"},
        {"Domain": "MetaData", "SubDomain": "Name", "Name": "Student Name"},
        {"Domain": "MetaData", "SubDomain": "Date", "Name": "Assessment Date"}
    ]
    
    for meta in metadata_questions:
        layout_data.append({
            "year_start": year_start,
            "year_end": year_end,
            "Domain": meta["Domain"],
            "SubDomain": meta["SubDomain"],
            "Index_ID": index_id,
            "Name": meta["Name"],
            "Date edited": today,
            "layout_name": "2025 Assessment Layout"
        })
        index_id += 1
    
    # Domain questions
    domains = {
        "Language & Literacy": [
            "Letter Recognition", "Phonemic Awareness", "Vocabulary", "Reading Comprehension",
            "Writing Skills", "Oral Communication"
        ],
        "Mathematics": [
            "Number Recognition", "Counting", "Basic Operations", "Patterns",
            "Shapes & Geometry", "Measurement"
        ],
        "Social-Emotional": [
            "Self-Regulation", "Social Skills", "Emotional Recognition", "Cooperation",
            "Empathy", "Conflict Resolution"
        ],
        "Physical Development": [
            "Fine Motor Skills", "Gross Motor Skills", "Body Awareness", "Health Habits"
        ],
        "Cognitive Development": [
            "Problem Solving", "Memory", "Attention", "Logic & Reasoning"
        ]
    }
    
    for domain_name, subdomains in domains.items():
        for subdomain in subdomains:
            for i in range(2):  # 2 questions per subdomain
                layout_data.append({
                    "year_start": year_start,
                    "year_end": year_end,
                    "Domain": domain_name,
                    "SubDomain": subdomain,
                    "Index_ID": index_id,
                    "Name": f"{subdomain} - Question {i+1}",
                    "Date edited": today,
                    "layout_name": "2025 Assessment Layout"
                })
                index_id += 1
    
    # Create the layout
    layout_id = layout_model.create_layout(layout_data)
    print(f"✅ Created layout {layout_id} with {len(layout_data)} questions")
    return layout_id


def create_test_responses(response_model: ResponseModel, num_students: int = 50) -> None:
    """Create test responses that match the layout."""
    
    print(f"📝 Creating {num_students} test student responses...")
    
    # Sample data
    schools = ["Lincoln Elementary", "Washington Middle", "Roosevelt High", "Jefferson Elementary", "Madison School"]
    grades = ["K", "1", "2", "3", "4", "5"]
    teachers = ["Ms. Smith", "Mr. Johnson", "Mrs. Davis", "Ms. Wilson", "Mr. Brown", "Ms. Garcia"]
    students = [
        "John Doe", "Jane Smith", "Mike Johnson", "Sarah Wilson", "Chris Brown",
        "Emma Davis", "Alex Garcia", "Lily Chen", "Noah Martinez", "Olivia Taylor",
        "Ethan Anderson", "Sophia Williams", "Liam Jones", "Isabella Miller", "Mason Wilson",
        "Ava Taylor", "Lucas Davis", "Mia Wilson", "Noah Garcia", "Charlotte Brown",
        "Elijah Smith", "Amelia Johnson", "Oliver Davis", "Harper Wilson", "William Garcia",
        "Evelyn Brown", "James Smith", "Abigail Johnson", "Benjamin Davis", "Emily Wilson"
    ]
    assessments = ["Pre-Assessment", "Mid-Term Assessment", "Final Assessment", "Progress Check"]
    
    # Create responses over the last 6 months
    today = date.today()
    start_date = today - timedelta(days=180)
    
    created_count = 0
    
    for i in range(num_students):
        try:
            # Generate random assessment date
            days_back = random.randint(0, 180)
            assessment_date = today - timedelta(days=days_back)
            
            # Create response data
            response_data = {}
            
            # Metadata (index 1-6)
            response_data[1] = random.choice(schools)      # School
            response_data[2] = random.choice(grades)       # Grade
            response_data[3] = random.choice(teachers)     # Teacher
            response_data[4] = random.choice(assessments)  # Assessment
            response_data[5] = students[i] if i < len(students) else f"Student {i+1}"  # Student name
            response_data[6] = assessment_date  # Date as date object
            
            # Domain questions (index 7 onwards)
            # Based on our layout creation, we have about 60 domain questions
            for question_idx in range(7, 67):  # 60 domain questions
                # Simulate varying skill levels with some students performing better
                if i < 10:  # Top 10 students
                    score = random.choices([3, 4], weights=[30, 70])[0]
                elif i < 30:  # Middle 20 students
                    score = random.choices([2, 3, 4], weights=[20, 50, 30])[0]
                else:  # Bottom 20 students
                    score = random.choices([1, 2, 3], weights=[30, 50, 20])[0]
                
                response_data[question_idx] = score
            
            # Create the response
            res_id = response_model.create_response(response_data)
            created_count += 1
            
            if created_count % 10 == 0:
                print(f"✅ Created {created_count} responses...")
                
        except Exception as e:
            print(f"⚠️  Error creating response {i+1}: {e}")
            continue
    
    print(f"✅ Successfully created {created_count} responses")


def create_student_counts(student_count_model: StudentCountModel) -> None:
    """Create student count entries."""
    
    print("📊 Creating student count entries...")
    
    today = date.today()
    
    student_counts = [
        {
            'start_date': date(2024, 1, 1),
            'end_date': date(2024, 12, 31),
            'total_students': 450,
            'description': '2024 Academic Year - Total Enrollment'
        },
        {
            'start_date': date(2025, 1, 1),
            'end_date': date(2025, 12, 31),
            'total_students': 425,
            'description': '2025 Academic Year - Current Enrollment'
        },
        {
            'start_date': today - timedelta(days=365),
            'end_date': today,
            'total_students': 380,
            'description': 'Last 12 months - Active Students'
        }
    ]
    
    for count_data in student_counts:
        try:
            count_id = student_count_model.create_student_count(**count_data)
            print(f"✅ Created student count {count_id}: {count_data['total_students']} students")
        except Exception as e:
            print(f"⚠️  Error creating student count: {e}")


def main():
    """Main function to create complete test environment."""
    
    print("🚀 Creating complete test environment for KEF Dashboard...")
    
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
    
    # Create models
    layout_model = LayoutModel(db_manager)
    response_model = ResponseModel(db_manager)
    student_count_model = StudentCountModel(db_manager)
    
    # Create sample layout
    layout_id = create_sample_layout(layout_model)
    
    # Create student counts
    create_student_counts(student_count_model)
    
    # Create test responses
    create_test_responses(response_model, num_students=75)
    
    # Test dashboard data
    print("\n📊 Testing dashboard functionality...")
    try:
        dashboard_data = response_model.get_dashboard_data()
        print(f"✅ Students assessed: {dashboard_data['total_students_assessed']}")
        print(f"✅ Total students: {dashboard_data['total_students']}")
        print(f"✅ Average score: {dashboard_data['average_score']}%")
        print(f"✅ Domains found: {len(dashboard_data['domain_scores'])}")
        
        if dashboard_data['domain_scores']:
            print("\n🎯 Domain Performance:")
            for domain in dashboard_data['domain_scores'][:5]:  # Top 5
                print(f"   - {domain['domain']}: {domain['score']:.1f}%")
        
        if dashboard_data['glowing_skills']:
            print(f"\n💡 Glowing Skills: {len(dashboard_data['glowing_skills'])}")
            for skill in dashboard_data['glowing_skills']:
                print(f"   - {skill['domain']}: {skill['score']:.1f}%")
        
        if dashboard_data['growing_skills']:
            print(f"\n📈 Growing Skills: {len(dashboard_data['growing_skills'])}")
            for skill in dashboard_data['growing_skills']:
                print(f"   - {skill['domain']}: {skill['score']:.1f}%")
        
    except Exception as e:
        print(f"⚠️  Error testing dashboard: {e}")
    
    print(f"\n🎉 Test environment created successfully!")
    print(f"📋 Layout ID: {layout_id}")
    print("\n🌐 Test the dashboard at:")
    print("   - Main Dashboard: http://127.0.0.1:5000")
    print("   - Maintenance Page: http://127.0.0.1:5000/maintenance")
    print("   - Layout Manager: http://127.0.0.1:5000/layout")


if __name__ == "__main__":
    main()
