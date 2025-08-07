def update_layout_inplace(layout_id, json_data):
    """Delete all rows for layout_id and insert new rows for a true in-place update."""
    # Delete all rows for this layout_id
    delete_query = questions.delete().where(questions.c.layout_id == layout_id)
    conn.execute(delete_query)
    conn.commit()  # Commit the deletion
    
    # Insert new rows (with the same layout_id)
    from datetime import datetime
    values = []
    for item in json_data:
        def to_date(val):
            if isinstance(val, str):
                try:
                    return datetime.strptime(val, "%Y-%m-%d").date()
                except Exception:
                    return None
            return val
        values.append({
            'year_start': to_date(item['year_start']),
            'year_end': to_date(item['year_end']),
            'Domain': item['Domain'],
            'SubDomain': item['SubDomain'],
            'Index_ID': item['Index_ID'],
            'Name': item['Name'],
            'Date edited': to_date(item['Date edited']),
            'layout_id': layout_id,
            'layout_name': item['layout_name']
        })
    if values:
        conn.execute(questions.insert(), values)
        conn.commit()  # Commit the insertion
def fetch_all_layouts():
    """Return a list of all layouts, grouped by layout_id, with layout_name, date_edited, is_current."""
    query = select(
        questions.c.layout_id,
        questions.c.layout_name,
        func.max(questions.c['Date edited']).label('date_edited'),
        func.max(questions.c.year_end).label('year_end'),
        func.max(questions.c.year_start).label('year_start')
    ).group_by(questions.c.layout_id, questions.c.layout_name)
    result = conn.execute(query).mappings().all()
    # Mark the most recent as current
    if not result:
        return []
    # Find the layout with the latest year_end as current
    max_year_end = max([r['year_end'] for r in result if r['year_end'] is not None], default=None)
    layouts = []
    for row in result:
        layouts.append({
            'layout_id': row['layout_id'],
            'layout_name': row['layout_name'],
            'date_edited': str(row['date_edited']) if row['date_edited'] else '',
            'is_current': (row['year_end'] == max_year_end)
        })
    return layouts

def fetch_layout_jinja(layout_id):
    """Return a dict with layout_name, layout_id, domains, metadata_list, layout_start_date, layout_end_date for Jinja2."""
    rows = fetch_questions(layout_id)
    if not rows:
        return None
    layout_name = rows[0].get('layout_name', f'Layout #{layout_id}')
    # Find min/max year_start/year_end robustly
    year_starts = [r['year_start'] for r in rows if r['year_start']]
    year_ends = [r['year_end'] for r in rows if r['year_end']]
    year_start = min(year_starts) if year_starts else ''
    year_end = max(year_ends) if year_ends else ''
    # Group domains/subdomains/questions
    domains = {}
    metadata_list = []
    for r in rows:
        if r['Domain'] == 'MetaData':
            metadata_list.append({
                'id': r['id'],
                'name': r['Name'],
                'question_id': r['Index_ID']
            })
        else:
            dname = r['Domain']
            sdname = r['SubDomain']
            if dname not in domains:
                domains[dname] = {}
            if sdname not in domains[dname]:
                domains[dname][sdname] = []
            domains[dname][sdname].append({
                'id': r['id'],
                'name': r['Name'],
                'question_id': r['Index_ID']
            })
    # Convert to list structure
    domain_list = []
    for dname, subdict in domains.items():
        sub_list = []
        for sdname, qlist in subdict.items():
            sub_list.append({'id': hash(sdname), 'name': sdname, 'questions': qlist})
        domain_list.append({'id': hash(dname), 'name': dname, 'subdomains': sub_list})
    return {
        'layout_name': layout_name,
        'layout_id': layout_id,
        'domains': domain_list,
        'metadata_list': metadata_list,
        'layout_start_date': str(year_start),
        'layout_end_date': str(year_end)
    }

def empty_layout_jinja():
    """Return an empty layout structure for new layout creation."""
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
from sqlalchemy import create_engine, MetaData, Table, Column, Integer, String, Float, DateTime, Text, ForeignKey, Date, insert, select, func
import json
from datetime import date
engine = create_engine('sqlite:///data.db', echo=False)
conn = engine.connect()
meta = MetaData()
subDomains = Table('subDomains', meta,
    Column('id', Integer, primary_key=True),
    Column('year_start', Date), 
    Column('year_end', Date),   
    Column('Domain', String),
    Column('SubDomain', String),
)

questions = Table('questions', meta,
    Column('id', Integer, primary_key=True),
    Column('year_start', Date),  # Fixed
    Column('year_end', Date),    # Fixed
    Column('Domain', String),
    Column('SubDomain', String),
    Column('Index_ID', Integer),
    Column('Name', String),
    Column("Date edited",  Date),
    Column("layout_id", Integer),
    Column("layout_name", String)  # Added for layout name
)

