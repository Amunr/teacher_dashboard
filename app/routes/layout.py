"""
Layout management routes.
"""
from flask import Blueprint, render_template, request, redirect, url_for, session, flash, jsonify, current_app
from typing import Dict, Any, Tuple
import logging
from datetime import datetime

from ..services import LayoutService
from ..utils import (
    ValidationError, LayoutNotFoundError, validate_id, 
    log_operation, create_response_context, sanitize_string
)

logger = logging.getLogger(__name__)
layout_bp = Blueprint('layout', __name__, url_prefix='/layout')


def get_layout_service() -> LayoutService:
    """Get layout service instance."""
    return current_app.layout_service


@layout_bp.route('/')
def layout_list() -> str:
    """
    Display list of all layouts.
    
    Returns:
        Rendered layout list template
    """
    try:
        layout_service = get_layout_service()
        layouts = layout_service.get_all_layouts()
        current_year = datetime.now().year
        
        log_operation('layout_list_viewed', {'count': len(layouts)})
        
        return render_template(
            'layout_view.html',
            current_year=current_year,
            layouts=layouts
        )
        
    except Exception as e:
        logger.error(f"Error fetching layout list: {e}")
        flash('Error loading layouts', 'error')
        return render_template('error.html', message="Failed to load layouts"), 500


@layout_bp.route('/view/<int:layout_id>')
def layout_view(layout_id: int) -> str:
    """
    View specific layout details.
    
    Args:
        layout_id: Layout identifier
        
    Returns:
        Rendered layout viewer template
    """
    try:
        layout_id = validate_id(layout_id, 'Layout ID')
        layout_service = get_layout_service()
        layout = layout_service.get_layout_for_viewing(layout_id)
        
        log_operation('layout_viewed', {'layout_id': layout_id})
        
        return render_template('layout_viewer.html', **layout)
        
    except LayoutNotFoundError:
        flash(f'Layout {layout_id} not found', 'error')
        return redirect(url_for('layout.layout_list'))
    except ValidationError as e:
        flash(f'Invalid layout ID: {e.message}', 'error')
        return redirect(url_for('layout.layout_list'))
    except Exception as e:
        logger.error(f"Error viewing layout {layout_id}: {e}")
        flash('Error loading layout', 'error')
        return redirect(url_for('layout.layout_list'))


@layout_bp.route('/delete/<int:layout_id>', methods=['POST'])
def delete_layout_route(layout_id: int) -> Tuple[str, int]:
    """
    Delete a layout.
    
    Args:
        layout_id: Layout identifier
        
    Returns:
        Redirect response
    """
    try:
        layout_id = validate_id(layout_id, 'Layout ID')
        layout_service = get_layout_service()
        layout_service.delete_layout(layout_id)
        
        flash('Layout deleted successfully', 'success')
        log_operation('layout_deleted', {'layout_id': layout_id})
        
        return redirect(url_for('layout.layout_list'))
        
    except LayoutNotFoundError:
        flash(f'Layout {layout_id} not found', 'error')
        return redirect(url_for('layout.layout_list'))
    except ValidationError as e:
        flash(f'Invalid layout ID: {e.message}', 'error')
        return redirect(url_for('layout.layout_list'))
    except Exception as e:
        logger.error(f"Error deleting layout {layout_id}: {e}")
        flash(f'Error deleting layout: {str(e)}', 'error')
        return redirect(url_for('layout.layout_view', layout_id=layout_id))


@layout_bp.route('/edit/new', methods=['GET'])
def layout_edit_new() -> str:
    """
    Create new layout form.
    
    Returns:
        Rendered layout builder template
    """
    try:
        layout_service = get_layout_service()
        empty_layout = layout_service.get_empty_layout()
        session['layout_data'] = empty_layout
        
        log_operation('new_layout_form_accessed')
        
        return render_template('layout_builder.html', **empty_layout)
        
    except Exception as e:
        logger.error(f"Error creating new layout form: {e}")
        flash('Error creating new layout', 'error')
        return redirect(url_for('layout.layout_list'))


