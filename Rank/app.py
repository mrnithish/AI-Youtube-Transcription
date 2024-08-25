
from flask import Flask, render_template, redirect, url_for, request, flash, make_response
from flask_pymongo import PyMongo
from flask_bcrypt import Bcrypt
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from bson.objectid import ObjectId
import os
import Rank.rank as rank  # Importing the rank.py script

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

        years_experience = data.get('experience')
        if not years_experience:
            flash('Years of experience is required', 'danger')
            return redirect(url_for('signup'))

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
        startup_id = mongo.db.startup_details.insert_one(form_data).inserted_id

        product_managers = list(mongo.db.product_managers.find())

        pm_objects = []
        for pm in product_managers:
            pm_obj = rank.ProductManager(pm['name'])
            pm_obj.industry_priorities = {ind: 5 for ind in pm['industry_verticals']}
            pm_obj.tech_priorities = {tech: 5 for tech in pm['technology_stack']}
            pm_obj.project_status_priorities = {status: 5 for status in pm['project_status']}
            pm_obj.experience = pm['years_experience']
            pm_obj.performance_score = pm['performance_score']
            pm_obj.current_workload = pm['active_projects']
            pm_objects.append(pm_obj)

        problem_statement = form_data['problem_statement']
        tech_stack = form_data['industry_technology']
        industry_vertical = form_data['industry_vertical']
        project_status = form_data['current_status']

        ranked_pms = rank.rank_pm(pm_objects, tech_stack, industry_vertical, project_status)

        mongo.db.pm_projects.insert_one({
            'startup_id': startup_id,
            'startup_name': form_data['startup_name'],
            'ranked_pms': ranked_pms
        })

        return render_template('acknowledgment.html')

    except Exception as e:
        return f"Error inserting data: {e}", 500

if __name__ == '__main__':
    app.run(debug=True)
