from typing import List, Dict, Any
from sqlalchemy.orm import Session
from backend.ai_engine.rag.vector_store import vector_store
from backend.database import crud
from backend.database import models
import json


class Retriever:
    def __init__(self, db: Session):
        self.db = db

    def get_similar_tasks(self, description: str, project_id: int, k: int = 3) -> List[Dict[str, Any]]:
        query = f"Project ID: {project_id} | Task: {description}"
        similar_docs = vector_store.similarity_search(query, k=k)
        return [{"title": doc.metadata["title"], "description": doc.page_content} for doc in similar_docs]

    def get_project_context(self, project_id: int) -> Dict[str, Any]:
        project = crud.get_project(self.db, project_id)
        if not project:
            print(f"No project found for id: {project_id}")
            return {}
        context = {
            "name": project.name,
            "description": project.description,
            "start_date": str(project.start_date),
            "end_date": str(project.end_date),
            "status": project.status,
            "team_members": [member.name for member in project.team_members]
        }
        print(f"Project context: {context}")
        return context

    
    def get_project_team_members(self, project_id: int):
        return self.db.query(models.TeamMember).join(models.Project.team_members).filter(models.Project.id == project_id).all()

    def get_similar_tasks_priorities(self, description: str, project_id: int, k: int = 3) -> List[Dict[str, Any]]:
        query = f"Project ID: {project_id} | Task: {description}"
        similar_docs = vector_store.similarity_search(query, k=k)
        return [{"title": doc.metadata["title"], "priority": doc.metadata.get("priority", "Unknown")} for doc in similar_docs]

    def get_available_team_members(self, project_id: int) -> List[Dict[str, Any]]:
        team_members = crud.get_project_team_members(self.db, project_id)
        return [{"name": tm.name, "skills": tm.skills, "role": tm.role} for tm in team_members]

    def get_similar_collaborations(self, task_description: str, project_id: int, k: int = 3) -> List[Dict[str, Any]]:
        query = f"Project ID: {project_id} | Collaboration for: {task_description}"
        similar_docs = vector_store.similarity_search(query, k=k)
        return [{"task": doc.metadata["task"], "collaboration": doc.page_content} for doc in similar_docs]

    def get_project_tasks(self, project_id: int) -> List[Dict[str, Any]]:
        tasks = crud.get_project_tasks(self.db, project_id)
        return [{"title": task.title, "status": task.status, "priority": task.priority} for task in tasks]

    def get_team_performance(self, project_id: int) -> Dict[str, Any]:
        tasks = crud.get_project_tasks(self.db, project_id)
        completed_tasks = sum(1 for task in tasks if task.status == "Completed")
        total_tasks = len(tasks)
        return {
            "task_completion_rate": completed_tasks / total_tasks if total_tasks > 0 else 0,
            "total_tasks": total_tasks,
            "completed_tasks": completed_tasks
        }

    def get_similar_projects(self, project_id: int, k: int = 3) -> List[Dict[str, Any]]:
        project = crud.get_project(self.db, project_id)
        if not project:
            return []
        
        query = f"Project: {project.name} | Description: {project.description}"
        similar_docs = vector_store.similarity_search(query, k=k)
        
        return [
            {
                "name": doc.metadata.get("name", "Unnamed Project"),
                "description": doc.page_content
            } 
            for doc in similar_docs
        ]

    def get_similar_completed_tasks(self, task_description: str, project_id: int, k: int = 3) -> List[Dict[str, Any]]:
        query = f"Project ID: {project_id} | Completed Task: {task_description}"
        similar_docs = vector_store.similarity_search(query, k=k)
        return [{"title": doc.metadata["title"], "description": doc.page_content} for doc in similar_docs]

    def get_team_skills(self, project_id: int) -> Dict[str, List[str]]:
        team_members = self.get_project_team_members(project_id)
        return {tm.name: json.loads(tm.skills) if tm.skills else [] for tm in team_members}

    def get_available_team_members(self, project_id: int) -> List[Dict[str, Any]]:
        team_members = crud.get_project_team_members(self.db, project_id)
        return [{"name": tm.name, "skills": tm.skills.split(',')} for tm in team_members]

    def get_related_information(self, question: str, k: int = 3) -> List[Dict[str, Any]]:
        similar_docs = vector_store.similarity_search(question, k=k)
        related_info = [{"title": doc.metadata.get("title", "Unknown"), "content": doc.page_content} for doc in similar_docs]
        print(f"Related information: {related_info}")
        return related_info
