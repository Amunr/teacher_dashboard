
from flask import Flask, render_template, request, redirect, url_for, session
import database
import time

app = Flask(__name__)
app.secret_key = 'dev'  # For session usage

# --- IN-PLACE UPDATE ROUTES (for /update mode) ---
@app.route('/layout/update_delete_domain/<int:layout_id>/<int:domain_id>', methods=['POST'])
def update_delete_domain(layout_id, domain_id):
    layout = get_layout()
    layout = update_layout_from_form(layout, request.form)
    layout['domains'] = [d for d in layout['domains'] if d['id'] != domain_id]
    save_layout(layout)
    return render_template('layout_updater.html', **layout)

@app.route('/layout/update_add_subdomain/<int:layout_id>/<int:domain_id>', methods=['POST'])
def update_add_subdomain(layout_id, domain_id):
    layout = get_layout()
    layout = update_layout_from_form(layout, request.form)
    for d in layout['domains']:
        if d['id'] == domain_id:
            d['subdomains'].append({'id': int(time.time()*1000), 'name': 'New Subdomain', 'questions': []})
    save_layout(layout)
    return render_template('layout_updater.html', **layout)

@app.route('/layout/update_delete_subdomain/<int:layout_id>/<int:domain_id>/<int:subdomain_id>', methods=['POST'])
def update_delete_subdomain(layout_id, domain_id, subdomain_id):
    layout = get_layout()
    layout = update_layout_from_form(layout, request.form)
    for d in layout['domains']:
        if d['id'] == domain_id:
            d['subdomains'] = [s for s in d['subdomains'] if s['id'] != subdomain_id]
    save_layout(layout)
    return render_template('layout_updater.html', **layout)

@app.route('/layout/update_add_question/<int:layout_id>/<int:domain_id>/<int:subdomain_id>', methods=['POST'])
def update_add_question(layout_id, domain_id, subdomain_id):
    layout = get_layout()
    layout = update_layout_from_form(layout, request.form)
    for d in layout['domains']:
        if d['id'] == domain_id:
            for s in d['subdomains']:
                if s['id'] == subdomain_id:
                    s['questions'].append({'id': int(time.time()*1000), 'name': 'New Question', 'question_id': int(time.time()*1000)%100000})
    save_layout(layout)
    return render_template('layout_updater.html', **layout)

@app.route('/layout/update_delete_question/<int:layout_id>/<int:domain_id>/<int:subdomain_id>/<int:question_id>', methods=['POST'])
def update_delete_question(layout_id, domain_id, subdomain_id, question_id):
    layout = get_layout()
    layout = update_layout_from_form(layout, request.form)
    for d in layout['domains']:
        if d['id'] == domain_id:
            for s in d['subdomains']:
                if s['id'] == subdomain_id:
                    s['questions'] = [q for q in s['questions'] if q['id'] != question_id]
    save_layout(layout)
    return render_template('layout_updater.html', **layout)
from flask import Flask, render_template, request, redirect, url_for, session
import database
import time

app = Flask(__name__)
app.secret_key = 'dev'  # For session usage

@app.route('/')
def home():
    return render_template('homepage.html')

@app.route('/layout')
def layout_list():
    from datetime import datetime
    current_year = datetime.now().year
    layouts = database.fetch_all_layouts()
    return render_template('layout_view.html', current_year=current_year, layouts=layouts)

@app.route('/layout/view/<int:layout_id>')
def layout_view(layout_id):
    layout = database.fetch_layout_jinja(layout_id)
    if not layout:
        return "Layout not found", 404
    return render_template('layout_viewer.html', **layout)

@app.route('/layout/edit/new', methods=['GET'])
def layout_edit_new():
    session['layout_data'] = database.empty_layout_jinja()
    return render_template('layout_builder.html', **session['layout_data'])