responses = Table('responses', meta,
    Column('id', Integer, primary_key=True),
    Column('res-id', Integer),
    Column('School', String),
    Column('Grade', String),
    Column('Teacher', String),
    Column('Assessment', String),
    Column('Name', String),
    Column('Date', Date),
    Column('Index_ID', Integer),
    Column('Response', Integer)
)

meta.create_all(engine)


def insert_response(json_data):
    values_list = []
    query = insert(responses)

    today = date.today()
    if isinstance(json_data, str):
        data = json.loads(json_data)
    else:
        data = json_data
    
    # SQLAlchemy way to get MAX(res_id)
    max_query = select(func.max(responses.c.res_id))
    result = conn.execute(max_query).fetchone()
    next_res_id = (result[0] + 1) if result[0] is not None else 1
    
    # SQLAlchemy way to get valid Index_IDs
    s = questions.select().where((questions.c.year_start <= today) & (questions.c.year_end >= today) & (questions.c.Domain != "MetaData")).distinct()
    valid_index = conn.execute(s).fetchall()
    valid_index_set = {row[5] for row in valid_index}

    # Efficiently map metadata elements to their Index_IDs
    meta_elements = ["School", "Grade", "Teacher", "Assessment", "Name", "Date"]
    meta_query = questions.select().where(
        (questions.c.year_start <= today) &
        (questions.c.year_end >= today) &
        (questions.c.SubDomain.in_(meta_elements))
    ).distinct()
    meta_rows = conn.execute(meta_query).fetchall()

    # Map SubDomain to Index_ID
    meta_index_map = {row[5]: row[6] for row in meta_rows}  # row[5]=SubDomain, row[6]=Index_ID

    # Assign variables for each metadata element
    school_index = meta_index_map.get("School")
    grade_index = meta_index_map.get("Grade")
    teacher_index = meta_index_map.get("Teacher")
    assessment_index = meta_index_map.get("Assessment")
    name_index = meta_index_map.get("Name")
    date_index = meta_index_map.get("Date")
    school = data[school_index]
    grade = data[grade_index]
    teacher = data[teacher_index]
    assessment = data[assessment_index]
    name = data[name_index]
    date_val = data[date_index]
    
    for index, value in enumerate(data):
        index_id = index + 1

        if index_id in valid_index_set:
            row = {
                'res-id': next_res_id,
                'School': school,
                'Grade': grade,
                'Teacher': teacher,
                'Assessment': assessment,
                'Name': name,
                'Date': date_val,
                'Index_ID': index_id,
                'Response': value
            }
            values_list.append(row)
    if values_list:
        conn.execute(query,values_list)
        conn.commit()  # Commit the transaction

def insert_layout(json_data):
    query = insert(questions)
    read = select(func.max(questions.c.layout_id))
    result = conn.execute(read).fetchone()
    layout_id = (result[0] + 1) if result[0] is not None else 1

    from datetime import datetime
    values = []
    for item in json_data:
        def to_date(val):
            if isinstance(val, str):
                try:
                    return datetime.strptime(val, "%Y-%m-%d").date()
                except Exception:
                    return None
            return val
        values.append({
            'year_start': to_date(item['year_start']),
            'year_end': to_date(item['year_end']),
            'Domain': item['Domain'],
            'SubDomain': item['SubDomain'],
            'Index_ID': item['Index_ID'],
            'Name': item['Name'],
            'Date edited': to_date(item['Date edited']),
            'layout_id': layout_id,
            'layout_name': item['layout_name']
        })
    if values:
        conn.execute(query, values)
        conn.commit()  # Commit the transaction

def update_layout(layout_id, json_data):
    query = questions.update().where(questions.c.layout_id == json_data['layout_id'])
    values = {
        'year_start': json_data['year_start'],
        'year_end': json_data['year_end'],
        'Domain': json_data['Domain'],
        'SubDomain': json_data['SubDomain'],
        'Index_ID': json_data['Index_ID'],
        'Name': json_data['Name'],
        'Date edited': json_data['Date edited'],
        'layout_name': json_data['layout_name']
    }
    conn.execute(query.values(values))
    conn.commit()  # Commit the transaction

def delete_layout(layout_id):
    """Delete all rows for a specific layout_id."""
    delete_query = questions.delete().where(questions.c.layout_id == layout_id)
    conn.execute(delete_query)
    conn.commit()  # Commit the deletion

def fetch_questions(request=None):
    query = select(questions)
    if request is not None:
        query = query.where(questions.c.layout_id == request)
    result = conn.execute(query).fetchall()
    return [dict(row._mapping) for row in result]