@layout_bp.route('/edit/<int:layout_id>', methods=['GET'])
def layout_edit(layout_id: int) -> str:
    """
    Edit existing layout (clone mode).
    
    Args:
        layout_id: Layout identifier
        
    Returns:
        Rendered layout builder template
    """
    try:
        layout_id = validate_id(layout_id, 'Layout ID')
        layout_service = get_layout_service()
        layout = layout_service.get_layout_for_editing(layout_id)
        
        session['layout_data'] = layout
        log_operation('layout_edit_form_accessed', {'layout_id': layout_id})
        
        return render_template('layout_builder.html', **layout)
        
    except LayoutNotFoundError:
        flash(f'Layout {layout_id} not found', 'error')
        return redirect(url_for('layout.layout_list'))
    except ValidationError as e:
        flash(f'Invalid layout ID: {e.message}', 'error')
        return redirect(url_for('layout.layout_list'))
    except Exception as e:
        logger.error(f"Error editing layout {layout_id}: {e}")
        flash('Error loading layout for editing', 'error')
        return redirect(url_for('layout.layout_list'))


@layout_bp.route('/update/<int:layout_id>', methods=['GET'])
def layout_update(layout_id: int) -> str:
    """
    Update existing layout (in-place mode).
    
    Args:
        layout_id: Layout identifier
        
    Returns:
        Rendered layout updater template
    """
    try:
        layout_id = validate_id(layout_id, 'Layout ID')
        layout_service = get_layout_service()
        layout = layout_service.get_layout_for_editing(layout_id)
        
        session['layout_data'] = layout
        log_operation('layout_update_form_accessed', {'layout_id': layout_id})
        
        return render_template('layout_updater.html', **layout)
        
    except LayoutNotFoundError:
        flash(f'Layout {layout_id} not found', 'error')
        return redirect(url_for('layout.layout_list'))
    except ValidationError as e:
        flash(f'Invalid layout ID: {e.message}', 'error')
        return redirect(url_for('layout.layout_list'))
    except Exception as e:
        logger.error(f"Error loading layout update form {layout_id}: {e}")
        flash('Error loading layout for updating', 'error')
        return redirect(url_for('layout.layout_list'))


def get_session_layout() -> Dict[str, Any]:
    """Get layout data from session."""
    layout_service = get_layout_service()
    return session.get('layout_data', layout_service.get_empty_layout())


def save_session_layout(layout: Dict[str, Any]) -> None:
    """Save layout data to session."""
    session['layout_data'] = layout


# --- CRUD Operations for Layout Builder ---

@layout_bp.route('/add_domain', methods=['POST'])
def add_domain() -> str:
    """Add new domain to current layout."""
    try:
        layout_service = get_layout_service()
        layout = get_session_layout()
        layout = layout_service.update_layout_from_session_data(layout, request.form)
        layout = layout_service.add_domain_to_layout(layout)
        save_session_layout(layout)
        
        log_operation('domain_added')
        return render_template('layout_builder.html', **layout)
        
    except Exception as e:
        logger.error(f"Error adding domain: {e}")
        flash('Error adding domain', 'error')
        layout = get_session_layout()
        return render_template('layout_builder.html', **layout)


@layout_bp.route('/delete_domain/<int:domain_id>', methods=['POST'])
def delete_domain(domain_id: int) -> str:
    """Delete domain from current layout."""
    try:
        domain_id = validate_id(domain_id, 'Domain ID')
        layout_service = get_layout_service()
        layout = get_session_layout()
        layout = layout_service.update_layout_from_session_data(layout, request.form)
        layout = layout_service.remove_domain_from_layout(layout, domain_id)
        save_session_layout(layout)
        
        log_operation('domain_deleted', {'domain_id': domain_id})
        return render_template('layout_builder.html', **layout)
        
    except Exception as e:
        logger.error(f"Error deleting domain: {e}")
        flash('Error deleting domain', 'error')
        layout = get_session_layout()
        return render_template('layout_builder.html', **layout)


@layout_bp.route('/add_subdomain/<int:domain_id>', methods=['POST'])
def add_subdomain(domain_id: int) -> str:
    """Add subdomain to specific domain."""
    try:
        domain_id = validate_id(domain_id, 'Domain ID')
        layout_service = get_layout_service()
        layout = get_session_layout()
        layout = layout_service.update_layout_from_session_data(layout, request.form)
        layout = layout_service.add_subdomain_to_domain(layout, domain_id)
        save_session_layout(layout)
        
        log_operation('subdomain_added', {'domain_id': domain_id})
        return render_template('layout_builder.html', **layout)
        
    except Exception as e:
        logger.error(f"Error adding subdomain: {e}")
        flash('Error adding subdomain', 'error')
        layout = get_session_layout()
        return render_template('layout_builder.html', **layout)