@app.route('/layout/edit/<int:layout_id>', methods=['GET'])
def layout_edit(layout_id):
    layout = database.fetch_layout_jinja(layout_id)
    if not layout:
        return "Layout not found", 404
    session['layout_data'] = layout
    return render_template('layout_builder.html', **layout)

@app.route('/layout/update/<int:layout_id>', methods=['GET'])
def layout_update(layout_id):
    layout = database.fetch_layout_jinja(layout_id)
    if not layout:
        return "Layout not found", 404
    session['layout_data'] = layout
    return render_template('layout_updater.html', **layout)

def get_layout():
    return session.get('layout_data', database.empty_layout_jinja())

def save_layout(layout):
    session['layout_data'] = layout


# --- CRUD ROUTES ---

def update_layout_from_form(layout, form):
    layout['layout_name'] = form.get('layout_name', 'New Layout')
    layout['layout_start_date'] = form.get('layout_start_date')
    layout['layout_end_date'] = form.get('layout_end_date')
    # Build a map of existing metadata by id and name
    meta_by_id = {str(meta['id']): meta for meta in layout.get('metadata_list', [])}
    meta_by_name = {meta['name']: meta for meta in layout.get('metadata_list', [])}
    # Track which meta fields have been updated
    updated_meta_ids = set()
    # Handle all metadata_id_* fields in the form
    for key in form:
        if key.startswith('metadata_id_'):
            meta_key = key[len('metadata_id_'):]
            val = form[key]
            if not val:
                continue  # skip empty values
            # Try to find by id first
            meta = meta_by_id.get(meta_key)
            if meta:
                try:
                    meta['question_id'] = int(val)
                    updated_meta_ids.add(meta['id'])
                except ValueError:
                    continue
            else:
                # If not found by id, treat meta_key as the name (from template fallback)
                # Only add if not already present
                if meta_key not in meta_by_name:
                    new_id = int(time.time()*1000)  # unique id
                    layout.setdefault('metadata_list', []).append({'id': new_id, 'name': meta_key.replace('_', ' '), 'question_id': int(val)})
                    updated_meta_ids.add(new_id)
    # Optionally, remove any metadata entries not present in the form (if you want to keep in sync)
    # layout['metadata_list'] = [m for m in layout.get('metadata_list', []) if m['id'] in updated_meta_ids]
    for domain in layout.get('domains', []):
        dkey = f"domain_name_{domain['id']}"
        if dkey in form:
            domain['name'] = form[dkey]
        for sub in domain.get('subdomains', []):
            skey = f"subdomain_name_{domain['id']}_{sub['id']}"
            if skey in form:
                sub['name'] = form[skey]
            for q in sub.get('questions', []):
                qkey = f"question_name_{domain['id']}_{sub['id']}_{q['id']}"
                qidkey = f"question_id_{domain['id']}_{sub['id']}_{q['id']}"
                if qkey in form:
                    q['name'] = form[qkey]
                if qidkey in form:
                    q['question_id'] = int(form[qidkey])
    return layout

@app.route('/layout/add_domain', methods=['POST'])
def add_domain():
    layout = get_layout()
    layout = update_layout_from_form(layout, request.form)
    layout['domains'].append({'id': int(time.time()*1000), 'name': 'New Domain', 'subdomains': []})
    save_layout(layout)
    return render_template('layout_builder.html', **layout)

@app.route('/layout/delete_domain/<int:domain_id>', methods=['POST'])
def delete_domain(domain_id):
    layout = get_layout()
    layout = update_layout_from_form(layout, request.form)
    layout['domains'] = [d for d in layout['domains'] if d['id'] != domain_id]
    save_layout(layout)
    return render_template('layout_builder.html', **layout)

@app.route('/layout/edit_domain/<int:domain_id>', methods=['POST'])
def edit_domain(domain_id):
    layout = get_layout()
    layout = update_layout_from_form(layout, request.form)
    save_layout(layout)
    return render_template('layout_builder.html', **layout)

