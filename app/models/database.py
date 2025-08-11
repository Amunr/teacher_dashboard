"""
Database models and schema definitions.
"""
from typing import Optional, List, Dict, Any
from datetime import date, datetime
from sqlalchemy import (
    create_engine, MetaData, Table, Column, Integer, String, 
    Date, Text, ForeignKey, select, func, insert, delete, update
)
from sqlalchemy.engine import Engine
from sqlalchemy.sql import Select
from contextlib import contextmanager
import json
import logging

logger = logging.getLogger(__name__)


class DatabaseManager:
    """Database connection and operation manager."""
    
    def __init__(self, database_url: str, engine_options: Dict[str, Any] = None):
        """
        Initialize database manager.
        
        Args:
            database_url: Database connection URL
            engine_options: Additional engine configuration options
        """
        self.database_url = database_url
        self.engine_options = engine_options or {}
        self.engine: Optional[Engine] = None
        self.meta: Optional[MetaData] = None
        self._tables_initialized = False
        
    def initialize_database(self) -> None:
        """Initialize database engine and create tables."""
        try:
            self.engine = create_engine(
                self.database_url, 
                echo=False,
                **self.engine_options
            )
            self.meta = MetaData()
            self._create_tables()
            self.meta.create_all(self.engine)
            self._tables_initialized = True
            logger.info("Database initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize database: {e}")
            raise
    
    def _create_tables(self) -> None:
        """Define database table schemas."""
        # SubDomains table
        self.subdomains_table = Table(
            'subDomains', self.meta,
            Column('id', Integer, primary_key=True),
            Column('year_start', Date),
            Column('year_end', Date),
            Column('Domain', String(255)),
            Column('SubDomain', String(255)),
        )
        
        # Questions table
        self.questions_table = Table(
            'questions', self.meta,
            Column('id', Integer, primary_key=True),
            Column('year_start', Date),
            Column('year_end', Date),
            Column('Domain', String(255)),
            Column('SubDomain', String(255)),
            Column('Index_ID', Integer),
            Column('Name', Text),
            Column('Date edited', Date),
            Column('layout_id', Integer),
            Column('layout_name', String(255))
        )
        
        # Responses table
        self.responses_table = Table(
            'responses', self.meta,
            Column('id', Integer, primary_key=True),
            Column('res-id', Integer),
            Column('School', String(255)),
            Column('Grade', String(50)),
            Column('Teacher', String(255)),
            Column('Assessment', String(255)),
            Column('Name', String(255)),
            Column('Date', Date),
            Column('Index_ID', Integer),
            Column('Response', Integer)
        )
        
        # Student counts table for manual total student entries
        self.student_counts_table = Table(
            'student_counts', self.meta,
            Column('id', Integer, primary_key=True),
            Column('start_date', Date, nullable=False),
            Column('end_date', Date, nullable=False),
            Column('total_students', Integer, nullable=False),
            Column('description', String(255))
        )
        
        # Google Sheets configuration table
        self.sheets_config_table = Table(
            'sheets_config', self.meta,
            Column('id', Integer, primary_key=True),
            Column('sheet_url', Text, nullable=False),
            Column('last_row_processed', Integer, nullable=False, default=0),
            Column('poll_interval', Integer, nullable=False, default=30),  # minutes
            Column('is_active', Integer, nullable=False, default=1),  # boolean
            Column('created_at', Date, nullable=False),
            Column('updated_at', Date, nullable=False)
        )
        
        # Failed sheet imports table
        self.failed_imports_table = Table(
            'failed_imports', self.meta,
            Column('id', Integer, primary_key=True),
            Column('sheet_row_number', Integer, nullable=False),
            Column('raw_row_data', Text, nullable=False),  # JSON string of the raw row
            Column('error_message', Text, nullable=False),
            Column('failed_at', Date, nullable=False),
            Column('retry_count', Integer, nullable=False, default=0),
            Column('is_resolved', Integer, nullable=False, default=0)  # boolean
        )
    
    @contextmanager
    def get_connection(self):
        """Get database connection with proper cleanup."""
        if not self._tables_initialized:
            raise RuntimeError("Database not initialized. Call initialize_database() first.")
        
        conn = self.engine.connect()
        try:
            yield conn
        except Exception as e:
            logger.error(f"Database operation failed: {e}")
            conn.rollback()
            raise
        finally:
            conn.close()
    
    def health_check(self) -> bool:
        """Check if database connection is healthy."""
        try:
            with self.get_connection() as conn:
                conn.execute(select(1))
            return True
        except Exception as e:
            logger.error(f"Database health check failed: {e}")
            return False


