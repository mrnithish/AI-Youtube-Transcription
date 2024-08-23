from flask import Flask, render_template, request, redirect
from flask_pymongo import PyMongo

app = Flask(__name__)

# MongoDB configuration

app.config["MONGO_URI"] = "mongodb+srv://nithishgihub:6Ehv1X8OCa2Rtgyl@cluster0.jnj2s.mongodb.net/yourDatabaseName?retryWrites=true&w=majority"
mongo = PyMongo(app)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
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
            'name': request.form.get('name'),
            'email': request.form.get('email'),
            'experience': request.form.get('experience'),
            'interest': request.form.get('interest'),
            'industry_verticals': industry_verticals,
            'technologies': technologies
        }

        # Insert the data into MongoDB
        try:
            mongo.db.product_managers.insert_one(form_data)
        except Exception as e:
            return f"Error inserting data: {e}", 500

        return redirect('/dashboard')

    return render_template('signup.html')

@app.route('/dashboard')
def dashboard():
    # Retrieve all product managers from MongoDB
    product_managers = mongo.db.product_managers.find()
    return render_template('dashboard.html', product_managers=product_managers)

if __name__ == '__main__':
    app.run(debug=True)