@layout_bp.route('/delete_subdomain/<int:domain_id>/<int:subdomain_id>', methods=['POST'])
def delete_subdomain(domain_id: int, subdomain_id: int) -> str:
    """Delete subdomain from domain."""
    try:
        domain_id = validate_id(domain_id, 'Domain ID')
        subdomain_id = validate_id(subdomain_id, 'Subdomain ID')
        layout_service = get_layout_service()
        layout = get_session_layout()
        layout = layout_service.update_layout_from_session_data(layout, request.form)
        layout = layout_service.remove_subdomain_from_domain(layout, domain_id, subdomain_id)
        save_session_layout(layout)
        
        log_operation('subdomain_deleted', {'domain_id': domain_id, 'subdomain_id': subdomain_id})
        return render_template('layout_builder.html', **layout)
        
    except Exception as e:
        logger.error(f"Error deleting subdomain: {e}")
        flash('Error deleting subdomain', 'error')
        layout = get_session_layout()
        return render_template('layout_builder.html', **layout)


@layout_bp.route('/add_question/<int:domain_id>/<int:subdomain_id>', methods=['POST'])
def add_question(domain_id: int, subdomain_id: int) -> str:
    """Add question to subdomain."""
    try:
        domain_id = validate_id(domain_id, 'Domain ID')
        subdomain_id = validate_id(subdomain_id, 'Subdomain ID')
        layout_service = get_layout_service()
        layout = get_session_layout()
        layout = layout_service.update_layout_from_session_data(layout, request.form)
        layout = layout_service.add_question_to_subdomain(layout, domain_id, subdomain_id)
        save_session_layout(layout)
        
        log_operation('question_added', {'domain_id': domain_id, 'subdomain_id': subdomain_id})
        return render_template('layout_builder.html', **layout)
        
    except Exception as e:
        logger.error(f"Error adding question: {e}")
        flash('Error adding question', 'error')
        layout = get_session_layout()
        return render_template('layout_builder.html', **layout)


@layout_bp.route('/delete_question/<int:domain_id>/<int:subdomain_id>/<int:question_id>', methods=['POST'])
def delete_question(domain_id: int, subdomain_id: int, question_id: int) -> str:
    """Delete question from subdomain."""
    try:
        domain_id = validate_id(domain_id, 'Domain ID')
        subdomain_id = validate_id(subdomain_id, 'Subdomain ID')
        question_id = validate_id(question_id, 'Question ID')
        layout_service = get_layout_service()
        layout = get_session_layout()
        layout = layout_service.update_layout_from_session_data(layout, request.form)
        layout = layout_service.remove_question_from_subdomain(layout, domain_id, subdomain_id, question_id)
        save_session_layout(layout)
        
        log_operation('question_deleted', {
            'domain_id': domain_id, 
            'subdomain_id': subdomain_id, 
            'question_id': question_id
        })
        return render_template('layout_builder.html', **layout)
        
    except Exception as e:
        logger.error(f"Error deleting question: {e}")
        flash('Error deleting question', 'error')
        layout = get_session_layout()
        return render_template('layout_builder.html', **layout)


# --- Save and Update Routes ---

@layout_bp.route('/submit', methods=['POST'])
def submit_layout() -> str:
    """Submit new layout to database."""
    try:
        layout_service = get_layout_service()
        layout = get_session_layout()
        layout = layout_service.update_layout_from_session_data(layout, request.form)
        
        # Sanitize layout name
        layout['layout_name'] = sanitize_string(layout.get('layout_name', ''), 255)
        
        layout_id = layout_service.create_layout(layout)
        session.pop('layout_data', None)
        
        flash('Layout created successfully', 'success')
        log_operation('layout_created', {'layout_id': layout_id})
        
        return redirect(url_for('layout.layout_list'))
        
    except ValidationError as e:
        flash(f'Validation error: {e.message}', 'error')
        layout = get_session_layout()
        return render_template('layout_builder.html', **layout)
    except Exception as e:
        logger.error(f"Error submitting layout: {e}")
        flash('Error saving layout', 'error')
        layout = get_session_layout()
        return render_template('layout_builder.html', **layout)


