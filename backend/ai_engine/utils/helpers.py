import re
from typing import List, Dict, Any
from datetime import datetime, timedelta
from sqlalchemy.orm import class_mapper

def extract_list_from_string(s: str) -> List[str]:
    """Extract a list of items from a comma-separated string."""
    return [item.strip() for item in s.split(',') if item.strip()]

def parse_duration(duration_str: str) -> timedelta:
    """Parse a duration string (e.g., '2 hours', '3 days') into a timedelta object."""
    match = re.match(r'(\d+)\s*(hour|day|week)s?', duration_str.lower())
    if not match:
        return timedelta()
    
    amount, unit = match.groups()
    amount = int(amount)
    
    if unit == 'hour':
        return timedelta(hours=amount)
    elif unit == 'day':
        return timedelta(days=amount)
    elif unit == 'week':
        return timedelta(weeks=amount)

def calculate_project_metrics(tasks: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Calculate various project metrics based on the tasks."""
    total_tasks = len(tasks)
    completed_tasks = sum(1 for task in tasks if task['status'] == 'Completed')
    total_duration = sum((task['actual_duration'] or task['estimated_duration']) for task in tasks)
    
    return {
        'total_tasks': total_tasks,
        'completed_tasks': completed_tasks,
        'completion_rate': completed_tasks / total_tasks if total_tasks > 0 else 0,
        'total_duration': total_duration,
        'average_task_duration': total_duration / total_tasks if total_tasks > 0 else 0
    }

def format_timedelta(td: timedelta) -> str:
    """Format a timedelta object into a human-readable string."""
    days, seconds = td.days, td.seconds
    hours = seconds // 3600
    minutes = (seconds % 3600) // 60
    
    parts = []
    if days > 0:
        parts.append(f"{days} day{'s' if days > 1 else ''}")
    if hours > 0:
        parts.append(f"{hours} hour{'s' if hours > 1 else ''}")
    if minutes > 0:
        parts.append(f"{minutes} minute{'s' if minutes > 1 else ''}")
    
    return ', '.join(parts) if parts else "0 minutes"

def sanitize_input(input_string: str) -> str:
    """Remove any potentially harmful characters from input strings."""
    return re.sub(r'[^\w\s-]', '', input_string).strip()

def generate_task_id(project_id: int, task_title: str) -> str:
    """Generate a unique task ID based on project ID and task title."""
    sanitized_title = sanitize_input(task_title)
    return f"{project_id}-{sanitized_title[:20]}-{datetime.now().strftime('%Y%m%d%H%M%S')}"

def calculate_task_priority_score(task: Dict[str, Any], project_context: Dict[str, Any]) -> float:
    """Calculate a priority score for a task based on various factors."""
    score = 0
    if task['priority'] == 'High':
        score += 3
    elif task['priority'] == 'Medium':
        score += 2
    elif task['priority'] == 'Low':
        score += 1
    
    return score

def model_to_dict(obj):
    return {c.key: getattr(obj, c.key)
            for c in class_mapper(obj.__class__).columns}