from flask import Flask, render_template, redirect, url_for, request, flash,make_response
from flask_pymongo import PyMongo
from flask_bcrypt import Bcrypt
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from bson.objectid import ObjectId
import os

app = Flask(__name__)
app.secret_key = os.urandom(24)  # Ensure secret_key is set for session management
app.config["MONGO_URI"] = "mongodb+srv://nithishgihub:6Ehv1X8OCa2Rtgyl@cluster0.jnj2s.mongodb.net/yourDatabaseName?retryWrites=true&w=majority"
app.config.update(
    SESSION_COOKIE_SECURE=True,  # Only send cookies over HTTPS
    REMEMBER_COOKIE_SECURE=True,  # Only send remember me cookies over HTTPS
    SESSION_COOKIE_HTTPONLY=True,  # Prevent JavaScript access to cookies
)

mongo = PyMongo(app)
bcrypt = Bcrypt(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'

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
            name=user_data['name'],
            email=user_data['email'],
            password=user_data['password'],
            years_experience=user_data['years_experience'],
            performance_score=user_data['performance_score'],
            active_projects=user_data['active_projects'],
            industry_verticals=user_data['industry_verticals'],
            technology_stack=user_data['technology_stack'],
            project_status=user_data['project_status'],
            _id=str(user_data['_id'])
        )
    return None

@app.route('/')
def index():
    return render_template('index.html')


@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        data = request.form
        existing_user = mongo.db.product_managers.find_one({"email": data['email']})
        if existing_user:
            flash('Email already exists', 'danger')
            return redirect(url_for('signup'))

        industry_verticals = [data[f'industry_{i}'] for i in range(1, 4)]
        technology_stack = [data[f'tech_{i}'] for i in range(1, 4)]
        project_status = data['project_status']

        product_manager = ProductManager(
            name=data['name'],
            email=data['email'],
            password=bcrypt.generate_password_hash(data['password']).decode('utf-8'),
            years_experience=data['years_experience'],
            performance_score=data['performance_score'],
            active_projects=data['active_projects'],
            industry_verticals=industry_verticals,
            technology_stack=technology_stack,
            project_status=project_status
        )
        mongo.db.product_managers.insert_one(product_manager.__dict__)
        flash('Signup successful! Please log in.', 'success')
        return redirect(url_for('login'))
    return render_template('signup.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        data = request.form
        user = mongo.db.product_managers.find_one({"email": data['email']})
        if user and bcrypt.check_password_hash(user['password'], data['password']):
            user_obj = ProductManager(
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
            )
            login_user(user_obj)
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
if __name__ == '__main__':
    app.run(debug=True)
