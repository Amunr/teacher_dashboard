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
                query = select(
                    self.db.questions_table.c.layout_id,
                    self.db.questions_table.c.layout_name,
                    func.max(self.db.questions_table.c['Date edited']).label('date_edited'),
                    func.max(self.db.questions_table.c.year_end).label('year_end'),
                    func.max(self.db.questions_table.c.year_start).label('year_start')
                ).group_by(
                    self.db.questions_table.c.layout_id, 
                    self.db.questions_table.c.layout_name
                )
                
                result = conn.execute(query).mappings().all()
                
                if not result:
                    return []
                
                # Find the layout with the latest year_end as current
                max_year_end = max(
                    [r['year_end'] for r in result if r['year_end'] is not None], 
                    default=None
                )
                
                layouts = []
                for row in result:
                    layouts.append({
                        'layout_id': row['layout_id'],
                        'layout_name': row['layout_name'],
                        'date_edited': str(row['date_edited']) if row['date_edited'] else '',
                        'is_current': (row['year_end'] == max_year_end)
                    })
                
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
    
    def create_response(self, response_data: Dict[str, Any]) -> None:
        """
        Create a new response record.
        
        Args:
            response_data: Response data dictionary
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
                
                # Get valid Index_IDs
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
                
        except Exception as e:
            logger.error(f"Failed to create response: {e}")
            raise
