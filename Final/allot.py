from pymongo import MongoClient
from rank import ProductManager, rank_pm, generate_feedback

# MongoDB connection string
MONGO_URI = "mongodb+srv://nithishgihub:6Ehv1X8OCa2Rtgyl@cluster0.jnj2s.mongodb.net/yourDatabaseName?retryWrites=true&w=majority"

# Connect to MongoDB
client = MongoClient(MONGO_URI)
db = client['yourDatabaseName']  # Replace 'yourDatabaseName' with your actual database name

def fetch_all_startups():
    return db.startup_details.find().sort('created_at', -1).limit(1)

def fetch_product_managers():
    product_managers_data = db.product_managers.find()
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
        # print(f'Project for startup {startup_id} has been allotted to {best_pm_name}.')
        # print(feedback)

        # Store the project allotment in the project_details collection
        project_details = {
            "startup_id": startup_id,
            "problem_statement": problem_statement,
            "tech_stack": tech_stack,
            "industry_vertical": industry_vertical,
            "project_status": project_status,
            "assigned_pm": best_pm_name,
            "pm_ranking": [pm[4] for pm in ranked_pms],  # Storing the PM ranking order
            "Feedback" : feedback
        }

        db.project_details.insert_one(project_details)