@app.route('/layout/add_subdomain/<int:domain_id>', methods=['POST'])
def add_subdomain(domain_id):
    layout = get_layout()
    layout = update_layout_from_form(layout, request.form)
    for d in layout['domains']:
        if d['id'] == domain_id:
            d['subdomains'].append({'id': int(time.time()*1000), 'name': 'New Subdomain', 'questions': []})
    save_layout(layout)
    return render_template('layout_builder.html', **layout)

@app.route('/layout/delete_subdomain/<int:domain_id>/<int:subdomain_id>', methods=['POST'])
def delete_subdomain(domain_id, subdomain_id):
    layout = get_layout()
    layout = update_layout_from_form(layout, request.form)
    for d in layout['domains']:
        if d['id'] == domain_id:
            d['subdomains'] = [s for s in d['subdomains'] if s['id'] != subdomain_id]
    save_layout(layout)
    return render_template('layout_builder.html', **layout)

@app.route('/layout/edit_subdomain/<int:domain_id>/<int:subdomain_id>', methods=['POST'])
def edit_subdomain(domain_id, subdomain_id):
    layout = get_layout()
    layout = update_layout_from_form(layout, request.form)
    save_layout(layout)
    return render_template('layout_builder.html', **layout)

@app.route('/layout/add_question/<int:domain_id>/<int:subdomain_id>', methods=['POST'])
def add_question(domain_id, subdomain_id):
    layout = get_layout()
    layout = update_layout_from_form(layout, request.form)
    for d in layout['domains']:
        if d['id'] == domain_id:
            for s in d['subdomains']:
                if s['id'] == subdomain_id:
                    s['questions'].append({'id': int(time.time()*1000), 'name': 'New Question', 'question_id': int(time.time()*1000)%100000})
    save_layout(layout)
    return render_template('layout_builder.html', **layout)

@app.route('/layout/delete_question/<int:domain_id>/<int:subdomain_id>/<int:question_id>', methods=['POST'])
def delete_question(domain_id, subdomain_id, question_id):
    layout = get_layout()
    layout = update_layout_from_form(layout, request.form)
    for d in layout['domains']:
        if d['id'] == domain_id:
            for s in d['subdomains']:
                if s['id'] == subdomain_id:
                    s['questions'] = [q for q in s['questions'] if q['id'] != question_id]
    save_layout(layout)
    return render_template('layout_builder.html', **layout)

@app.route('/layout/edit_question/<int:domain_id>/<int:subdomain_id>/<int:question_id>', methods=['POST'])
def edit_question(domain_id, subdomain_id, question_id):
    layout = get_layout()
    layout = update_layout_from_form(layout, request.form)
    save_layout(layout)
    return render_template('layout_builder.html', **layout)

