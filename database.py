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

def insert_layout(json_data):
    query = insert(questions)
    read = select(func.max(questions.c.layout_id))
    result = conn.execute(read).fetchone()
    layout_id = (result[0] + 1) if result[0] is not None else 1

    values = []
    for item in json_data:
        values.append({
            'year_start': item['year_start'],
            'year_end': item['year_end'],
            'Domain': item['Domain'],
            'SubDomain': item['SubDomain'],
            'Index_ID': item['Index_ID'],
            'Name': item['Name'],
            'Date edited': item['Date edited'],
            'layout_id': layout_id,
            'layout_name': item['layout_name']
        })
    if values:
        conn.execute(query, values)

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

def fetch_questions(request=None):
    query = select(questions)
    if request is not None:
        query = query.where(questions.c.layout_id == request)
    result = conn.execute(query).fetchall()
    return [dict(row) for row in result]