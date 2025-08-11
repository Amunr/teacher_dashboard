#!/usr/bin/env python3
"""
Script to load fake sample data with sample layouts if none exists.
"""

import sys
import os
import random
from datetime import date, timedelta

# Add the current directory to Python path
sys.path.insert(0, os.path.dirname(__file__))

from app.models.database import DatabaseManager, LayoutModel, ResponseModel, StudentCountModel
from config.config import DevelopmentConfig


def create_sample_layout(layout_model: LayoutModel) -> int:
    """Create a comprehensive sample layout with realistic questions."""
    
    print("📋 Creating sample layout with realistic educational questions...")
    
    # Educational domains and their questions
    layout_questions = [
        # Metadata questions (Index 1-6)
        {"Index_ID": 1, "Question": "School", "Domain": "MetaData", "SubDomain": "Administrative", "Response_Type": "Text"},
        {"Index_ID": 2, "Question": "Grade Level", "Domain": "MetaData", "SubDomain": "Administrative", "Response_Type": "Text"},
        {"Index_ID": 3, "Question": "Teacher Name", "Domain": "MetaData", "SubDomain": "Administrative", "Response_Type": "Text"},
        {"Index_ID": 4, "Question": "Assessment Type", "Domain": "MetaData", "SubDomain": "Administrative", "Response_Type": "Text"},
        {"Index_ID": 5, "Question": "Student Name", "Domain": "MetaData", "SubDomain": "Administrative", "Response_Type": "Text"},
        {"Index_ID": 6, "Question": "Assessment Date", "Domain": "MetaData", "SubDomain": "Administrative", "Response_Type": "Date"},
        
        # Language & Literacy Domain (Index 7-18)
        {"Index_ID": 7, "Question": "Recognizes letters of the alphabet", "Domain": "Language & Literacy", "SubDomain": "Alphabet Knowledge", "Response_Type": "Scale"},
        {"Index_ID": 8, "Question": "Identifies letter sounds", "Domain": "Language & Literacy", "SubDomain": "Phonological Awareness", "Response_Type": "Scale"},
        {"Index_ID": 9, "Question": "Blends sounds to form words", "Domain": "Language & Literacy", "SubDomain": "Phonological Awareness", "Response_Type": "Scale"},
        {"Index_ID": 10, "Question": "Reads simple sight words", "Domain": "Language & Literacy", "SubDomain": "Reading", "Response_Type": "Scale"},
        {"Index_ID": 11, "Question": "Comprehends simple stories", "Domain": "Language & Literacy", "SubDomain": "Reading Comprehension", "Response_Type": "Scale"},
        {"Index_ID": 12, "Question": "Retells familiar stories", "Domain": "Language & Literacy", "SubDomain": "Oral Language", "Response_Type": "Scale"},
        {"Index_ID": 13, "Question": "Uses descriptive language", "Domain": "Language & Literacy", "SubDomain": "Vocabulary", "Response_Type": "Scale"},
        {"Index_ID": 14, "Question": "Follows multi-step directions", "Domain": "Language & Literacy", "SubDomain": "Listening", "Response_Type": "Scale"},
        {"Index_ID": 15, "Question": "Holds pencil correctly", "Domain": "Language & Literacy", "SubDomain": "Writing Mechanics", "Response_Type": "Scale"},
        {"Index_ID": 16, "Question": "Writes recognizable letters", "Domain": "Language & Literacy", "SubDomain": "Writing", "Response_Type": "Scale"},
        {"Index_ID": 17, "Question": "Writes simple words", "Domain": "Language & Literacy", "SubDomain": "Writing", "Response_Type": "Scale"},
        {"Index_ID": 18, "Question": "Expresses ideas through writing", "Domain": "Language & Literacy", "SubDomain": "Written Expression", "Response_Type": "Scale"},
        
        # Mathematics Domain (Index 19-30)
        {"Index_ID": 19, "Question": "Counts to 20", "Domain": "Mathematics", "SubDomain": "Number Sense", "Response_Type": "Scale"},
        {"Index_ID": 20, "Question": "Recognizes numbers 1-10", "Domain": "Mathematics", "SubDomain": "Number Recognition", "Response_Type": "Scale"},
        {"Index_ID": 21, "Question": "Understands one-to-one correspondence", "Domain": "Mathematics", "SubDomain": "Counting", "Response_Type": "Scale"},
        {"Index_ID": 22, "Question": "Compares quantities (more/less)", "Domain": "Mathematics", "SubDomain": "Number Comparison", "Response_Type": "Scale"},
        {"Index_ID": 23, "Question": "Adds simple numbers", "Domain": "Mathematics", "SubDomain": "Addition", "Response_Type": "Scale"},
        {"Index_ID": 24, "Question": "Subtracts simple numbers", "Domain": "Mathematics", "SubDomain": "Subtraction", "Response_Type": "Scale"},
        {"Index_ID": 25, "Question": "Identifies basic shapes", "Domain": "Mathematics", "SubDomain": "Geometry", "Response_Type": "Scale"},
        {"Index_ID": 26, "Question": "Sorts objects by attributes", "Domain": "Mathematics", "SubDomain": "Classification", "Response_Type": "Scale"},
        {"Index_ID": 27, "Question": "Creates and extends patterns", "Domain": "Mathematics", "SubDomain": "Patterns", "Response_Type": "Scale"},
        {"Index_ID": 28, "Question": "Measures using non-standard units", "Domain": "Mathematics", "SubDomain": "Measurement", "Response_Type": "Scale"},
        {"Index_ID": 29, "Question": "Understands basic time concepts", "Domain": "Mathematics", "SubDomain": "Time", "Response_Type": "Scale"},
        {"Index_ID": 30, "Question": "Collects and organizes data", "Domain": "Mathematics", "SubDomain": "Data Analysis", "Response_Type": "Scale"},
        
        # Social-Emotional Development (Index 31-42)
        {"Index_ID": 31, "Question": "Regulates emotions appropriately", "Domain": "Social-Emotional", "SubDomain": "Self-Regulation", "Response_Type": "Scale"},
        {"Index_ID": 32, "Question": "Shows empathy for others", "Domain": "Social-Emotional", "SubDomain": "Empathy", "Response_Type": "Scale"},
        {"Index_ID": 33, "Question": "Cooperates in group activities", "Domain": "Social-Emotional", "SubDomain": "Cooperation", "Response_Type": "Scale"},
        {"Index_ID": 34, "Question": "Resolves conflicts peacefully", "Domain": "Social-Emotional", "SubDomain": "Conflict Resolution", "Response_Type": "Scale"},
        {"Index_ID": 35, "Question": "Shares materials willingly", "Domain": "Social-Emotional", "SubDomain": "Sharing", "Response_Type": "Scale"},
        {"Index_ID": 36, "Question": "Makes friends easily", "Domain": "Social-Emotional", "SubDomain": "Friendship Skills", "Response_Type": "Scale"},
        {"Index_ID": 37, "Question": "Follows classroom rules", "Domain": "Social-Emotional", "SubDomain": "Rule Following", "Response_Type": "Scale"},
        {"Index_ID": 38, "Question": "Shows self-confidence", "Domain": "Social-Emotional", "SubDomain": "Self-Esteem", "Response_Type": "Scale"},
        {"Index_ID": 39, "Question": "Expresses needs appropriately", "Domain": "Social-Emotional", "SubDomain": "Communication", "Response_Type": "Scale"},
        {"Index_ID": 40, "Question": "Shows independence in tasks", "Domain": "Social-Emotional", "SubDomain": "Independence", "Response_Type": "Scale"},
        {"Index_ID": 41, "Question": "Demonstrates cultural awareness", "Domain": "Social-Emotional", "SubDomain": "Cultural Competence", "Response_Type": "Scale"},
        {"Index_ID": 42, "Question": "Shows respect for diversity", "Domain": "Social-Emotional", "SubDomain": "Respect", "Response_Type": "Scale"},
        
        # Physical Development (Index 43-53)
        {"Index_ID": 43, "Question": "Runs and jumps confidently", "Domain": "Physical Development", "SubDomain": "Gross Motor", "Response_Type": "Scale"},
        {"Index_ID": 44, "Question": "Balances on one foot", "Domain": "Physical Development", "SubDomain": "Balance", "Response_Type": "Scale"},
        {"Index_ID": 45, "Question": "Throws and catches a ball", "Domain": "Physical Development", "SubDomain": "Coordination", "Response_Type": "Scale"},
        {"Index_ID": 46, "Question": "Uses scissors effectively", "Domain": "Physical Development", "SubDomain": "Fine Motor", "Response_Type": "Scale"},
        {"Index_ID": 47, "Question": "Manipulates small objects", "Domain": "Physical Development", "SubDomain": "Fine Motor", "Response_Type": "Scale"},
        {"Index_ID": 48, "Question": "Draws recognizable figures", "Domain": "Physical Development", "SubDomain": "Drawing Skills", "Response_Type": "Scale"},
        {"Index_ID": 49, "Question": "Demonstrates body awareness", "Domain": "Physical Development", "SubDomain": "Body Awareness", "Response_Type": "Scale"},
        {"Index_ID": 50, "Question": "Practices healthy habits", "Domain": "Physical Development", "SubDomain": "Health Awareness", "Response_Type": "Scale"},
        {"Index_ID": 51, "Question": "Shows appropriate energy levels", "Domain": "Physical Development", "SubDomain": "Energy Management", "Response_Type": "Scale"},
        {"Index_ID": 52, "Question": "Navigates playground equipment", "Domain": "Physical Development", "SubDomain": "Spatial Awareness", "Response_Type": "Scale"},
        {"Index_ID": 53, "Question": "Participates in physical activities", "Domain": "Physical Development", "SubDomain": "Physical Participation", "Response_Type": "Scale"},
        
        # Cognitive Development (Index 54-64)
        {"Index_ID": 54, "Question": "Focuses attention on tasks", "Domain": "Cognitive Development", "SubDomain": "Attention", "Response_Type": "Scale"},
        {"Index_ID": 55, "Question": "Remembers multi-step instructions", "Domain": "Cognitive Development", "SubDomain": "Memory", "Response_Type": "Scale"},
        {"Index_ID": 56, "Question": "Solves problems creatively", "Domain": "Cognitive Development", "SubDomain": "Problem Solving", "Response_Type": "Scale"},
        {"Index_ID": 57, "Question": "Shows curiosity about learning", "Domain": "Cognitive Development", "SubDomain": "Curiosity", "Response_Type": "Scale"},
        {"Index_ID": 58, "Question": "Makes logical connections", "Domain": "Cognitive Development", "SubDomain": "Logical Thinking", "Response_Type": "Scale"},
        {"Index_ID": 59, "Question": "Plans and organizes activities", "Domain": "Cognitive Development", "SubDomain": "Executive Function", "Response_Type": "Scale"},
        {"Index_ID": 60, "Question": "Demonstrates creativity", "Domain": "Cognitive Development", "SubDomain": "Creativity", "Response_Type": "Scale"},
        {"Index_ID": 61, "Question": "Transfers learning to new situations", "Domain": "Cognitive Development", "SubDomain": "Transfer", "Response_Type": "Scale"},
        {"Index_ID": 62, "Question": "Shows metacognitive awareness", "Domain": "Cognitive Development", "SubDomain": "Metacognition", "Response_Type": "Scale"},
        {"Index_ID": 63, "Question": "Demonstrates flexible thinking", "Domain": "Cognitive Development", "SubDomain": "Flexibility", "Response_Type": "Scale"},
        {"Index_ID": 64, "Question": "Persists through challenges", "Domain": "Cognitive Development", "SubDomain": "Persistence", "Response_Type": "Scale"}
    ]
    
    today = date.today()
    year_start = date(today.year, 1, 1)
    year_end = date(today.year, 12, 31)
    
    try:
        # Prepare layout data in the correct format
        layout_data = []
        for question in layout_questions:
            question_data = {
                'Index_ID': question['Index_ID'],
                'Question': question['Question'],
                'Domain': question['Domain'],
                'SubDomain': question['SubDomain'],
                'Response_Type': question['Response_Type'],
                'year_start': year_start,
                'year_end': year_end
            }
            layout_data.append(question_data)
        
        layout_id = layout_model.create_layout(layout_data)
        
        print(f"✅ Created comprehensive layout {layout_id} with {len(layout_questions)} questions")
        return layout_id
        
    except Exception as e:
        print(f"❌ Error creating layout: {e}")
        return None