class LayoutModel:
    """Model for layout operations."""
    
    def __init__(self, db_manager: DatabaseManager):
        self.db = db_manager
    
    def get_all_layouts(self) -> List[Dict[str, Any]]:
        """
        Fetch all layouts with metadata.
        
        Returns:
            List of layout dictionaries with id, name, date_edited, is_current
        """
        try:
            with self.db.get_connection() as conn:
                today = date.today()
                
                query = select(
                    self.db.questions_table.c.layout_id,
                    self.db.questions_table.c.layout_name,
                    func.max(self.db.questions_table.c['Date edited']).label('date_edited'),
                    func.max(self.db.questions_table.c.year_end).label('year_end'),
                    func.min(self.db.questions_table.c.year_start).label('year_start')
                ).group_by(
                    self.db.questions_table.c.layout_id, 
                    self.db.questions_table.c.layout_name
                )
                
                result = conn.execute(query).mappings().all()
                
                if not result:
                    return []
                
                layouts = []
                current_layout_id = None
                
                # Find the layout that is currently active (today's date falls within its range)
                for row in result:
                    year_start = row['year_start']
                    year_end = row['year_end']
                    is_current = False
                    
                    if year_start and year_end:
                        is_current = year_start <= today <= year_end
                        if is_current:
                            current_layout_id = row['layout_id']
                    
                    layouts.append({
                        'layout_id': row['layout_id'],
                        'layout_name': row['layout_name'],
                        'date_edited': str(row['date_edited']) if row['date_edited'] else '',
                        'year_start': str(year_start) if year_start else '',
                        'year_end': str(year_end) if year_end else '',
                        'is_current': is_current
                    })
                
                # If no layout is current based on date range, mark the one with latest year_end as current
                if current_layout_id is None and layouts:
                    max_year_end = max(
                        [l['year_end'] for l in layouts if l['year_end']], 
                        default=None
                    )
                    for layout in layouts:
                        if layout['year_end'] == max_year_end:
                            layout['is_current'] = True
                            current_layout_id = layout['layout_id']
                            break
                
                # Sort layouts: current layout first, then by year_end descending
                layouts.sort(key=lambda x: (not x['is_current'], x['year_end'] or ''), reverse=True)
                
                return layouts
                
        except Exception as e:
            logger.error(f"Failed to fetch layouts: {e}")
            raise
    
    def get_layout_by_id(self, layout_id: int) -> Optional[Dict[str, Any]]:
        """
        Get layout data for Jinja2 template rendering.
        
        Args:
            layout_id: Layout identifier
            
        Returns:
            Layout data dictionary or None if not found
        """
        try:
            questions = self.get_questions_by_layout(layout_id)
            if not questions:
                return None
            
            layout_name = questions[0].get('layout_name', f'Layout #{layout_id}')
            
            # Find min/max year_start/year_end
            year_starts = [q['year_start'] for q in questions if q['year_start']]
            year_ends = [q['year_end'] for q in questions if q['year_end']]
            year_start = min(year_starts) if year_starts else ''
            year_end = max(year_ends) if year_ends else ''
            
            # Group domains/subdomains/questions
            domains = {}
            metadata_list = []
            
            for q in questions:
                if q['Domain'] == 'MetaData':
                    metadata_list.append({
                        'id': q['id'],
                        'name': q['Name'],
                        'question_id': q['Index_ID']
                    })
                else:
                    domain_name = q['Domain']
                    subdomain_name = q['SubDomain']
                    
                    if domain_name not in domains:
                        domains[domain_name] = {}
                    if subdomain_name not in domains[domain_name]:
                        domains[domain_name][subdomain_name] = []
                    
                    domains[domain_name][subdomain_name].append({
                        'id': q['id'],
                        'name': q['Name'],
                        'question_id': q['Index_ID']
                    })
            
            # Convert to list structure
            domain_list = []
            for domain_name, subdomains in domains.items():
                subdomain_list = []
                for subdomain_name, questions_list in subdomains.items():
                    subdomain_list.append({
                        'id': hash(subdomain_name),
                        'name': subdomain_name,
                        'questions': questions_list
                    })
                domain_list.append({
                    'id': hash(domain_name),
                    'name': domain_name,
                    'subdomains': subdomain_list
                })
            
            return {
                'layout_name': layout_name,
                'layout_id': layout_id,
                'domains': domain_list,
                'metadata_list': metadata_list,
                'layout_start_date': str(year_start),
                'layout_end_date': str(year_end)
            }
            
        except Exception as e:
            logger.error(f"Failed to get layout {layout_id}: {e}")
            raise
    
    def get_questions_by_layout(self, layout_id: int) -> List[Dict[str, Any]]:
        """
        Get all questions for a specific layout.
        
        Args:
            layout_id: Layout identifier
            
        Returns:
            List of question dictionaries
        """
        try:
            with self.db.get_connection() as conn:
                query = select(self.db.questions_table).where(
                    self.db.questions_table.c.layout_id == layout_id
                )
                result = conn.execute(query).fetchall()
                return [dict(row._mapping) for row in result]
                
        except Exception as e:
            logger.error(f"Failed to get questions for layout {layout_id}: {e}")
            raise
    
    def create_layout(self, layout_data: List[Dict[str, Any]]) -> int:
        """
        Create a new layout.
        
        Args:
            layout_data: List of question/metadata dictionaries
            
        Returns:
            New layout ID
        """
        try:
            with self.db.get_connection() as conn:
                # Get next layout ID
                max_query = select(func.max(self.db.questions_table.c.layout_id))
                result = conn.execute(max_query).fetchone()
                layout_id = (result[0] + 1) if result[0] is not None else 1
                
                # Prepare insert data
                values = []
                for item in layout_data:
                    values.append({
                        'year_start': self._parse_date(item.get('year_start')),
                        'year_end': self._parse_date(item.get('year_end')),
                        'Domain': item.get('Domain'),
                        'SubDomain': item.get('SubDomain'),
                        'Index_ID': item.get('Index_ID'),
                        'Name': item.get('Name'),
                        'Date edited': self._parse_date(item.get('Date edited')),
                        'layout_id': layout_id,
                        'layout_name': item.get('layout_name')
                    })
                
                if values:
                    conn.execute(insert(self.db.questions_table), values)
                    conn.commit()
                
                logger.info(f"Created layout {layout_id} with {len(values)} items")
                return layout_id
                
        except Exception as e:
            logger.error(f"Failed to create layout: {e}")
            raise
    
    def update_layout_inplace(self, layout_id: int, layout_data: List[Dict[str, Any]]) -> None:
        """
        Update existing layout by replacing all its data.
        
        Args:
            layout_id: Layout identifier
            layout_data: New layout data
        """
        try:
            with self.db.get_connection() as conn:
                # Delete existing data
                delete_query = delete(self.db.questions_table).where(
                    self.db.questions_table.c.layout_id == layout_id
                )
                conn.execute(delete_query)
                
                # Insert new data
                values = []
                for item in layout_data:
                    values.append({
                        'year_start': self._parse_date(item.get('year_start')),
                        'year_end': self._parse_date(item.get('year_end')),
                        'Domain': item.get('Domain'),
                        'SubDomain': item.get('SubDomain'),
                        'Index_ID': item.get('Index_ID'),
                        'Name': item.get('Name'),
                        'Date edited': self._parse_date(item.get('Date edited')),
                        'layout_id': layout_id,
                        'layout_name': item.get('layout_name')
                    })
                
                if values:
                    conn.execute(insert(self.db.questions_table), values)
                
                conn.commit()
                logger.info(f"Updated layout {layout_id} with {len(values)} items")
                
        except Exception as e:
            logger.error(f"Failed to update layout {layout_id}: {e}")
            raise
    
    def delete_layout(self, layout_id: int) -> None:
        """
        Delete a layout and all its data.
        
        Args:
            layout_id: Layout identifier
        """
        try:
            with self.db.get_connection() as conn:
                delete_query = delete(self.db.questions_table).where(
                    self.db.questions_table.c.layout_id == layout_id
                )
                conn.execute(delete_query)
                conn.commit()
                logger.info(f"Deleted layout {layout_id}")
                
        except Exception as e:
            logger.error(f"Failed to delete layout {layout_id}: {e}")
            raise
    
    @staticmethod
    def _parse_date(date_value: Any) -> Optional[date]:
        """Parse date value from various formats."""
        if isinstance(date_value, str):
            try:
                return datetime.strptime(date_value, "%Y-%m-%d").date()
            except (ValueError, TypeError):
                return None
        elif isinstance(date_value, date):
            return date_value
        return None
    
    @staticmethod
    def get_empty_layout() -> Dict[str, Any]:
        """Get empty layout structure for new layout creation."""
        return {
            'layout_name': '',
            'layout_id': '',
            'domains': [],
            'metadata_list': [
                {'id': 1, 'name': 'Date', 'question_id': 0},
                {'id': 2, 'name': 'Student Name', 'question_id': 0},
                {'id': 3, 'name': 'School', 'question_id': 0},
                {'id': 4, 'name': 'Teacher Name', 'question_id': 0},
                {'id': 5, 'name': 'Assessment Type', 'question_id': 0},
                {'id': 6, 'name': 'Grade', 'question_id': 0},
            ],
            'layout_start_date': '',
            'layout_end_date': ''
        }