@layout_bp.route('/update/<int:layout_id>/submit', methods=['POST'])
def update_layout_submit(layout_id: int) -> str:
    """Submit layout updates to database."""
    try:
        layout_id = validate_id(layout_id, 'Layout ID')
        layout_service = get_layout_service()
        layout = get_session_layout()
        layout = layout_service.update_layout_from_session_data(layout, request.form)
        
        # Sanitize layout name
        layout['layout_name'] = sanitize_string(layout.get('layout_name', ''), 255)
        
        layout_service.update_layout(layout_id, layout)
        session.pop('layout_data', None)
        
        flash('Layout updated successfully', 'success')
        log_operation('layout_updated', {'layout_id': layout_id})
        
        return redirect(url_for('layout.layout_view', layout_id=layout_id))
        
    except LayoutNotFoundError:
        flash(f'Layout {layout_id} not found', 'error')
        return redirect(url_for('layout.layout_list'))
    except ValidationError as e:
        flash(f'Validation error: {e.message}', 'error')
        layout = get_session_layout()
        return render_template('layout_updater.html', **layout)
    except Exception as e:
        logger.error(f"Error updating layout {layout_id}: {e}")
        flash('Error updating layout', 'error')
        layout = get_session_layout()
        return render_template('layout_updater.html', **layout)


# --- API Routes for AJAX Operations ---

@layout_bp.route('/api/validate', methods=['POST'])
def validate_layout_api() -> Dict[str, Any]:
    """API endpoint for layout validation."""
    try:
        layout_data = request.get_json()
        if not layout_data:
            return {'valid': False, 'errors': ['No data provided']}, 400
        
        # Perform validation (implement as needed)
        return {'valid': True, 'message': 'Layout is valid'}
        
    except Exception as e:
        logger.error(f"Error validating layout: {e}")
        return {'valid': False, 'errors': [str(e)]}, 500


# --- Update-specific routes for layout editing ---

@layout_bp.route('/update/<int:layout_id>/add_domain', methods=['POST'])
def update_add_domain(layout_id: int) -> str:
    """Add domain during layout update."""
    try:
        layout_id = validate_id(layout_id, 'Layout ID')
        layout_service = get_layout_service()
        layout = get_session_layout()
        layout['layout_id'] = layout_id
        layout = layout_service.update_layout_from_session_data(layout, request.form)
        layout = layout_service.add_domain_to_layout(layout)
        save_session_layout(layout)
        
        log_operation('domain_added_update', {'layout_id': layout_id})
        return render_template('layout_updater.html', **layout)
        
    except Exception as e:
        logger.error(f"Error adding domain during update: {e}")
        flash('Error adding domain', 'error')
        layout = get_session_layout()
        layout['layout_id'] = layout_id
        return render_template('layout_updater.html', **layout)


@layout_bp.route('/update/<int:layout_id>/delete_domain/<int:domain_id>', methods=['POST'])
def update_delete_domain(layout_id: int, domain_id: int) -> str:
    """Delete domain during layout update."""
    try:
        layout_id = validate_id(layout_id, 'Layout ID')
        domain_id = validate_id(domain_id, 'Domain ID')
        layout_service = get_layout_service()
        layout = get_session_layout()
        layout['layout_id'] = layout_id
        layout = layout_service.update_layout_from_session_data(layout, request.form)
        layout = layout_service.remove_domain_from_layout(layout, domain_id)
        save_session_layout(layout)
        
        log_operation('domain_deleted_update', {'layout_id': layout_id, 'domain_id': domain_id})
        return render_template('layout_updater.html', **layout)
        
    except Exception as e:
        logger.error(f"Error deleting domain during update: {e}")
        flash('Error deleting domain', 'error')
        layout = get_session_layout()
        layout['layout_id'] = layout_id
        return render_template('layout_updater.html', **layout)


@layout_bp.route('/update/<int:layout_id>/add_subdomain/<int:domain_id>', methods=['POST'])
def update_add_subdomain(layout_id: int, domain_id: int) -> str:
    """Add subdomain during layout update."""
    try:
        layout_id = validate_id(layout_id, 'Layout ID')
        domain_id = validate_id(domain_id, 'Domain ID')
        layout_service = get_layout_service()
        layout = get_session_layout()
        layout['layout_id'] = layout_id
        layout = layout_service.update_layout_from_session_data(layout, request.form)
        layout = layout_service.add_subdomain_to_domain(layout, domain_id)
        save_session_layout(layout)
        
        log_operation('subdomain_added_update', {'layout_id': layout_id, 'domain_id': domain_id})
        return render_template('layout_updater.html', **layout)
        
    except Exception as e:
        logger.error(f"Error adding subdomain during update: {e}")
        flash('Error adding subdomain', 'error')
        layout = get_session_layout()
        layout['layout_id'] = layout_id
        return render_template('layout_updater.html', **layout)