# --- SAVE ROUTE ---
@app.route('/layout/submit', methods=['POST'])
def submit_layout():
    form = request.form
    layout = get_layout()
    layout['layout_name'] = form.get('layout_name', 'New Layout')
    layout['layout_start_date'] = form.get('layout_start_date')
    layout['layout_end_date'] = form.get('layout_end_date')
    for meta in layout.get('metadata_list', []):
        key = f"metadata_id_{meta['id']}"
        if key in form:
            meta['question_id'] = int(form[key])
    for domain in layout.get('domains', []):
        dkey = f"domain_name_{domain['id']}"
        if dkey in form:
            domain['name'] = form[dkey]
        for sub in domain.get('subdomains', []):
            skey = f"subdomain_name_{domain['id']}_{sub['id']}"
            if skey in form:
                sub['name'] = form[skey]
            for q in sub.get('questions', []):
                qkey = f"question_name_{domain['id']}_{sub['id']}_{q['id']}"
                qidkey = f"question_id_{domain['id']}_{sub['id']}_{q['id']}"
                if qkey in form:
                    q['name'] = form[qkey]
                if qidkey in form:
                    q['question_id'] = int(form[qidkey])
    # Flatten for DB
    def flatten(layout):
        out = []
        for domain in layout.get('domains', []):
            dname = domain.get('name', '')
            for sub in domain.get('subdomains', []):
                sdname = sub.get('name', '')
                for q in sub.get('questions', []):
                    out.append({
                        'year_start': layout.get('layout_start_date'),
                        'year_end': layout.get('layout_end_date'),
                        'Domain': dname,
                        'SubDomain': sdname,
                        'Index_ID': q.get('question_id', 0),
                        'Name': q.get('name', ''),
                        'Date edited': layout.get('layout_start_date'),
                        'layout_name': layout.get('layout_name', 'New Layout')
                    })
        for meta in layout.get('metadata_list', []):
            out.append({
                'year_start': layout.get('layout_start_date'),
                'year_end': layout.get('layout_end_date'),
                'Domain': 'MetaData',
                'SubDomain': '',
                'Index_ID': meta.get('question_id', 0),
                'Name': meta.get('name', ''),
                'Date edited': layout.get('layout_start_date'),
                'layout_name': layout.get('layout_name', 'New Layout')
            })
        return out
    database.insert_layout(flatten(layout))
    session.pop('layout_data', None)
    return redirect(url_for('layout_list'))

@app.route('/layout/update_submit/<int:layout_id>', methods=['POST'])
def update_layout_submit(layout_id):
    form = request.form
    layout = get_layout()
    layout['layout_name'] = form.get('layout_name', 'New Layout')
    layout['layout_start_date'] = form.get('layout_start_date')
    layout['layout_end_date'] = form.get('layout_end_date')
    for meta in layout.get('metadata_list', []):
        key = f"metadata_id_{meta['id']}"
        if key in form:
            meta['question_id'] = int(form[key])
    for domain in layout.get('domains', []):
        dkey = f"domain_name_{domain['id']}"
        if dkey in form:
            domain['name'] = form[dkey]
        for sub in domain.get('subdomains', []):
            skey = f"subdomain_name_{domain['id']}_{sub['id']}"
            if skey in form:
                sub['name'] = form[skey]
            for q in sub.get('questions', []):
                qkey = f"question_name_{domain['id']}_{sub['id']}_{q['id']}"
                qidkey = f"question_id_{domain['id']}_{sub['id']}_{q['id']}"
                if qkey in form:
                    q['name'] = form[qkey]
                if qidkey in form:
                    q['question_id'] = int(form[qidkey])
    # Flatten for DB
    def flatten(layout):
        out = []
        for domain in layout.get('domains', []):
            dname = domain.get('name', '')
            for sub in domain.get('subdomains', []):
                sdname = sub.get('name', '')
                for q in sub.get('questions', []):
                    out.append({
                        'year_start': layout.get('layout_start_date'),
                        'year_end': layout.get('layout_end_date'),
                        'Domain': dname,
                        'SubDomain': sdname,
                        'Index_ID': q.get('question_id', 0),
                        'Name': q.get('name', ''),
                        'Date edited': layout.get('layout_start_date'),
                        'layout_id': layout_id,
                        'layout_name': layout.get('layout_name', 'New Layout')
                    })
        for meta in layout.get('metadata_list', []):
            out.append({
                'year_start': layout.get('layout_start_date'),
                'year_end': layout.get('layout_end_date'),
                'Domain': 'MetaData',
                'SubDomain': '',
                'Index_ID': meta.get('question_id', 0),
                'Name': meta.get('name', ''),
                'Date edited': layout.get('layout_start_date'),
                'layout_id': layout_id,
                'layout_name': layout.get('layout_name', 'New Layout')
            })
        return out
    # Remove all old rows and insert new for this layout_id
    database.update_layout_inplace(layout_id, flatten(layout))
    session.pop('layout_data', None)
    return redirect(url_for('layout_view', layout_id=layout_id))

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)