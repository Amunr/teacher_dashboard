"""
Layout management service layer.
"""
from typing import Dict, List, Any, Optional
import time
import logging
from datetime import datetime, date

from ..models import LayoutModel
from ..utils.validators import validate_layout_data
from ..utils.exceptions import ValidationError, LayoutNotFoundError

logger = logging.getLogger(__name__)


class LayoutService:
    """Service for layout operations with business logic."""
    
    def __init__(self, layout_model: LayoutModel):
        self.layout_model = layout_model
    
    def get_all_layouts(self) -> List[Dict[str, Any]]:
        """
        Get all layouts with current year information.
        
        Returns:
            List of layout data with metadata
        """
        try:
            layouts = self.layout_model.get_all_layouts()
            current_year = datetime.now().year
            
            # Add additional metadata
            for layout in layouts:
                layout['current_year'] = current_year
                layout['is_active'] = self._is_layout_active(layout)
            
            return layouts
        except Exception as e:
            logger.error(f"Error fetching layouts: {e}")
            raise
    
    def get_layout_for_viewing(self, layout_id: int) -> Dict[str, Any]:
        """
        Get layout data formatted for viewing.
        
        Args:
            layout_id: Layout identifier
            
        Returns:
            Layout data with viewing metadata
            
        Raises:
            LayoutNotFoundError: If layout doesn't exist
        """
        try:
            layout = self.layout_model.get_layout_by_id(layout_id)
            if not layout:
                raise LayoutNotFoundError(f"Layout {layout_id} not found")
            
            # Add viewing metadata
            layout['current_year'] = datetime.now().year
            layout['is_editable'] = self._is_layout_editable(layout)
            layout['question_count'] = self._count_questions(layout)
            
            return layout
        except LayoutNotFoundError:
            raise
        except Exception as e:
            logger.error(f"Error fetching layout {layout_id}: {e}")
            raise
    
    def get_layout_for_editing(self, layout_id: int) -> Dict[str, Any]:
        """
        Get layout data formatted for editing.
        
        Args:
            layout_id: Layout identifier
            
        Returns:
            Layout data with editing metadata
        """
        layout = self.get_layout_for_viewing(layout_id)
        
        # Add editing-specific data
        layout['edit_mode'] = True
        layout['last_modified'] = datetime.now().isoformat()
        
        return layout
    
    def create_layout(self, layout_form_data: Dict[str, Any]) -> int:
        """
        Create new layout from form data.
        
        Args:
            layout_form_data: Form data containing layout information
            
        Returns:
            New layout ID
            
        Raises:
            ValidationError: If layout data is invalid
        """
        try:
            # Validate input data
            validate_layout_data(layout_form_data)
            
            # Process form data into database format
            db_data = self._process_layout_form_data(layout_form_data)
            
            # Create layout
            layout_id = self.layout_model.create_layout(db_data)
            
            logger.info(f"Created new layout {layout_id}")
            return layout_id
            
        except ValidationError:
            raise
        except Exception as e:
            logger.error(f"Error creating layout: {e}")
            raise
    
    def update_layout(self, layout_id: int, layout_form_data: Dict[str, Any]) -> None:
        """
        Update existing layout with new data.
        
        Args:
            layout_id: Layout identifier
            layout_form_data: Form data containing updated layout information
            
        Raises:
            LayoutNotFoundError: If layout doesn't exist
            ValidationError: If layout data is invalid
        """
        try:
            # Check if layout exists
            existing_layout = self.layout_model.get_layout_by_id(layout_id)
            if not existing_layout:
                raise LayoutNotFoundError(f"Layout {layout_id} not found")
            
            # Validate input data
            validate_layout_data(layout_form_data)
            
            # Process form data
            db_data = self._process_layout_form_data(layout_form_data, layout_id)
            
            # Update layout
            self.layout_model.update_layout_inplace(layout_id, db_data)
            
            logger.info(f"Updated layout {layout_id}")
            
        except (LayoutNotFoundError, ValidationError):
            raise
        except Exception as e:
            logger.error(f"Error updating layout {layout_id}: {e}")
            raise
    
    def delete_layout(self, layout_id: int) -> None:
        """
        Delete a layout.
        
        Args:
            layout_id: Layout identifier
            
        Raises:
            LayoutNotFoundError: If layout doesn't exist
        """
        try:
            # Check if layout exists
            existing_layout = self.layout_model.get_layout_by_id(layout_id)
            if not existing_layout:
                raise LayoutNotFoundError(f"Layout {layout_id} not found")
            
            # Delete layout
            self.layout_model.delete_layout(layout_id)
            
            logger.info(f"Deleted layout {layout_id}")
            
        except LayoutNotFoundError:
            raise
        except Exception as e:
            logger.error(f"Error deleting layout {layout_id}: {e}")
            raise
    
    def update_layout_from_session_data(self, session_layout: Dict[str, Any], form_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Update session layout data from form input.
        
        Args:
            session_layout: Current session layout data
            form_data: Form input data
            
        Returns:
            Updated layout data
        """
        try:
            # Update basic fields
            session_layout['layout_name'] = form_data.get('layout_name', 'New Layout')
            session_layout['layout_start_date'] = form_data.get('layout_start_date')
            session_layout['layout_end_date'] = form_data.get('layout_end_date')
            
            # Update metadata
            self._update_metadata_from_form(session_layout, form_data)
            
            # Update domains, subdomains, and questions
            self._update_domains_from_form(session_layout, form_data)
            
            return session_layout
            
        except Exception as e:
            logger.error(f"Error updating layout from form: {e}")
            raise
    
    def add_domain_to_layout(self, session_layout: Dict[str, Any]) -> Dict[str, Any]:
        """Add new domain to layout."""
        new_domain = {
            'id': int(time.time() * 1000),
            'name': 'New Domain',
            'subdomains': []
        }
        session_layout['domains'].append(new_domain)
        return session_layout
    
    def add_subdomain_to_domain(self, session_layout: Dict[str, Any], domain_id: int) -> Dict[str, Any]:
        """Add new subdomain to specific domain."""
        for domain in session_layout['domains']:
            if domain['id'] == domain_id:
                new_subdomain = {
                    'id': int(time.time() * 1000),
                    'name': 'New Subdomain',
                    'questions': []
                }
                domain['subdomains'].append(new_subdomain)
                break
        return session_layout
    
    def add_question_to_subdomain(self, session_layout: Dict[str, Any], domain_id: int, subdomain_id: int) -> Dict[str, Any]:
        """Add new question to specific subdomain."""
        for domain in session_layout['domains']:
            if domain['id'] == domain_id:
                for subdomain in domain['subdomains']:
                    if subdomain['id'] == subdomain_id:
                        new_question = {
                            'id': int(time.time() * 1000),
                            'name': 'New Question',
                            'question_id': int(time.time() * 1000) % 100000
                        }
                        subdomain['questions'].append(new_question)
                        break
                break
        return session_layout
    
    def remove_domain_from_layout(self, session_layout: Dict[str, Any], domain_id: int) -> Dict[str, Any]:
        """Remove domain from layout."""
        session_layout['domains'] = [d for d in session_layout['domains'] if d['id'] != domain_id]
        return session_layout
    
    def remove_subdomain_from_domain(self, session_layout: Dict[str, Any], domain_id: int, subdomain_id: int) -> Dict[str, Any]:
        """Remove subdomain from domain."""
        for domain in session_layout['domains']:
            if domain['id'] == domain_id:
                domain['subdomains'] = [s for s in domain['subdomains'] if s['id'] != subdomain_id]
                break
        return session_layout
    
    def remove_question_from_subdomain(self, session_layout: Dict[str, Any], domain_id: int, subdomain_id: int, question_id: int) -> Dict[str, Any]:
        """Remove question from subdomain."""
        for domain in session_layout['domains']:
            if domain['id'] == domain_id:
                for subdomain in domain['subdomains']:
                    if subdomain['id'] == subdomain_id:
                        subdomain['questions'] = [q for q in subdomain['questions'] if q['id'] != question_id]
                        break
                break
        return session_layout
    
    @staticmethod
    def get_empty_layout() -> Dict[str, Any]:
        """Get empty layout structure."""
        return LayoutModel.get_empty_layout()
    
    def _is_layout_active(self, layout: Dict[str, Any]) -> bool:
        """Check if layout is currently active."""
        try:
            if not layout.get('date_edited'):
                return False
            
            today = date.today()
            layout_date = datetime.strptime(layout['date_edited'], '%Y-%m-%d').date()
            
            # Layout is active if edited within last year
            return (today - layout_date).days <= 365
        except (ValueError, TypeError):
            return False
    
    def _is_layout_editable(self, layout: Dict[str, Any]) -> bool:
        """Check if layout can be edited."""
        # For now, all layouts are editable
        return True
    
    def _count_questions(self, layout: Dict[str, Any]) -> int:
        """Count total questions in layout."""
        count = 0
        for domain in layout.get('domains', []):
            for subdomain in domain.get('subdomains', []):
                count += len(subdomain.get('questions', []))
        count += len(layout.get('metadata_list', []))
        return count
    
    def _process_layout_form_data(self, form_data: Dict[str, Any], layout_id: Optional[int] = None) -> List[Dict[str, Any]]:
        """Convert form data to database format."""
        db_records = []
        
        # Process domains and questions
        for domain in form_data.get('domains', []):
            domain_name = domain.get('name', '')
            for subdomain in domain.get('subdomains', []):
                subdomain_name = subdomain.get('name', '')
                for question in subdomain.get('questions', []):
                    record = {
                        'year_start': form_data.get('layout_start_date'),
                        'year_end': form_data.get('layout_end_date'),
                        'Domain': domain_name,
                        'SubDomain': subdomain_name,
                        'Index_ID': question.get('question_id', 0),
                        'Name': question.get('name', ''),
                        'Date edited': form_data.get('layout_start_date'),
                        'layout_name': form_data.get('layout_name', 'New Layout')
                    }
                    if layout_id is not None:
                        record['layout_id'] = layout_id
                    db_records.append(record)
        
        # Process metadata
        for metadata in form_data.get('metadata_list', []):
            record = {
                'year_start': form_data.get('layout_start_date'),
                'year_end': form_data.get('layout_end_date'),
                'Domain': 'MetaData',
                'SubDomain': '',
                'Index_ID': metadata.get('question_id', 0),
                'Name': metadata.get('name', ''),
                'Date edited': form_data.get('layout_start_date'),
                'layout_name': form_data.get('layout_name', 'New Layout')
            }
            if layout_id is not None:
                record['layout_id'] = layout_id
            db_records.append(record)
        
        return db_records
    
    def _update_metadata_from_form(self, layout: Dict[str, Any], form_data: Dict[str, Any]) -> None:
        """Update metadata from form data."""
        meta_by_id = {str(meta['id']): meta for meta in layout.get('metadata_list', [])}
        meta_by_name = {meta['name']: meta for meta in layout.get('metadata_list', [])}
        
        for key in form_data:
            if key.startswith('metadata_id_'):
                meta_key = key[len('metadata_id_'):]
                val = form_data[key]
                if not val:
                    continue
                
                meta = meta_by_id.get(meta_key)
                if meta:
                    try:
                        meta['question_id'] = int(val)
                    except ValueError:
                        continue
                else:
                    # Add new metadata if not found
                    if meta_key not in meta_by_name:
                        new_id = int(time.time() * 1000)
                        layout.setdefault('metadata_list', []).append({
                            'id': new_id,
                            'name': meta_key.replace('_', ' '),
                            'question_id': int(val)
                        })
    
    def _update_domains_from_form(self, layout: Dict[str, Any], form_data: Dict[str, Any]) -> None:
        """Update domains, subdomains, and questions from form data."""
        for domain in layout.get('domains', []):
            # Update domain name
            domain_key = f"domain_name_{domain['id']}"
            if domain_key in form_data:
                domain['name'] = form_data[domain_key]
            
            for subdomain in domain.get('subdomains', []):
                # Update subdomain name
                subdomain_key = f"subdomain_name_{domain['id']}_{subdomain['id']}"
                if subdomain_key in form_data:
                    subdomain['name'] = form_data[subdomain_key]
                
                for question in subdomain.get('questions', []):
                    # Update question name and ID
                    question_name_key = f"question_name_{domain['id']}_{subdomain['id']}_{question['id']}"
                    question_id_key = f"question_id_{domain['id']}_{subdomain['id']}_{question['id']}"
                    
                    if question_name_key in form_data:
                        question['name'] = form_data[question_name_key]
                    if question_id_key in form_data:
                        try:
                            question['question_id'] = int(form_data[question_id_key])
                        except ValueError:
                            pass
