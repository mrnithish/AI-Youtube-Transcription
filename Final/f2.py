from flask import Flask, render_template, redirect, url_for, request, flash, make_response
from flask_pymongo import PyMongo
from flask_bcrypt import Bcrypt
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from bson.objectid import ObjectId
from rank import ProductManager, rank_pm, generate_feedback
import os

app = Flask(__name__)
app.secret_key = os.urandom(24)

# MongoDB configuration
app.config["MONGO_URI"] = "mongodb+srv://nithishgihub:6Ehv1X8OCa2Rtgyl@cluster0.jnj2s.mongodb.net/yourDatabaseName?retryWrites=true&w=majority"
mongo = PyMongo(app)

bcrypt = Bcrypt(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'

@login_manager.user_loader
def load_user(user_id):
    user_data = mongo.db.product_managers.find_one({"_id": ObjectId(user_id)})
    if user_data:
        return ProductManager(
            name=user_data.get('name'),
            industry_priorities=user_data.get('industry_verticals'),
            tech_priorities=user_data.get('technology_stack'),
            project_status_priorities=user_data.get('project_status'),
            experience=user_data.get('years_experience', 0),
            performance_score=user_data.get('performance_score', 0),
            current_workload=user_data.get('active_projects', 0),
        )
    return None

def fetch_all_startups():
    return mongo.db.startup_details.find()

def fetch_product_managers():
    product_managers_data = mongo.db.product_managers.find()
    product_managers = []
    
    for pm_data in product_managers_data:
        pm = ProductManager(
            name=pm_data['name'],
            industry_priorities=pm_data.get('industry_verticals', []),
            tech_priorities=pm_data.get('technology_stack', []),
            project_status_priorities=pm_data.get('project_status', []),
            experience=int(pm_data.get('years_experience', 0)),
            performance_score=int(pm_data.get('performance_score', 0)),
            current_workload=int(pm_data.get('active_projects', 0))
        )
        product_managers.append(pm)
    
    return product_managers

def allot_projects():
    startups = fetch_all_startups()
    product_managers = fetch_product_managers()

    for startup in startups:
        # Extract necessary startup details
        startup_id = str(startup['_id'])
        problem_statement = startup['problem_statement']
        tech_stack = startup.get('industry_technology', [])  # Assuming this is a list
        industry_vertical = startup.get('industry_vertical', '')
        project_status = startup.get('current_status', '')

        # Rank the PMs based on the startup details
        ranked_pms = rank_pm(product_managers, tech_stack, industry_vertical, project_status)
        
        if not ranked_pms:
            print(f"No suitable Product Manager found for startup {startup_id}")
            continue

        # Get the best PM
        best_pm_name = ranked_pms[0][4]

        # Generate feedback
        feedback = generate_feedback(ranked_pms, tech_stack, industry_vertical, project_status)
        print(f'Project for startup {startup_id} has been allotted to {best_pm_name}.')
        print(feedback)

        # Store the project allotment in the project_details collection
        project_details = {
            "startup_id": startup_id,
            "problem_statement": problem_statement,
            "tech_stack": tech_stack,
            "industry_vertical": industry_vertical,
            "project_status": project_status,
            "assigned_pm": best_pm_name,
            "pm_ranking": [pm[4] for pm in ranked_pms],  # Storing the PM ranking order
            "feedback" : feedback
        }

        mongo.db.project_details.insert_one(project_details)

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
            'industry_verticals': industry_verticals,
            'technology_stack': technology_stack,
            'project_status': project_status,
            'years_experience': years_experience,
            'performance_score': data.get('performance_score'),
            'active_projects': data.get('active_projects')
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
                industry_priorities=user['industry_verticals'],
                tech_priorities=user['technology_stack'],
                project_status_priorities=user['project_status'],
                experience=user['years_experience'],
                performance_score=user['performance_score'],
                current_workload=user['active_projects']
            ))
            return redirect(url_for('dashboard'))
        flash('Invalid email or password', 'danger')
    return render_template('login.html')

@app.route('/dashboard')
@login_required
def dashboard():
    response = make_response(render_template('dashboard.html', user=current_user))
    response.headers['Cache-Control'] = 'no-store'
    return response

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

    try:
        mongo.db.startup_details.insert_one(form_data)
        allot_projects()
    except Exception as e:
        return f"Error inserting data: {e}", 500

    return render_template('acknowledgment.html')

if __name__ == '__main__':
    app.run(debug=True)
