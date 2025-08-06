from flask import Flask, render_template, jsonify, redirect

app = Flask(__name__)

@app.route('/')
def home():
    return render_template('homepage.html')


# /linkage shows all layouts
@app.route('/linkage')
def linkage():
    from datetime import datetime
    current_year = datetime.now().year
    return render_template('layout_view.html', current_year=current_year)

# /linkage/view/<layout_id> shows a specific layout
@app.route('/linkage/view/<int:layout_id>')
def linkage_view(layout_id):
    from datetime import datetime
    current_year = datetime.now().year
    return render_template('layout_viewer.html', current_year=current_year, layout_id=layout_id)

# /layout/edit/new creates a new layout
@app.route('/layout/edit/new')
def layout_edit_new():
    from datetime import datetime
    current_year = datetime.now().year
    return render_template('layout_builder.html', current_year=current_year)

# /layout/edit/<layout_id> edits an existing layout (stub)
@app.route('/layout/edit/<int:layout_id>')
def layout_edit(layout_id):
    from datetime import datetime
    current_year = datetime.now().year
    return render_template('layout_builder.html', current_year=current_year, layout_id=layout_id)

@app.route('/linkage/edit')
def linkage_edit():
    from datetime import datetime
    current_year = datetime.now().year
    return render_template('layout_builder.html', current_year=current_year)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000) 

@app.route('/api/dashboard')
def api():
    print("API called"	)