@layout_bp.route('/update/<int:layout_id>/delete_subdomain/<int:domain_id>/<int:subdomain_id>', methods=['POST'])
def update_delete_subdomain(layout_id: int, domain_id: int, subdomain_id: int) -> str:
    """Delete subdomain during layout update."""
    try:
        layout_id = validate_id(layout_id, 'Layout ID')
        domain_id = validate_id(domain_id, 'Domain ID')
        subdomain_id = validate_id(subdomain_id, 'Subdomain ID')
        layout_service = get_layout_service()
        layout = get_session_layout()
        layout['layout_id'] = layout_id
        layout = layout_service.update_layout_from_session_data(layout, request.form)
        layout = layout_service.remove_subdomain_from_domain(layout, domain_id, subdomain_id)
        save_session_layout(layout)
        
        log_operation('subdomain_deleted_update', {'layout_id': layout_id, 'domain_id': domain_id, 'subdomain_id': subdomain_id})
        return render_template('layout_updater.html', **layout)
        
    except Exception as e:
        logger.error(f"Error deleting subdomain during update: {e}")
        flash('Error deleting subdomain', 'error')
        layout = get_session_layout()
        layout['layout_id'] = layout_id
        return render_template('layout_updater.html', **layout)


@layout_bp.route('/update/<int:layout_id>/add_question/<int:domain_id>/<int:subdomain_id>', methods=['POST'])
def update_add_question(layout_id: int, domain_id: int, subdomain_id: int) -> str:
    """Add question during layout update."""
    try:
        layout_id = validate_id(layout_id, 'Layout ID')
        domain_id = validate_id(domain_id, 'Domain ID')
        subdomain_id = validate_id(subdomain_id, 'Subdomain ID')
        layout_service = get_layout_service()
        layout = get_session_layout()
        layout['layout_id'] = layout_id
        layout = layout_service.update_layout_from_session_data(layout, request.form)
        layout = layout_service.add_question_to_subdomain(layout, domain_id, subdomain_id)
        save_session_layout(layout)
        
        log_operation('question_added_update', {'layout_id': layout_id, 'domain_id': domain_id, 'subdomain_id': subdomain_id})
        return render_template('layout_updater.html', **layout)
        
    except Exception as e:
        logger.error(f"Error adding question during update: {e}")
        flash('Error adding question', 'error')
        layout = get_session_layout()
        layout['layout_id'] = layout_id
        return render_template('layout_updater.html', **layout)


@layout_bp.route('/update/<int:layout_id>/delete_question/<int:domain_id>/<int:subdomain_id>/<int:question_id>', methods=['POST'])
def update_delete_question(layout_id: int, domain_id: int, subdomain_id: int, question_id: int) -> str:
    """Delete question during layout update."""
    try:
        layout_id = validate_id(layout_id, 'Layout ID')
        domain_id = validate_id(domain_id, 'Domain ID')
        subdomain_id = validate_id(subdomain_id, 'Subdomain ID')
        question_id = validate_id(question_id, 'Question ID')
        layout_service = get_layout_service()
        layout = get_session_layout()
        layout['layout_id'] = layout_id
        layout = layout_service.update_layout_from_session_data(layout, request.form)
        layout = layout_service.remove_question_from_subdomain(layout, domain_id, subdomain_id, question_id)
        save_session_layout(layout)
        
        log_operation('question_deleted_update', {'layout_id': layout_id, 'domain_id': domain_id, 'subdomain_id': subdomain_id, 'question_id': question_id})
        return render_template('layout_updater.html', **layout)
        
    except Exception as e:
        logger.error(f"Error deleting question during update: {e}")
        flash('Error deleting question', 'error')
        layout = get_session_layout()
        layout['layout_id'] = layout_id
        return render_template('layout_updater.html', **layout)


# Error handlers for layout blueprint
@layout_bp.errorhandler(ValidationError)
def handle_validation_error(error: ValidationError) -> Tuple[str, int]:
    """Handle validation errors."""
    flash(f'Validation error: {error.message}', 'error')
    return redirect(url_for('layout.layout_list')), 400


@layout_bp.errorhandler(LayoutNotFoundError)
def handle_layout_not_found(error: LayoutNotFoundError) -> Tuple[str, int]:
    """Handle layout not found errors."""
    flash(str(error), 'error')
    return redirect(url_for('layout.layout_list')), 404
