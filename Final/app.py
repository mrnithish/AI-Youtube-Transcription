from flask import Flask, render_template, redirect, url_for, request, flash, make_response
from flask_pymongo import PyMongo
from flask_bcrypt import Bcrypt
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from bson.objectid import ObjectId
from allot import allot_projects
import os,jsonify
from flask import Flask, jsonify, request

app = Flask(__name__)
app.secret_key = os.urandom(24)

# MongoDB configuration
app.config["MONGO_URI"] = "mongodb+srv://nithishgihub:6Ehv1X8OCa2Rtgyl@cluster0.jnj2s.mongodb.net/yourDatabaseName?retryWrites=true&w=majority"
mongo = PyMongo(app)

bcrypt = Bcrypt(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'

# Product Manager Model
class ProductManager(UserMixin):
    def __init__(self, name, email, password, years_experience, performance_score, active_projects, industry_verticals, technology_stack, project_status, _id=None):
        self.id = _id
        self.name = name
        self.email = email
        self.password = password
        self.years_experience = years_experience
        self.performance_score = performance_score
        self.active_projects = active_projects
        self.industry_verticals = industry_verticals
        self.technology_stack = technology_stack
        self.project_status = project_status


@login_manager.user_loader
def load_user(user_id):
    user_data = mongo.db.product_managers.find_one({"_id": ObjectId(user_id)})
    if user_data:
        return ProductManager(
            name=user_data.get('name'),
            email=user_data.get('email'),
            password=user_data.get('password'),
            years_experience=user_data.get('years_experience'),
            performance_score=user_data.get('performance_score'),
            active_projects=user_data.get('active_projects'),
            industry_verticals=user_data.get('industry_verticals'),
            technology_stack=user_data.get('technology_stack'),
            project_status=user_data.get('project_status'),
            _id=user_id
        )
    return None

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        data = request.form

        years_experience = data.get('experience')  # Use .get() to avoid KeyError
        if not years_experience:
            flash('Years of experience is required', 'danger')
            return redirect(url_for('signup'))

        # Continue with other fields and processing
        industry_verticals = [data.get(f'industry_verticals_{i}') for i in range(1, 9) if data.get(f'industry_verticals_{i}')]
        technology_stack = [data.get(f'technologies_{i}') for i in range(1, 8) if data.get(f'technologies_{i}')]
        project_status = [data.get(f'project_statuses_{i}') for i in range(1, 5) if data.get(f'project_statuses_{i}')]

        product_manager = {
            'name': data.get('name'),
            'email': data.get('email'),
            'password': bcrypt.generate_password_hash(data.get('password')).decode('utf-8'),
            'years_experience': years_experience,
            'performance_score': data.get('performance_score'),
            'active_projects': data.get('active_projects'),
            'industry_verticals': industry_verticals,
            'technology_stack': technology_stack,
            'project_status': project_status
        }

        try:
            mongo.db.product_managers.insert_one(product_manager)
            flash('Signup successful! Please log in.', 'success')
            return redirect(url_for('login'))
        except Exception as e:
            flash(f'Error occurred: {e}', 'danger')
            return redirect(url_for('signup'))
    return render_template('signup.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        data = request.form
        user = mongo.db.product_managers.find_one({"email": data['email']})
        if user and bcrypt.check_password_hash(user['password'], data['password']):
            login_user(ProductManager(
                name=user['name'],
                email=user['email'],
                password=user['password'],
                years_experience=user['years_experience'],
                performance_score=user['performance_score'],
                active_projects=user['active_projects'],
                industry_verticals=user['industry_verticals'],
                technology_stack=user['technology_stack'],
                project_status=user['project_status'],
                _id=str(user['_id'])
            ))
            return redirect(url_for('dashboard'))
        flash('Invalid email or password', 'danger')
    return render_template('login.html')




@app.route('/dashboard')
@login_required
def dashboard():
    # Get the current PM's user ID from the database
    pm_id = mongo.db.product_managers.find_one({"name": current_user.name}, {"_id": 1})['_id']

    # Check if pm_id already exists in the pm_slots collection
    pm_slot_exists = mongo.db.pm_slots.find_one({"pm_id": str(pm_id)}, {"_id": 1})

    # If pm_id does not exist, update the ideas array
    if not pm_slot_exists:
        # Query project_details to find all projects assigned to the current PM using their ID
        assigned_projects = mongo.db.project_details.find({"assigned_pm_id": pm_id})

        # Create a list to store project IDs
        project_ids = []

        # Iterate through the assigned projects and collect the project IDs
        for project in assigned_projects:
            project_ids.append(str(project['_id']))  # Store the project ID as a string

        # Update the pm_slots collection to store the assigned project IDs in the 'ideas' array
        mongo.db.pm_slots.update_one(
            {'pm_id': str(pm_id)},
            {'$set': {'ideas': project_ids}},
            upsert=True
        )

    # Step 2: Retrieve and Display Startup Details Based on `ideas` Array

    # Fetch the `pm_slots` document for the current PM
    pm_slot = mongo.db.pm_slots.find_one({"pm_id": str(pm_id)}, {"ideas": 1})

    # Initialize the list to store projects with corresponding startup details
    projects_with_startup_details = []

    if pm_slot and "ideas" in pm_slot:
        # Iterate through the 'ideas' array to fetch project and startup details
        for project_id in pm_slot['ideas']:
            # Convert project_id to ObjectId and fetch project details
            project = mongo.db.project_details.find_one({"_id": ObjectId(project_id)})

            if project:
                # Get the startup_id from the project
                startup_id = project.get('startup_id')

                # Fetch the corresponding startup details using the startup_id
                startup_details = mongo.db.startup_details.find_one({"_id": ObjectId(startup_id)})

                if startup_details:
                    # Append project and startup details to the list
                    projects_with_startup_details.append({
                        "project": project,
                        "startup_details": startup_details
                    })

    # Print debug information
    print(f"Projects in 'Ideas' for PM ID {pm_id}:")
    for proj in projects_with_startup_details:
        print(f"Project ID: {proj['project'].get('_id')}, Startup ID: {proj['project'].get('startup_id')}")

    # Render the dashboard with the user's projects that are still in the 'Ideas' stage
    return render_template('dashboard.html', user=current_user, projects=projects_with_startup_details)





@app.route('/interested', methods=['POST'])
@login_required
def mark_interested():
    try:
        data = request.get_json()  # Get JSON data from the request
        project_id = data.get('project_id')

        if not project_id:
            return jsonify({'message': 'No project ID provided.'}), 400

        # Fetch the current PM's ID
        pm_id = current_user.id

        # Update the pm_slots collection:
        # 1. Remove the project_id from the 'ideas' array.
        # 2. Add the project_id to the 'interested' array.
        result = mongo.db.pm_slots.update_one(
            {'pm_id': pm_id},
            {
                '$pull': {'ideas': project_id},       # Remove project_id from ideas array
                '$addToSet': {'interested': project_id}  # Add project_id to interested array
            },
            upsert=True
        )

        if result.modified_count > 0 or result.upserted_id:
            return jsonify({'message': 'Project marked as interested!'}), 200
        else:
            return jsonify({'message': 'Failed to mark project as interested.'}), 400
    except Exception as e:
        print(f"Error occurred: {e}")  # Log the error to the console
        return jsonify({'message': f'Error marking project as interested: {str(e)}'}), 500





@app.route('/interested_startups')
@login_required
def interested_startups_page():
    pm_id = current_user.id
    pm_slots = mongo.db.pm_slots.find_one({'pm_id': pm_id})
    interested_project_ids = pm_slots.get('interested', []) if pm_slots else []

    interested_projects = []
    for project_id in interested_project_ids:
        project = mongo.db.project_details.find_one({'_id': ObjectId(project_id)})
        if project:
            startup = mongo.db.startup_details.find_one({'_id': ObjectId(project['startup_id'])})
            interested_projects.append({
                'project': project,
                'startup_details': startup
            })

    return render_template('interested_startups.html', user=current_user, projects=interested_projects)


@app.route('/shortlist_startup', methods=['POST'])
@login_required
def shortlist_startup():
    project_id = request.form.get('project_id')

    # Find the project and update the PM's interested and shortlisted lists
    pm_id = current_user.id
    pm_slots = mongo.db.pm_slots.find_one({'pm_id': pm_id})

    if pm_slots:
        interested = pm_slots.get('interested', [])
        shortlisted = pm_slots.get('shortlisted', [])

        # Remove from interested array if it exists
        if project_id in interested:
            interested.remove(project_id)

        # Add to shortlisted array if it's not already there
        if project_id not in shortlisted:
            shortlisted.append(project_id)
            mongo.db.pm_slots.update_one({'pm_id': pm_id}, {'$set': {'shortlisted': shortlisted, 'interested': interested}})
            message = "Project has been moved to shortlisted."
        else:
            message = "Project is already in the shortlisted list."
    else:
        # If pm_slots doesn't exist, create it with the new shortlisted project
        mongo.db.pm_slots.insert_one({
            'pm_id': pm_id,
            'shortlisted': [project_id]
        })
        message = "Project has been shortlisted."

    return redirect(url_for('interested_startups_page'))

@app.route('/shortlisted_startups')
@login_required
def shortlisted_startups_page():
    pm_id = current_user.id
    pm_slots = mongo.db.pm_slots.find_one({'pm_id': pm_id})
    shortlisted_project_ids = pm_slots.get('shortlisted', []) if pm_slots else []

    shortlisted_projects = []
    for project_id in shortlisted_project_ids:
        project = mongo.db.project_details.find_one({'_id': ObjectId(project_id)})
        if project:
            startup = mongo.db.startup_details.find_one({'_id': ObjectId(project['startup_id'])})
            shortlisted_projects.append({
                'project': project,
                'startup_details': startup
            })

    return render_template('shortlisted_startups.html', user=current_user, projects=shortlisted_projects)

@app.route('/finalize_startup', methods=['POST'])
@login_required
def finalize_startup():
    try:
        project_id = request.form.get('project_id')

        # Find the PM's document
        pm_id = current_user.id
        pm_slots = mongo.db.pm_slots.find_one({'pm_id': pm_id})

        if pm_slots:
            shortlisted = pm_slots.get('shortlisted', [])
            finalized = pm_slots.get('finalized', [])

            # Remove from shortlisted array if it exists
            if project_id in shortlisted:
                shortlisted.remove(project_id)

            # Add to finalized array if it's not already there
            if project_id not in finalized:
                finalized.append(project_id)
                mongo.db.pm_slots.update_one({'pm_id': pm_id}, {'$set': {'shortlisted': shortlisted, 'finalized': finalized}})
                flash('Project has been finalized successfully!', 'success')
            else:
                flash('Project is already in the finalized list.', 'info')
        else:
            # If pm_slots doesn't exist, create it with the new finalized project
            mongo.db.pm_slots.insert_one({
                'pm_id': pm_id,
                'finalized': [project_id]
            })
            flash('Project has been finalized successfully!', 'success')

    except Exception as e:
        print(f"Error occurred: {e}")  # Log the error to the console
        flash('Error finalizing the project.', 'danger')

    return redirect(url_for('shortlisted_startups_page'))

@app.route('/finalized_startups')
@login_required
def finalized_startups_page():
    pm_id = current_user.id
    pm_slots = mongo.db.pm_slots.find_one({'pm_id': pm_id})
    finalized_project_ids = pm_slots.get('finalized', []) if pm_slots else []

    finalized_projects = []
    for project_id in finalized_project_ids:
        project = mongo.db.project_details.find_one({'_id': ObjectId(project_id)})
        if project:
            startup = mongo.db.startup_details.find_one({'_id': ObjectId(project['startup_id'])})
            finalized_projects.append({
                'project': project,
                'startup_details': startup
            })

    return render_template('finalized_startups.html', user=current_user, projects=finalized_projects)






@app.route('/surplus')
@login_required
def surplus():
    # Fetch all project details from the project_details collection
    all_projects = mongo.db.project_details.find()

    # Initialize the list to store projects with corresponding startup details
    projects_with_startup_details = []

    # Iterate through all projects and fetch corresponding startup details
    for project in all_projects:
        # Get the startup_id from the project
        startup_id = project.get('startup_id')

        # Fetch the corresponding startup details using the startup_id
        startup_details = mongo.db.startup_details.find_one({"_id": ObjectId(startup_id)})

        # Append project and startup details to the list
        projects_with_startup_details.append({
            "project": project,
            "startup_details": startup_details
        })

    # Render the surplus page with all project details and corresponding startup details
    return render_template('surplus.html', user=current_user, projects=projects_with_startup_details)






@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Logged out successfully', 'success')
    response = make_response(redirect(url_for('login')))
    response.headers['Cache-Control'] = 'no-store'
    return response

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
        allot_projects()
    except Exception as e:
        return f"Error inserting data: {e}", 500

    # Render acknowledgment page
    return render_template('acknowledgment.html')

if __name__ == '__main__':
    app.run(debug=True)
