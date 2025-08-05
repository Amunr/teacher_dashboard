from sqlalchemy import create_engine, MetaData, Table, Column, Integer, String, Float, DateTime, Text, ForeignKey, Date, insert

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
    Column('Question_ID', Integer),
)

responses = Table('responses', meta,
    Column('id', Integer, primary_key=True),
    Column('res-id', Integer)
    Column('School', String),
    Column('Grade', String),
    Column('Teacher', String),
    Column('Assessment', String),
    Column('Name', String),
    Column('Date', Date),
    Column('Question_ID', Integer),
    Column('Response', Integer),
)

meta.create_all(engine)


def insert_response(data):
    query = insert(responses)
    values_list = []
    for r in data:
        values_list.append(
        'School': data['School'],
        'Grade' : data['Grade'],
        'Teacher': data['Teacher'],
        'Assessment': data['Assessment'],
        'Name': data['Name'],
        'Date': data['Date'],
        'Question_ID': r['Question_ID'],
        'Response': r['Response']
        )