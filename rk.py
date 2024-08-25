import heapq

class ProductManager:
    def __init__(self, name, industry_priorities=None, tech_priorities=None, 
                 project_status_priorities=None, experience=0, performance_score=0, 
                 current_workload=0, active_projects=0):
        self.name = name
        self.industry_priorities = self.create_priority_dict(industry_priorities)
        self.tech_priorities = self.create_priority_dict(tech_priorities)
        self.project_status_priorities = self.create_priority_dict(project_status_priorities)
        self.experience = int(experience)
        self.performance_score = int(performance_score)
        self.current_workload = int(current_workload)
        self.active_projects = int(active_projects)

    def create_priority_dict(self, priorities_list):
        if priorities_list is None:
            return {}
        return {item: len(priorities_list) - index for index, item in enumerate(priorities_list)}

def rank_pm(pms, tech_stack, industry_vertical, project_status):
    ranked_pms = []

    # Define maximum possible scores for normalization
    max_industry_score = 5.0
    max_tech_score = 3.0
    max_status_score = 1.5
    max_experience_score = 0.5
    max_performance_score = 0.5
    max_workload_penalty = 0.5

    for pm in pms:
        # Calculate scores based on priority order and normalize them
        industry_score = pm.industry_priorities.get(industry_vertical, 0)
        normalized_industry_score = min(industry_score, 5) / 5 * max_industry_score
        
        tech_score = sum(pm.tech_priorities.get(tech, 0) for tech in tech_stack)
        normalized_tech_score = min(tech_score, 5) / 5 * max_tech_score
        
        status_score = pm.project_status_priorities.get(project_status, 0)
        normalized_status_score = min(status_score, 5) / 5 * max_status_score

        # Experience and performance are also normalized
        normalized_experience_score = min(pm.experience, 10) / 10 * max_experience_score
        normalized_performance_score = min(pm.performance_score, 10) / 10 * max_performance_score

        # Calculate the total score
        total_score = (
            normalized_industry_score +
            normalized_tech_score +
            normalized_status_score +
            normalized_experience_score +
            normalized_performance_score
        )

        # Adjust score for current workload, fewer active projects is better
        workload_adjustment = pm.current_workload * max_workload_penalty / 10
        adjusted_score = total_score - workload_adjustment

        # Ensure that the adjusted score does not exceed 10 or go below 0
        adjusted_score = max(0, min(adjusted_score, 10))

        heapq.heappush(ranked_pms, (-adjusted_score, total_score, pm.experience, pm.performance_score, pm.name, workload_adjustment))

    return ranked_pms

def generate_feedback(ranked_pms, tech_stack, industry_vertical, project_status):
    feedback = (
        f"Ranking based on:\n"
        f"Industry Vertical: {industry_vertical}, "
        f"Tech Stack: {', '.join(tech_stack)}, "
        f"Project Status: {project_status}\n\n"
        "Ranked Product Managers:\n"
    )
    
    for idx, (neg_adjusted_score, total_score, experience, performance_score, name, workload_adjustment) in enumerate(ranked_pms, 1):
        adjusted_score = -neg_adjusted_score
        feedback += (
            f"{idx}. {name} - Adjusted Score: {adjusted_score:.2f}, "
            f"Total Score: {total_score:.2f}, "
            f"Experience: {experience} years, "
            f"Performance Score: {performance_score}, "
            f"Current Workload Adjustment: {workload_adjustment:.2f}\n"
        )
    
    return feedback
