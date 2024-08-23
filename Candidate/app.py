from flask import Flask, render_template, request, redirect
from flask_pymongo import PyMongo

app = Flask(__name__)

# MongoDB configuration
app.config["MONGO_URI"] = "mongodb+srv://nithishgihub:6Ehv1X8OCa2Rtgyl@cluster0.jnj2s.mongodb.net/yourDatabaseName?retryWrites=true&w=majority"
mongo = PyMongo(app)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/submit', methods=['POST'])
def submit():
    # Get data from the form
    form_data = {
        'name': request.form.get('name'),
        'email': request.form.get('email'),
        'bmc_video_link': request.form.get('bmc_video_link'),
        'startup_name': request.form.get('startup_name'),
        'problem_statement': request.form.get('problem_statement'),
        'description': request.form.get('description'),
        'current_status': request.form.get('current_status'),
        'sns_institution': request.form.get('sns_institution'),
        'team_details': request.form.get('team_details'),
        'industry_vertical': request.form.get('industry_vertical'),
        'industry_technology': request.form.get('industry_technology')
    }

    # Insert the data into MongoDB
    try:
        mongo.db.startup_details.insert_one(form_data)
    except Exception as e:
        return f"Error inserting data: {e}", 500

    # Render acknowledgment page
    return render_template('acknowledgment.html')

if __name__ == '__main__':
    app.run(debug=True)
