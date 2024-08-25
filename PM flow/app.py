from flask import Flask, render_template, request, redirect, url_for, session, flash
from flask_pymongo import PyMongo
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your_secret_key_here'  # Replace with your actual secret key

# MongoDB configuration
app.config["MONGO_URI"] = "mongodb+srv://nithishgihub:6Ehv1X8OCa2Rtgyl@cluster0.jnj2s.mongodb.net/yourDatabaseName?retryWrites=true&w=majority"
mongo = PyMongo(app)

@app.route('/')
def index():
    if 'user' in session:
        return redirect(url_for('dashboard'))
    return render_template('index.html')

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email')
        password = request.form.get('password')  # Collect password
        hashed_password = generate_password_hash(password, method='sha256')
        
        industry_verticals = []
        technologies = []
        
        # Extract priorities and corresponding values for industry verticals
        for i in range(1, 9):  # Adjust range if needed
            vertical = request.form.get(f'industry_verticals_{i}')
            if vertical:
                industry_verticals.append({'vertical': vertical, 'priority': i})
        
        # Extract priorities and corresponding values for technologies
        for i in range(1, 8):  # Adjust range if needed
            tech = request.form.get(f'technologies_{i}')
            if tech:
                technologies.append({'technology': tech, 'priority': i})
        
        form_data = {
            'name': name,
            'email': email,
            'password': hashed_password,  # Store hashed password
            'experience': request.form.get('experience'),
            'interest': request.form.get('interest'),
            'industry_verticals': industry_verticals,
            'technologies': technologies
        }

        # Insert the data into MongoDB
        try:
            mongo.db.product_managers.insert_one(form_data)
            flash('Signup successful! Please log in.')
            return redirect('/login')
        except Exception as e:
            return f"Error inserting data: {e}", 500

    return render_template('signup.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        
        # Find user by email
        user = mongo.db.product_managers.find_one({'email': email})
        
        if user and check_password_hash(user['password'], password):
            session['user'] = email
            flash('Login successful!')
            return redirect('/dashboard')
        else:
            flash('Login failed. Check your email and/or password.')
    
    return render_template('login.html')

@app.route('/dashboard')
def dashboard():
    if 'user' not in session:
        return redirect('/login')
    
    # Retrieve all product managers from MongoDB
    product_managers = mongo.db.product_managers.find()
    return render_template('dashboard.html', product_managers=product_managers)

@app.route('/logout')
def logout():
    session.pop('user', None)
    flash('You have been logged out.')
    return redirect('/')

if __name__ == '__main__':
    app.run(debug=True)
