import heapq
from collections import defaultdict

class ProductManager:
    def _init_(self, name):
        self.name = name
        self.industry_priorities = {}
        self.tech_priorities = {}
        self.project_status_priorities = {}
        self.experience = 0  # Experience level in years or relevant metric
        self.performance_score = 0  # Performance metric (e.g., on-time delivery, quality, etc.)
        self.current_workload = 0  # Number of active projects or workload score
        self.active_projects = 0  # Number of currently assigned projects

    def set_priorities(self):
        print(f"\nEnter priorities for {self.name} (scale of 1-10):")
        
        print("Set priorities for industries:")
        for industry in industries:
            priority = self.get_valid_priority(f"  Priority for industry '{industry}': ", 1, 10)
            self.industry_priorities[industry] = priority
        
        print("Set priorities for technologies:")
        for tech in technologies:
            priority = self.get_valid_priority(f"  Priority for technology '{tech}': ", 1, 10)
            self.tech_priorities[tech] = priority
        
        print("Set priorities for project statuses:")
        for status in project_statuses:
            priority = self.get_valid_priority(f"  Priority for project status '{status}': ", 1, 10)
            self.project_status_priorities[status] = priority

        self.experience = self.get_valid_priority(f"  Enter experience in years for {self.name} (no limit): ", 0, float('inf'))
        self.performance_score = self.get_valid_priority(f"  Enter performance score (scale of 1-10) for {self.name}: ", 1, 10)
        self.current_workload = self.get_valid_priority(f"  Enter current workload (number of active projects) for {self.name}: ", 0, float('inf'))

    @staticmethod
    def get_valid_priority(prompt, min_val, max_val):
        while True:
            try:
                priority = float(input(prompt))
                if min_val <= priority <= max_val:
                    return priority
                else:
                    print(f"Value must be between {min_val} and {max_val}.")
            except ValueError:
                print(f"Please enter a valid number between {min_val} and {max_val}.")

def get_candidate_input():
    print("Enter the problem statement:")
    problem_statement = input("> ")

    print("\nSelect the technology stack from the following options:")
    for i, tech in enumerate(technologies):
        print(f"{i + 1}. {tech}")
    tech_stack = technologies[get_valid_index(technologies, "> ")]

    print("\nSelect the industry vertical from the following options:")
    for i, industry in enumerate(industries):
        print(f"{i + 1}. {industry}")
    industry_vertical = industries[get_valid_index(industries, "> ")]

    print("\nSelect the project status from the following options:")
    for i, status in enumerate(project_statuses):
        print(f"{i + 1}. {status}")
    project_status = project_statuses[get_valid_index(project_statuses, "> ")]

    return problem_statement, tech_stack, industry_vertical, project_status

def get_valid_index(options, prompt):
    while True:
        try:
            index = int(input(prompt)) - 1
            if 0 <= index < len(options):
                return index
            else:
                print(f"Please select a valid option between 1 and {len(options)}.")
        except ValueError:
            print(f"Please enter a valid integer between 1 and {len(options)}.")

def rank_pm(pms, tech_stack, industry_vertical, project_status):
    ranked_pms = []

    for pm in pms:
        if pm.active_projects < 5:
            industry_score = pm.industry_priorities.get(industry_vertical, 0)
            tech_score = pm.tech_priorities.get(tech_stack, 0)
            status_score = pm.project_status_priorities.get(project_status, 0)
            total_score = industry_score + tech_score + status_score

            # Create a tuple of scores for sorting
            ranked_pms.append((
                total_score, 
                pm.experience, 
                pm.performance_score, 
                -pm.current_workload,  # Negative to prioritize fewer active projects
                pm.name
            ))

    # Sort PMs by total score, experience, performance score, and workload
    ranked_pms.sort(reverse=True, key=lambda x: (
        x[0],  # Total score
        x[1],  # Experience
        x[2],  # Performance score
        x[3]   # Workload (negative to prioritize fewer projects)
    ))

    return ranked_pms

def generate_feedback(ranked_pms, tech_stack, industry_vertical, project_status):
    if not ranked_pms:
        return "No suitable Product Manager found."

    feedback = "Ranking of Product Managers for the given problem statement:\n"
    for idx, pm_info in enumerate(ranked_pms, start=1):
        total_score, experience, performance_score, neg_workload, name = pm_info
        feedback += (f"{idx}. {name} - Total Score: {total_score}, "
                     f"Experience: {experience} years, "
                     f"Performance Score: {performance_score}, "
                     f"Active Projects: {-neg_workload}\n")
    
    return feedback

# Define the industries, technologies, project statuses, and projects
industries = [
    "Smart City/Manufacturing",
    "Health Care",
    "Agriculture and Food Technology",
    "Aerospace and Defence",
    "Automobile",
    "Retail (FMCG), Real Estate, Entertainment & Finance (BFSI)",
    "Power/Energy"
]

technologies = [
    "Robotics and Automation",
    "AR/VR/Metaverse Gaming and Digital Twins",
    "Data Science / AI/ML",
    "Internet of Things",
    "Communication and Growth Tech",
    "Additive Manufacturing (3D Printing)",
    "Low Code Development"
]

project_statuses = [
    "Ideation",
    "MVP",
    "Development",
    "Product Launch"
]

# Get the number of PMs
num_pms = int(input("Enter the number of Product Managers: "))

# Create PMs and set their priorities
product_managers = []
for i in range(num_pms):
    pm_name = input(f"\nEnter the name of Product Manager {i + 1}: ")
    pm = ProductManager(pm_name)
    pm.set_priorities()
    product_managers.append(pm)

# Get candidate's problem statement, tech stack, industry vertical, and project status
problem_statement, tech_stack, industry_vertical, project_status = get_candidate_input()

# Rank the Product Managers
ranked_pms = rank_pm(product_managers, tech_stack, industry_vertical, project_status)

# Generate feedback based on the ranking
feedback = generate_feedback(ranked_pms, tech_stack, industry_vertical, project_status)

print(f"\n{feedback}")

# Assign the project to the highest-ranked PM
if ranked_pms:
    best_pm_name = ranked_pms[0][4]
    print(f"\nThe problem statement should be assigned to {best_pm_name}.")
else:
    print("\nNo suitable Product Manager found.")