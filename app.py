from flask import Flask, render_template, jsonify

app = Flask(__name__)

@app.route('/')
def home():
    return render_template('homepage.html')

# API endpoints for dropdown data
@app.route('/api/schools')
def get_schools():
    return jsonify(['School A', 'School B', 'School C', 'School D'])

@app.route('/api/grades')
def get_grades():
    return jsonify(['Grade 1', 'Grade 2', 'Grade 3', 'Grade 4', 'Grade 5'])

@app.route('/api/assessments')
def get_assessments():
    return jsonify(['Mid-term', 'Final', 'Practice', 'Diagnostic'])

@app.route('/api/domains')
def get_domains():
    return jsonify(['Language Development', 'Cognitive Development', 'Social and Emotional', 'Physical Development'])

@app.route('/api/students')
def get_students():
    return jsonify(['John Doe', 'Jane Smith', 'Mike Johnson', 'Sarah Wilson', 'David Brown', 'Emily Davis'])

# API endpoints for metrics
@app.route('/api/readiness-percentage')
def get_readiness_percentage():
    return jsonify(75)

@app.route('/api/total-students')
def get_total_students():
    return jsonify(150)

@app.route('/api/students-assessed')
def get_students_assessed():
    return jsonify(142)

@app.route('/api/class-avg-score')
def get_class_avg_score():
    return jsonify(78)

@app.route('/api/glowing-skills')
def get_glowing_skills():
    return jsonify(['Critical Thinking', 'Problem Solving'])

@app.route('/api/growing-skills')
def get_growing_skills():
    return jsonify(['Communication', 'Teamwork'])

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000) 