class ResponseModel:
    """Model for response operations."""
    
    def __init__(self, db_manager: DatabaseManager):
        self.db = db_manager
    
    def create_response(self, response_data: Dict[str, Any]) -> int:
        """
        Create a new response record.
        
        Args:
            response_data: Response data dictionary
            
        Returns:
            The created res_id
        """
        try:
            with self.db.get_connection() as conn:
                today = date.today()
                
                if isinstance(response_data, str):
                    data = json.loads(response_data)
                else:
                    data = response_data
                
                # Get next response ID
                max_query = select(func.max(self.db.responses_table.c['res-id']))
                result = conn.execute(max_query).fetchone()
                next_res_id = (result[0] + 1) if result[0] is not None else 1
                
                # Get valid Index_IDs for today's date
                valid_query = select(self.db.questions_table).where(
                    (self.db.questions_table.c.year_start <= today) &
                    (self.db.questions_table.c.year_end >= today) &
                    (self.db.questions_table.c.Domain != "MetaData")
                ).distinct()
                valid_questions = conn.execute(valid_query).fetchall()
                valid_index_set = {row.Index_ID for row in valid_questions}
                
                # Map metadata elements to their Index_IDs
                meta_elements = ["School", "Grade", "Teacher", "Assessment", "Name", "Date"]
                meta_query = select(self.db.questions_table).where(
                    (self.db.questions_table.c.year_start <= today) &
                    (self.db.questions_table.c.year_end >= today) &
                    (self.db.questions_table.c.SubDomain.in_(meta_elements))
                ).distinct()
                meta_rows = conn.execute(meta_query).fetchall()
                
                # Map SubDomain to Index_ID
                meta_index_map = {row.Index_ID: row.SubDomain for row in meta_rows}
                
                # Extract metadata values
                school_index = next((k for k, v in meta_index_map.items() if v == "School"), None)
                grade_index = next((k for k, v in meta_index_map.items() if v == "Grade"), None)
                teacher_index = next((k for k, v in meta_index_map.items() if v == "Teacher"), None)
                assessment_index = next((k for k, v in meta_index_map.items() if v == "Assessment"), None)
                name_index = next((k for k, v in meta_index_map.items() if v == "Name"), None)
                date_index = next((k for k, v in meta_index_map.items() if v == "Date"), None)
                
                school = data.get(school_index, '')
                grade = data.get(grade_index, '')
                teacher = data.get(teacher_index, '')
                assessment = data.get(assessment_index, '')
                name = data.get(name_index, '')
                date_val = data.get(date_index, '')
                
                # Prepare response records
                values_list = []
                for index, value in enumerate(data):
                    index_id = index + 1
                    
                    if index_id in valid_index_set:
                        values_list.append({
                            'res-id': next_res_id,
                            'School': school,
                            'Grade': grade,
                            'Teacher': teacher,
                            'Assessment': assessment,
                            'Name': name,
                            'Date': date_val,
                            'Index_ID': index_id,
                            'Response': value
                        })
                
                if values_list:
                    conn.execute(insert(self.db.responses_table), values_list)
                    conn.commit()
                    logger.info(f"Created response {next_res_id} with {len(values_list)} items")
                
                return next_res_id
                
        except Exception as e:
            logger.error(f"Failed to create response: {e}")
            raise
    
    def get_responses(self, filters: Dict[str, Any] = None, limit: int = None, offset: int = None) -> List[Dict[str, Any]]:
        """
        Get responses with optional filtering.
        
        Args:
            filters: Dictionary of filter criteria
            limit: Maximum number of records to return
            offset: Number of records to skip
            
        Returns:
            List of response dictionaries
        """
        try:
            with self.db.get_connection() as conn:
                # Join responses with questions to get domain/subdomain info
                query = select(
                    self.db.responses_table.c['res-id'],
                    self.db.responses_table.c.School,
                    self.db.responses_table.c.Grade,
                    self.db.responses_table.c.Teacher,
                    self.db.responses_table.c.Assessment,
                    self.db.responses_table.c.Name,
                    self.db.responses_table.c.Date,
                    self.db.responses_table.c.Index_ID,
                    self.db.responses_table.c.Response,
                    self.db.questions_table.c.Domain,
                    self.db.questions_table.c.SubDomain,
                    self.db.questions_table.c.Name.label('Question_Name')
                ).select_from(
                    self.db.responses_table.join(
                        self.db.questions_table,
                        self.db.responses_table.c.Index_ID == self.db.questions_table.c.Index_ID
                    )
                )
                
                # Apply filters
                if filters:
                    if 'school' in filters and filters['school']:
                        query = query.where(self.db.responses_table.c.School.ilike(f"%{filters['school']}%"))
                    if 'grade' in filters and filters['grade']:
                        query = query.where(self.db.responses_table.c.Grade.ilike(f"%{filters['grade']}%"))
                    if 'teacher' in filters and filters['teacher']:
                        query = query.where(self.db.responses_table.c.Teacher.ilike(f"%{filters['teacher']}%"))
                    if 'assessment' in filters and filters['assessment']:
                        query = query.where(self.db.responses_table.c.Assessment.ilike(f"%{filters['assessment']}%"))
                    if 'student_name' in filters and filters['student_name']:
                        query = query.where(self.db.responses_table.c.Name.ilike(f"%{filters['student_name']}%"))
                    if 'domain' in filters and filters['domain']:
                        query = query.where(self.db.questions_table.c.Domain.ilike(f"%{filters['domain']}%"))
                    if 'start_date' in filters and filters['start_date']:
                        query = query.where(self.db.responses_table.c.Date >= filters['start_date'])
                    if 'end_date' in filters and filters['end_date']:
                        query = query.where(self.db.responses_table.c.Date <= filters['end_date'])
                
                # Add ordering
                query = query.order_by(self.db.responses_table.c.Date.desc(), self.db.responses_table.c['res-id'].desc())
                
                # Apply pagination
                if limit:
                    query = query.limit(limit)
                if offset:
                    query = query.offset(offset)
                
                result = conn.execute(query).fetchall()
                return [dict(row._mapping) for row in result]
                
        except Exception as e:
            logger.error(f"Failed to get responses: {e}")
            raise
    
    def get_dashboard_data(self, filters: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Get aggregated data for dashboard display.
        
        Args:
            filters: Dictionary of filter criteria
            
        Returns:
            Dashboard data dictionary
        """
        try:
            with self.db.get_connection() as conn:
                today = date.today()
                
                # Set default date range to last 365 days if not provided
                if not filters:
                    filters = {}
                if 'start_date' not in filters:
                    filters['start_date'] = date(today.year - 1, today.month, today.day)
                if 'end_date' not in filters:
                    filters['end_date'] = today
                
                # Build base query for valid responses
                base_query = select(
                    self.db.responses_table.c['res-id'],
                    self.db.responses_table.c.Date,
                    self.db.responses_table.c.Response,
                    self.db.questions_table.c.Domain,
                    self.db.questions_table.c.SubDomain
                ).select_from(
                    self.db.responses_table.join(
                        self.db.questions_table,
                        (self.db.responses_table.c.Index_ID == self.db.questions_table.c.Index_ID) &
                        (self.db.responses_table.c.Date >= self.db.questions_table.c.year_start) &
                        (self.db.responses_table.c.Date <= self.db.questions_table.c.year_end) &
                        (self.db.questions_table.c.Domain != "MetaData")
                    )
                )
                
                # Apply filters to base query
                if filters.get('school'):
                    base_query = base_query.where(self.db.responses_table.c.School.ilike(f"%{filters['school']}%"))
                if filters.get('grade'):
                    base_query = base_query.where(self.db.responses_table.c.Grade.ilike(f"%{filters['grade']}%"))
                if filters.get('teacher'):
                    base_query = base_query.where(self.db.responses_table.c.Teacher.ilike(f"%{filters['teacher']}%"))
                if filters.get('assessment'):
                    base_query = base_query.where(self.db.responses_table.c.Assessment.ilike(f"%{filters['assessment']}%"))
                if filters.get('student_name'):
                    base_query = base_query.where(self.db.responses_table.c.Name.ilike(f"%{filters['student_name']}%"))
                if filters.get('domain'):
                    base_query = base_query.where(self.db.questions_table.c.Domain.ilike(f"%{filters['domain']}%"))
                if filters.get('start_date'):
                    base_query = base_query.where(self.db.responses_table.c.Date >= filters['start_date'])
                if filters.get('end_date'):
                    base_query = base_query.where(self.db.responses_table.c.Date <= filters['end_date'])
                
                responses = conn.execute(base_query).fetchall()
                
                if not responses:
                    return {
                        'total_students_assessed': 0,
                        'total_students': 0,
                        'average_score': 0,
                        'glowing_skills': [],
                        'growing_skills': [],
                        'domain_scores': [],
                        'subdomain_scores': []
                    }
                
                # Convert rows to dictionaries for easier access
                response_dicts = []
                for row in responses:
                    response_dict = {
                        'res-id': row[0],
                        'Date': row[1],
                        'Response': row[2],
                        'Domain': row[3],
                        'SubDomain': row[4]
                    }
                    response_dicts.append(response_dict)
                
                # Calculate metrics
                unique_res_ids = set(r['res-id'] for r in response_dicts)
                total_students_assessed = len(unique_res_ids)
                
                # Get manual total student count for date range
                total_students = self._get_total_students_for_date_range(
                    conn, filters['start_date'], filters['end_date']
                )
                
                # Calculate scores by res_id
                res_scores = {}
                res_question_counts = {}
                for response in response_dicts:
                    res_id = response['res-id']
                    if res_id not in res_scores:
                        res_scores[res_id] = 0
                        res_question_counts[res_id] = 0
                    
                    # Convert response to numeric value (handle both characters and numbers)
                    response_value = self._convert_response_to_numeric(response['Response'])
                    res_scores[res_id] += response_value
                    res_question_counts[res_id] += 1
                
                # Calculate percentage scores (scale 0-1, so percentage is just * 100)
                student_scores = []
                for res_id in res_scores:
                    if res_question_counts[res_id] > 0:
                        avg_score = res_scores[res_id] / res_question_counts[res_id]
                        percent_score = avg_score * 100  # Convert 0-1 scale to percentage
                        student_scores.append(percent_score)
                
                average_score = sum(student_scores) / len(student_scores) if student_scores else 0
                
                # Calculate school readiness: students scoring >80% in ALL domains
                school_ready_students = 0
                
                # Get unique domains from responses
                all_domains = set(response['Domain'] for response in response_dicts)
                
                # For each student, calculate their score in each domain
                for res_id in res_scores:
                    student_domain_scores = {}
                    
                    # Calculate domain averages for this student
                    for response in response_dicts:
                        if response['res-id'] == res_id:
                            domain = response['Domain']
                            if domain not in student_domain_scores:
                                student_domain_scores[domain] = []
                            # Convert response to numeric value
                            response_value = self._convert_response_to_numeric(response['Response'])
                            student_domain_scores[domain].append(response_value)
                    
                    # Check if student scores >80% in ALL domains
                    is_school_ready = True
                    for domain in all_domains:
                        if domain in student_domain_scores:
                            domain_avg = sum(student_domain_scores[domain]) / len(student_domain_scores[domain])
                            domain_percent = domain_avg * 100  # Convert 0-1 scale to percentage
                            if domain_percent <= 80:
                                is_school_ready = False
                                break
                        else:
                            # Student has no responses in this domain
                            is_school_ready = False
                            break
                    
                    if is_school_ready:
                        school_ready_students += 1
                
                # Calculate school readiness percentage
                school_readiness_percent = (school_ready_students / total_students_assessed * 100) if total_students_assessed > 0 else 0
                
                # Calculate domain averages
                domain_data = {}
                for response in response_dicts:
                    domain = response['Domain']
                    if domain not in domain_data:
                        domain_data[domain] = []
                    # Convert response to numeric value
                    response_value = self._convert_response_to_numeric(response['Response'])
                    domain_data[domain].append(response_value)
                
                domain_scores = []
                for domain, scores in domain_data.items():
                    avg_score = sum(scores) / len(scores) if scores else 0
                    percent_score = avg_score * 100  # Convert 0-1 scale to percentage
                    domain_scores.append({'domain': domain, 'score': round(percent_score, 1)})
                
                domain_scores.sort(key=lambda x: x['score'], reverse=True)
                
                # Get glowing and growing skills
                glowing_skills = domain_scores[:2] if len(domain_scores) >= 2 else domain_scores
                growing_skills = domain_scores[-2:] if len(domain_scores) >= 2 else []
                
                # Calculate subdomain scores if domain filter is applied
                subdomain_scores = []
                if filters.get('domain'):
                    subdomain_data = {}
                    for response in response_dicts:
                        if response['Domain'].lower() == filters['domain'].lower():
                            subdomain = response['SubDomain']
                            if subdomain not in subdomain_data:
                                subdomain_data[subdomain] = []
                            # Convert response to numeric value
                            response_value = self._convert_response_to_numeric(response['Response'])
                            subdomain_data[subdomain].append(response_value)
                    
                    for subdomain, scores in subdomain_data.items():
                        avg_score = sum(scores) / len(scores) if scores else 0
                        percent_score = avg_score * 100  # Convert 0-1 scale to percentage
                        subdomain_scores.append({'subdomain': subdomain, 'score': round(percent_score, 1)})
                    
                    subdomain_scores.sort(key=lambda x: x['score'], reverse=True)
                
                return {
                    'total_students_assessed': total_students_assessed,
                    'total_students': total_students,
                    'average_score': round(average_score, 1),
                    'school_readiness_percent': round(school_readiness_percent, 1),
                    'glowing_skills': glowing_skills,
                    'growing_skills': growing_skills,
                    'domain_scores': domain_scores,
                    'subdomain_scores': subdomain_scores
                }
                
        except Exception as e:
            logger.error(f"Failed to get dashboard data: {e}")
            raise
    
    def delete_responses(self, res_ids: List[int]) -> int:
        """
        Delete responses by res_id.
        
        Args:
            res_ids: List of res_id values to delete
            
        Returns:
            Number of deleted records
        """
        try:
            with self.db.get_connection() as conn:
                delete_query = delete(self.db.responses_table).where(
                    self.db.responses_table.c['res-id'].in_(res_ids)
                )
                result = conn.execute(delete_query)
                conn.commit()
                
                deleted_count = result.rowcount
                logger.info(f"Deleted {deleted_count} response records for res_ids: {res_ids}")
                return deleted_count
                
        except Exception as e:
            logger.error(f"Failed to delete responses: {e}")
            raise
    
    def get_orphaned_responses(self) -> List[Dict[str, Any]]:
        """
        Get responses that don't have valid question mappings for their dates.
        
        Returns:
            List of orphaned response dictionaries
        """
        try:
            with self.db.get_connection() as conn:
                # Find responses without valid question mappings
                query = select(self.db.responses_table).where(
                    ~self.db.responses_table.c.Index_ID.in_(
                        select(self.db.questions_table.c.Index_ID).where(
                            (self.db.responses_table.c.Date >= self.db.questions_table.c.year_start) &
                            (self.db.responses_table.c.Date <= self.db.questions_table.c.year_end)
                        )
                    )
                )
                
                result = conn.execute(query).fetchall()
                return [dict(row._mapping) for row in result]
                
        except Exception as e:
            logger.error(f"Failed to get orphaned responses: {e}")
            raise
    
    def get_filter_options(self) -> Dict[str, List[str]]:
        """
        Get available filter options for the dashboard.
        
        Returns:
            Dictionary with lists of available filter values
        """
        try:
            with self.db.get_connection() as conn:
                options = {}
                
                # Get distinct values for each filter field
                for field in ['School', 'Grade', 'Teacher', 'Assessment', 'Name']:
                    query = select(self.db.responses_table.c[field]).distinct().where(
                        self.db.responses_table.c[field].isnot(None) &
                        (self.db.responses_table.c[field] != '')
                    ).order_by(self.db.responses_table.c[field])
                    
                    result = conn.execute(query).fetchall()
                    options[field.lower()] = [row[0] for row in result if row[0]]
                
                # Get distinct domains
                domain_query = select(self.db.questions_table.c.Domain).distinct().where(
                    (self.db.questions_table.c.Domain.isnot(None)) &
                    (self.db.questions_table.c.Domain != '') &
                    (self.db.questions_table.c.Domain != 'MetaData')
                ).order_by(self.db.questions_table.c.Domain)
                
                result = conn.execute(domain_query).fetchall()
                options['domain'] = [row[0] for row in result if row[0]]
                
                return options
                
        except Exception as e:
            logger.error(f"Failed to get filter options: {e}")
            raise
    
    def _get_total_students_for_date_range(self, conn, start_date: date, end_date: date) -> int:
        """
        Get manual total student count for a date range.
        
        Args:
            conn: Database connection
            start_date: Start date
            end_date: End date
            
        Returns:
            Total student count
        """
        try:
            query = select(self.db.student_counts_table.c.total_students).where(
                (self.db.student_counts_table.c.start_date <= start_date) &
                (self.db.student_counts_table.c.end_date >= end_date)
            ).order_by(self.db.student_counts_table.c.end_date.desc()).limit(1)
            
            result = conn.execute(query).fetchone()
            return result[0] if result else 0
            
        except Exception as e:
            logger.warning(f"Failed to get total student count: {e}")
            return 0
    
    def _convert_response_to_numeric(self, response_value: Any) -> float:
        """
        Convert response value to numeric score.
        Response values should already be numeric (0, 0.5, 1) from the database.
        
        Args:
            response_value: Response value (should be numeric)
            
        Returns:
            Numeric score value (0, 0.5, or 1)
        """
        # If already a number, return it
        if isinstance(response_value, (int, float)):
            return float(response_value)
        
        # Try to parse as number
        if isinstance(response_value, str):
            try:
                return float(response_value)
            except (ValueError, TypeError):
                # Default to 0 for invalid responses
                return 0.0
        
        # Default for any other type
        return 0.0


class StudentCountModel:
    """Model for student count operations."""
    
    def __init__(self, db_manager: DatabaseManager):
        self.db = db_manager
    
    def create_student_count(self, start_date: date, end_date: date, total_students: int, description: str = None) -> int:
        """
        Create a new student count entry.
        
        Args:
            start_date: Start date of the range
            end_date: End date of the range
            total_students: Total number of students
            description: Optional description
            
        Returns:
            Created record ID
        """
        try:
            with self.db.get_connection() as conn:
                insert_query = insert(self.db.student_counts_table).values(
                    start_date=start_date,
                    end_date=end_date,
                    total_students=total_students,
                    description=description
                )
                
                result = conn.execute(insert_query)
                conn.commit()
                
                logger.info(f"Created student count entry: {total_students} students from {start_date} to {end_date}")
                return result.inserted_primary_key[0]
                
        except Exception as e:
            logger.error(f"Failed to create student count: {e}")
            raise
    
    def get_all_student_counts(self) -> List[Dict[str, Any]]:
        """
        Get all student count entries.
        
        Returns:
            List of student count dictionaries
        """
        try:
            with self.db.get_connection() as conn:
                query = select(self.db.student_counts_table).order_by(
                    self.db.student_counts_table.c.end_date.desc()
                )
                result = conn.execute(query).fetchall()
                return [dict(row._mapping) for row in result]
                
        except Exception as e:
            logger.error(f"Failed to get student counts: {e}")
            raise
    
    def update_student_count(self, count_id: int, start_date: date, end_date: date, total_students: int, description: str = None) -> None:
        """
        Update a student count entry.
        
        Args:
            count_id: ID of the record to update
            start_date: Start date of the range
            end_date: End date of the range
            total_students: Total number of students
            description: Optional description
        """
        try:
            with self.db.get_connection() as conn:
                update_query = update(self.db.student_counts_table).where(
                    self.db.student_counts_table.c.id == count_id
                ).values(
                    start_date=start_date,
                    end_date=end_date,
                    total_students=total_students,
                    description=description,
                    updated_at=date.today()
                )
                
                conn.execute(update_query)
                conn.commit()
                
                logger.info(f"Updated student count entry {count_id}")
                
        except Exception as e:
            logger.error(f"Failed to update student count {count_id}: {e}")
            raise
    
    def delete_student_count(self, count_id: int) -> None:
        """
        Delete a student count entry.
        
        Args:
            count_id: ID of the record to delete
        """
        try:
            with self.db.get_connection() as conn:
                delete_query = delete(self.db.student_counts_table).where(
                    self.db.student_counts_table.c.id == count_id
                )
                conn.execute(delete_query)
                conn.commit()
                
                logger.info(f"Deleted student count entry {count_id}")
                
        except Exception as e:
            logger.error(f"Failed to delete student count {count_id}: {e}")
            raise


class SheetsConfigModel:
    """Model for Google Sheets configuration operations."""
    
    def __init__(self, db_manager: DatabaseManager):
        self.db = db_manager
    
    def get_config(self) -> Optional[Dict[str, Any]]:
        """
        Get the current Google Sheets configuration.
        
        Returns:
            Configuration dictionary or None if not found
        """
        try:
            with self.db.get_connection() as conn:
                query = select(self.db.sheets_config_table).where(
                    self.db.sheets_config_table.c.is_active == 1
                ).order_by(self.db.sheets_config_table.c.updated_at.desc()).limit(1)
                
                result = conn.execute(query).fetchone()
                return dict(result._mapping) if result else None
                
        except Exception as e:
            logger.error(f"Failed to get sheets config: {e}")
            raise
    
    def create_or_update_config(self, sheet_url: str, poll_interval: int = 30) -> int:
        """
        Create or update Google Sheets configuration.
        
        Args:
            sheet_url: Google Sheets URL
            poll_interval: Polling interval in minutes
            
        Returns:
            Configuration ID
        """
        try:
            with self.db.get_connection() as conn:
                today = date.today()
                
                # Check if config exists
                existing = self.get_config()
                
                if existing:
                    # Update existing config
                    update_query = update(self.db.sheets_config_table).where(
                        self.db.sheets_config_table.c.id == existing['id']
                    ).values(
                        sheet_url=sheet_url,
                        poll_interval=poll_interval,
                        updated_at=today
                    )
                    conn.execute(update_query)
                    conn.commit()
                    logger.info(f"Updated sheets config {existing['id']}")
                    return existing['id']
                else:
                    # Create new config
                    insert_query = insert(self.db.sheets_config_table).values(
                        sheet_url=sheet_url,
                        last_row_processed=0,
                        poll_interval=poll_interval,
                        is_active=1,
                        created_at=today,
                        updated_at=today
                    )
                    result = conn.execute(insert_query)
                    conn.commit()
                    config_id = result.inserted_primary_key[0]
                    logger.info(f"Created new sheets config {config_id}")
                    return config_id
                    
        except Exception as e:
            logger.error(f"Failed to create/update sheets config: {e}")
            raise
    
    def update_last_row_processed(self, last_row: int) -> None:
        """
        Update the last processed row number.
        
        Args:
            last_row: Last row number that was successfully processed
        """
        try:
            with self.db.get_connection() as conn:
                config = self.get_config()
                if not config:
                    raise ValueError("No active sheets configuration found")
                
                update_query = update(self.db.sheets_config_table).where(
                    self.db.sheets_config_table.c.id == config['id']
                ).values(
                    last_row_processed=last_row,
                    updated_at=date.today()
                )
                conn.execute(update_query)
                conn.commit()
                logger.info(f"Updated last row processed to {last_row}")
                
        except Exception as e:
            logger.error(f"Failed to update last row processed: {e}")
            raise
    
    def deactivate_config(self) -> None:
        """Deactivate the current configuration."""
        try:
            with self.db.get_connection() as conn:
                config = self.get_config()
                if config:
                    update_query = update(self.db.sheets_config_table).where(
                        self.db.sheets_config_table.c.id == config['id']
                    ).values(
                        is_active=0,
                        updated_at=date.today()
                    )
                    conn.execute(update_query)
                    conn.commit()
                    logger.info(f"Deactivated sheets config {config['id']}")
                    
        except Exception as e:
            logger.error(f"Failed to deactivate sheets config: {e}")
            raise


class FailedImportsModel:
    """Model for managing failed Google Sheets imports."""
    
    def __init__(self, db_manager: DatabaseManager):
        self.db = db_manager
    
    def create_failed_import(self, sheet_row_number: int, raw_row_data: List[str], error_message: str) -> int:
        """
        Record a failed import attempt.
        
        Args:
            sheet_row_number: Row number in the Google Sheet
            raw_row_data: List of raw cell values from the sheet
            error_message: Error description
            
        Returns:
            Created record ID
        """
        try:
            with self.db.get_connection() as conn:
                insert_query = insert(self.db.failed_imports_table).values(
                    sheet_row_number=sheet_row_number,
                    raw_row_data=json.dumps(raw_row_data),
                    error_message=error_message,
                    failed_at=date.today(),
                    retry_count=0,
                    is_resolved=0
                )
                
                result = conn.execute(insert_query)
                conn.commit()
                
                failed_id = result.inserted_primary_key[0]
                logger.warning(f"Created failed import record {failed_id} for sheet row {sheet_row_number}: {error_message}")
                return failed_id
                
        except Exception as e:
            logger.error(f"Failed to create failed import record: {e}")
            raise
    
    def get_failed_imports(self, include_resolved: bool = False) -> List[Dict[str, Any]]:
        """
        Get all failed import records.
        
        Args:
            include_resolved: Whether to include resolved failures
            
        Returns:
            List of failed import dictionaries
        """
        try:
            with self.db.get_connection() as conn:
                query = select(self.db.failed_imports_table)
                
                if not include_resolved:
                    query = query.where(self.db.failed_imports_table.c.is_resolved == 0)
                
                query = query.order_by(self.db.failed_imports_table.c.failed_at.desc())
                
                result = conn.execute(query).fetchall()
                failed_imports = []
                
                for row in result:
                    row_dict = dict(row._mapping)
                    # Parse the JSON raw data
                    row_dict['raw_row_data'] = json.loads(row_dict['raw_row_data'])
                    failed_imports.append(row_dict)
                
                return failed_imports
                
        except Exception as e:
            logger.error(f"Failed to get failed imports: {e}")
            raise
    
    def retry_failed_import(self, failed_import_id: int) -> bool:
        """
        Attempt to retry a failed import by re-fetching the row from Google Sheets.
        
        Args:
            failed_import_id: ID of the failed import to retry
            
        Returns:
            True if retry was successful, False otherwise
        """
        try:
            with self.db.get_connection() as conn:
                # Get the failed import record
                query = select(self.db.failed_imports_table).where(
                    self.db.failed_imports_table.c.id == failed_import_id
                )
                result = conn.execute(query).fetchone()
                
                if not result:
                    raise ValueError(f"Failed import {failed_import_id} not found")
                
                failed_import = dict(result._mapping)
                sheet_row_number = failed_import['sheet_row_number']
                
                # Increment retry count
                update_query = update(self.db.failed_imports_table).where(
                    self.db.failed_imports_table.c.id == failed_import_id
                ).values(
                    retry_count=failed_import['retry_count'] + 1
                )
                conn.execute(update_query)
                conn.commit()
                
                logger.info(f"Incremented retry count for failed import {failed_import_id}")
                return True
                
        except Exception as e:
            logger.error(f"Failed to retry import {failed_import_id}: {e}")
            return False
    
    def mark_resolved(self, failed_import_id: int) -> None:
        """
        Mark a failed import as resolved.
        
        Args:
            failed_import_id: ID of the failed import to mark as resolved
        """
        try:
            with self.db.get_connection() as conn:
                update_query = update(self.db.failed_imports_table).where(
                    self.db.failed_imports_table.c.id == failed_import_id
                ).values(
                    is_resolved=1
                )
                conn.execute(update_query)
                conn.commit()
                
                logger.info(f"Marked failed import {failed_import_id} as resolved")
                
        except Exception as e:
            logger.error(f"Failed to mark import {failed_import_id} as resolved: {e}")
            raise
    
    def delete_failed_import(self, failed_import_id: int) -> None:
        """
        Delete a failed import record.
        
        Args:
            failed_import_id: ID of the failed import to delete
        """
        try:
            with self.db.get_connection() as conn:
                delete_query = delete(self.db.failed_imports_table).where(
                    self.db.failed_imports_table.c.id == failed_import_id
                )
                conn.execute(delete_query)
                conn.commit()
                
                logger.info(f"Deleted failed import {failed_import_id}")
                
        except Exception as e:
            logger.error(f"Failed to delete failed import {failed_import_id}: {e}")
            raise


class SheetsImportService:
    """Service for importing data from Google Sheets."""
    
    # Kannada to numeric conversion mapping
    KANNADA_MAPPINGS = {
        'ಸಾಧಿಸಿದ್ದಾರೆ': 1,
        'ಪ್ರಗತಿಯಲ್ಲಿದ್ದಾರೆ': 0.5,
        'ಕಲಿಯುತ್ತಿದ್ದಾರೆ': 0,
        # English equivalents
        'achieved': 1,
        'in progress': 0.5,
        'learning': 0,
        'accomplished': 1,
        'progressing': 0.5,
        'developing': 0
    }
    
    def __init__(self, db_manager: DatabaseManager):
        self.db = db_manager
        self.response_model = ResponseModel(db_manager)
        self.failed_imports_model = FailedImportsModel(db_manager)
    
    @staticmethod
    def convert_sheets_url_to_csv(sheets_url: str) -> str:
        """
        Convert a Google Sheets URL to CSV export format.
        
        Args:
            sheets_url: Regular Google Sheets URL
            
        Returns:
            CSV export URL
        """
        try:
            import re
            
            # Extract sheet ID from various Google Sheets URL formats
            patterns = [
                r'/spreadsheets/d/([a-zA-Z0-9-_]+)',
                r'key=([a-zA-Z0-9-_]+)',
                r'id=([a-zA-Z0-9-_]+)'
            ]
            
            sheet_id = None
            for pattern in patterns:
                match = re.search(pattern, sheets_url)
                if match:
                    sheet_id = match.group(1)
                    break
            
            if not sheet_id:
                raise ValueError("Could not extract sheet ID from URL")
            
            csv_url = f"https://docs.google.com/spreadsheets/d/{sheet_id}/gviz/tq?tqx=out:csv"
            logger.info(f"Converted sheets URL to CSV: {csv_url}")
            return csv_url
            
        except Exception as e:
            logger.error(f"Failed to convert sheets URL: {e}")
            raise
    
    def convert_response_value(self, value: str) -> float:
        """
        Convert Kannada/English response values to numeric.
        
        Args:
            value: Response value from the sheet
            
        Returns:
            Numeric value
        """
        logger.debug(f"Converting response value: '{value}' (type: {type(value)})")
        
        if not value or not isinstance(value, str):
            logger.warning(f"Invalid response value: {value}")
            raise ValueError(f"Invalid response value: {value}")
        
        # Clean and normalize the value
        clean_value = value.strip().lower()
        logger.debug(f"Cleaned value: '{clean_value}'")
        
        # Try direct numeric conversion first
        try:
            numeric_result = float(clean_value)
            logger.debug(f"Direct numeric conversion successful: {clean_value} -> {numeric_result}")
            return numeric_result
        except ValueError:
            logger.debug(f"Direct numeric conversion failed for: '{clean_value}'")
            pass
        
        # Try Kannada/English mapping
        if clean_value in self.KANNADA_MAPPINGS:
            result = self.KANNADA_MAPPINGS[clean_value]
            logger.debug(f"Found direct mapping: '{clean_value}' -> {result}")
            return result
        
        # Check for partial matches
        for key, numeric_value in self.KANNADA_MAPPINGS.items():
            if clean_value in key.lower() or key.lower() in clean_value:
                logger.debug(f"Found partial match: '{clean_value}' matches '{key}' -> {numeric_value}")
                return numeric_value
        
        logger.error(f"Could not convert response value: '{value}' (cleaned: '{clean_value}')")
        logger.debug(f"Available mappings: {list(self.KANNADA_MAPPINGS.keys())}")
        raise ValueError(f"Could not convert response value: {value}")
    
    def validate_metadata(self, metadata: Dict[str, str]) -> Dict[str, str]:
        """
        Validate and clean metadata fields.
        
        Args:
            metadata: Dictionary of metadata fields
            
        Returns:
            Cleaned metadata dictionary
        """
        required_fields = ['School', 'Grade', 'Teacher', 'Assessment', 'Name', 'Date']
        cleaned = {}
        
        for field in required_fields:
            value = metadata.get(field, '').strip()
            if not value:
                raise ValueError(f"Required field '{field}' is missing or empty")
            cleaned[field] = value
        
        # Validate date format
        try:
            if cleaned['Date']:
                # Try to parse the date to ensure it's valid
                datetime.strptime(cleaned['Date'], "%Y-%m-%d")
        except ValueError:
            raise ValueError(f"Invalid date format: {cleaned['Date']}. Expected YYYY-MM-DD")
        
        return cleaned
    
    def process_sheet_row(self, row_data: List[str], sheet_row_number: int) -> int:
        """
        Process a single row from Google Sheets and insert into database.
        
        Args:
            row_data: List of cell values from the sheet row
            sheet_row_number: Row number in the sheet
            
        Returns:
            Created res_id
        """
        try:
            logger.debug(f"Processing sheet row {sheet_row_number} with {len(row_data) if row_data else 0} columns")
            logger.debug(f"Raw row data: {row_data}")
            
            if not row_data or len(row_data) == 0:
                raise ValueError("Empty row data")
            
            # Convert row data to response format (index + 1 = column position)
            response_data = {}
            
            # Process each column
            for col_index, cell_value in enumerate(row_data):
                index_id = col_index + 1  # Column A = 1, B = 2, etc.
                logger.debug(f"Processing column {index_id} (col_index {col_index}): '{cell_value}'")
                
                if cell_value and str(cell_value).strip():
                    try:
                        # Try to convert response values
                        numeric_value = self.convert_response_value(str(cell_value))
                        response_data[index_id] = numeric_value
                        logger.debug(f"Successfully converted column {index_id}: '{cell_value}' -> {numeric_value}")
                    except ValueError as e:
                        # If conversion fails, store as string (for metadata)
                        response_data[index_id] = str(cell_value).strip()
                        logger.debug(f"Conversion failed for column {index_id}, stored as string: '{cell_value}' (error: {e})")
            
            logger.debug(f"Final response_data for row {sheet_row_number}: {response_data}")
            
            # Create response using existing ResponseModel logic
            res_id = self.response_model.create_response(response_data)
            logger.info(f"Successfully processed sheet row {sheet_row_number}, created res_id {res_id}")
            return res_id
            
        except Exception as e:
            error_msg = f"Failed to process sheet row {sheet_row_number}: {str(e)}"
            logger.error(error_msg)
            
            # Record the failed import
            self.failed_imports_model.create_failed_import(
                sheet_row_number=sheet_row_number,
                raw_row_data=row_data,
                error_message=str(e)
            )
            raise
    
    def process_row_data(self, row_data: List[str], row_number: int) -> Dict[str, Any]:
        """
        Process a single row of data from Google Sheets.
        
        Args:
            row_data: List of cell values from the sheet row
            row_number: The row number in the sheet
            
        Returns:
            Dict with success status and any error information
        """
        try:
            res_id = self.process_sheet_row(row_data, row_number)
            return {
                'success': True,
                'message': f'Successfully processed row {row_number}',
                'res_id': res_id
            }
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'row_number': row_number
            }
    
    def fetch_and_process_new_rows(self, sheet_url: str, last_row_processed: int) -> Dict[str, Any]:
        """
        Fetch new rows from Google Sheets and process them.
        
        Args:
            sheet_url: Google Sheets URL
            last_row_processed: Last row number that was processed
            
        Returns:
            Dict with processing results
        """
        try:
            import requests
            import csv
            from io import StringIO
            
            # Convert to CSV URL
            csv_url = self.convert_sheets_url_to_csv(sheet_url)
            
            # Fetch the sheet data
            response = requests.get(csv_url, timeout=30)
            response.raise_for_status()
            
            # Parse CSV content
            csv_content = response.text
            csv_reader = csv.reader(StringIO(csv_content))
            rows = list(csv_reader)
            
            total_rows = len(rows)
            
            if total_rows <= last_row_processed:
                return {
                    'success': True,
                    'processed_rows': 0,
                    'message': 'No new rows to process'
                }
            
            processed_count = 0
            failed_count = 0
            
            # Process new rows (skip header if last_row_processed is 0)
            start_row = max(1 if last_row_processed == 0 else last_row_processed + 1, 1)
            
            for row_number in range(start_row, total_rows + 1):
                try:
                    if row_number <= len(rows):
                        row_data = rows[row_number - 1]  # Convert to 0-based index
                        self.process_sheet_row(row_data, row_number)
                        processed_count += 1
                        logger.info(f"Processed sheet row {row_number}")
                except Exception as e:
                    failed_count += 1
                    logger.error(f"Failed to process sheet row {row_number}: {e}")
                    # Error is already recorded in process_sheet_row
                    continue
            
            return {
                'success': True,
                'processed_rows': processed_count,
                'failed_rows': failed_count,
                'total_new_rows': total_rows - last_row_processed,
                'message': f'Processed {processed_count} rows, {failed_count} failed'
            }
            
        except Exception as e:
            logger.error(f"Failed to fetch and process new rows: {e}")
            return {
                'success': False,
                'error': str(e),
                'processed_rows': 0
            }