def create_sample_responses(response_model: ResponseModel, layout_id: int, num_students: int = 50) -> None:
    """Create realistic sample student responses."""
    
    print(f"📝 Creating {num_students} fake student responses with realistic data...")
    
    # Sample schools, teachers, and other metadata
    schools = [
        "Lincoln Elementary", "Roosevelt High", "Washington Middle", 
        "Jefferson Academy", "Madison School", "Monroe Elementary",
        "Adams Middle School", "Jackson High", "Van Buren Elementary"
    ]
    
    teachers = [
        "Ms. Garcia", "Mr. Johnson", "Mrs. Smith", "Mr. Davis", 
        "Ms. Wilson", "Mrs. Brown", "Mr. Miller", "Ms. Anderson",
        "Mrs. Taylor", "Mr. Thompson", "Ms. Lee", "Mrs. Martinez"
    ]
    
    grades = ["K", "1", "2", "3", "4", "5"]
    
    assessments = [
        "Fall Assessment", "Winter Assessment", "Spring Assessment",
        "Mid-Term Assessment", "Final Assessment", "Progress Check",
        "Diagnostic Assessment", "Quarterly Review"
    ]
    
    # Generate diverse student names
    first_names = [
        "Emma", "Liam", "Olivia", "Noah", "Ava", "Ethan", "Sophia", "Mason",
        "Isabella", "William", "Charlotte", "James", "Amelia", "Benjamin", "Mia",
        "Lucas", "Harper", "Henry", "Evelyn", "Alexander", "Abigail", "Michael",
        "Emily", "Daniel", "Elizabeth", "Jacob", "Sofia", "Logan", "Avery", "Jackson",
        "Ella", "David", "Madison", "Oliver", "Scarlett", "Jayden", "Victoria", "Luke",
        "Aria", "Matthew", "Grace", "Carter", "Chloe", "Owen", "Camila", "Wyatt",
        "Penelope", "Caleb", "Riley", "Nathan"
    ]
    
    last_names = [
        "Smith", "Johnson", "Williams", "Brown", "Jones", "Garcia", "Miller", "Davis",
        "Rodriguez", "Martinez", "Hernandez", "Lopez", "Gonzalez", "Wilson", "Anderson",
        "Thomas", "Taylor", "Moore", "Jackson", "Martin", "Lee", "Perez", "Thompson",
        "White", "Harris", "Sanchez", "Clark", "Ramirez", "Lewis", "Robinson"
    ]
    
    students = [f"{random.choice(first_names)} {random.choice(last_names)}" for _ in range(num_students)]
    
    created_count = 0
    
    for i in range(num_students):
        # Create varied assessment dates over the past year
        days_back = random.randint(0, 365)
        assessment_date = date.today() - timedelta(days=days_back)
        
        # Create realistic response patterns
        student_name = students[i]
        school = random.choice(schools)
        teacher = random.choice(teachers)
        grade = random.choice(grades)
        assessment = random.choice(assessments)
        
        # Create response data for each domain question (Index 7-64)
        responses_to_create = []
        
        # Simulate different skill levels
        if i < 10:  # Top 10% students - high performers
            base_score_range = (3, 4)
            score_weights = [20, 80]  # Mostly 4s
        elif i < 30:  # Next 40% - average to above average
            base_score_range = (2, 4)
            score_weights = [15, 50, 35]  # Mix of 2, 3, 4
        elif i < 45:  # Next 30% - below average
            base_score_range = (1, 3)
            score_weights = [30, 50, 20]  # Mix of 1, 2, 3
        else:  # Bottom 10% - struggling students
            base_score_range = (1, 2)
            score_weights = [70, 30]  # Mostly 1s and 2s
        
        for question_idx in range(7, 65):  # Domain questions only
            if len(base_score_range) == 2:
                score = random.choices(list(range(base_score_range[0], base_score_range[1] + 1)), 
                                     weights=score_weights)[0]
            else:
                score = random.choices([1, 2, 3, 4], weights=score_weights)[0]
            
            response_data = {
                'res-id': i + 1,
                'School': school,
                'Grade': grade,
                'Teacher': teacher,
                'Assessment': assessment,
                'Name': student_name,
                'Date': assessment_date,
                'Index_ID': question_idx,
                'Response': score
            }
            responses_to_create.append(response_data)
        
        # Batch create responses for this student
        try:
            response_model.create_response(responses_to_create)
            created_count += 1
            
            if created_count % 10 == 0:
                print(f"✅ Created responses for {created_count} students...")
                
        except Exception as e:
            print(f"⚠️  Error creating responses for student {i+1}: {e}")
    
    print(f"✅ Successfully created responses for {created_count} students")


def create_sample_student_counts(student_count_model: StudentCountModel) -> None:
    """Create sample student count entries for various time periods."""
    
    print("📊 Skipping student count creation due to schema issues...")
    print("✅ Student counts can be added manually through the maintenance interface")
    return


def check_existing_data(db_manager: DatabaseManager) -> dict:
    """Check if sample data already exists."""
    
    print("🔍 Checking for existing data...")
    
    try:
        response_model = ResponseModel(db_manager)
        layout_model = LayoutModel(db_manager)
        student_count_model = StudentCountModel(db_manager)
        
        responses = response_model.get_responses()
        layouts = layout_model.get_all_layouts()
        student_counts = student_count_model.get_all_student_counts()
        
        data_status = {
            'responses': len(responses),
            'layouts': len(layouts),
            'student_counts': len(student_counts)
        }
        
        print(f"📊 Found: {data_status['responses']} responses, "
              f"{data_status['layouts']} layouts, "
              f"{data_status['student_counts']} student counts")
        
        return data_status
        
    except Exception as e:
        print(f"⚠️  Error checking existing data: {e}")
        return {'responses': 0, 'layouts': 0, 'student_counts': 0}


def main():
    """Main function to load sample data if needed."""
    
    print("🚀 Loading fake sample data for KEF Dashboard...")
    
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
    
    # Check existing data
    data_status = check_existing_data(db_manager)
    
    # Create layout if none exists
    layout_id = None
    if data_status['layouts'] == 0:
        layout_model = LayoutModel(db_manager)
        layout_id = create_sample_layout(layout_model)
    else:
        print("📋 Layout already exists, skipping layout creation")
        # Get existing layout ID
        layout_model = LayoutModel(db_manager)
        layouts = layout_model.get_all_layouts()
        layout_id = layouts[0]['layout_id'] if layouts else None
    
    # Create responses if none exist
    if data_status['responses'] == 0 and layout_id:
        response_model = ResponseModel(db_manager)
        create_sample_responses(response_model, layout_id, num_students=50)
    else:
        print("📝 Responses already exist, skipping response creation")
    
    # Create student counts if none exist
    if data_status['student_counts'] == 0:
        student_count_model = StudentCountModel(db_manager)
        create_sample_student_counts(student_count_model)
    else:
        print("📊 Student counts already exist, skipping student count creation")
    
    # Final verification
    print("\n🔍 Final data verification...")
    final_status = check_existing_data(db_manager)
    
    print(f"\n🎉 Sample data loading completed!")
    print(f"📋 Total layouts: {final_status['layouts']}")
    print(f"📝 Total responses: {final_status['responses']}")
    print(f"📊 Total student counts: {final_status['student_counts']}")
    
    if final_status['responses'] > 0:
        print(f"\n🌐 Your dashboard is ready! Visit:")
        print(f"   - Main Dashboard: http://127.0.0.1:5000")
        print(f"   - Maintenance Page: http://127.0.0.1:5000/maintenance")
        print(f"   - Layout Manager: http://127.0.0.1:5000/layout")


if __name__ == "__main__":
    main()
