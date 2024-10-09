from sqlalchemy.orm import Session
from . import models, schemas
from datetime import datetime
from fastapi import HTTPException
import json


def create_user(db: Session, user: schemas.UserCreate):
    fake_hashed_password = user.password + "notreallyhashed"
    db_user = models.User(username=user.username, email=user.email, hashed_password=fake_hashed_password)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

def get_user(db: Session, user_id: int):
    return db.query(models.User).filter(models.User.id == user_id).first()

def get_user_by_email(db: Session, email: str):
    return db.query(models.User).filter(models.User.email == email).first()

def get_users(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.User).offset(skip).limit(limit).all()

def create_project(db: Session, project: schemas.ProjectCreate, user_id: int):
    db_project = models.Project(**project.dict(), owner_id=user_id)
    db.add(db_project)
    db.commit()
    db.refresh(db_project)
    return db_project

def get_project(db: Session, project_id: int):
    return db.query(models.Project).filter(models.Project.id == project_id).first()

def get_projects(db: Session, skip: int = 0, limit: int = 100):
    projects = db.query(models.Project).offset(skip).limit(limit).all()
    return [schemas.ProjectOut(
        id=project.id,
        name=project.name,
        description=project.description,
        start_date=project.start_date,
        end_date=project.end_date,
        status=project.status,
        created_at=project.created_at,
        updated_at=project.updated_at,
        tasks=[schemas.Task.from_orm(task) for task in project.tasks],
        team_members=[schemas.TeamMember(
            id=tm.id,
            name=tm.name,
            email=tm.email,
            role=tm.role,
            skills=json.loads(tm.skills) if tm.skills else None,
            assigned_tasks=[schemas.Task.from_orm(task) for task in tm.assigned_tasks]
        ) for tm in project.team_members]
    ) for project in projects]

def create_task(db: Session, task: schemas.TaskCreate, project_id: int):
    task_data = task.dict()
    if task_data.get('required_skills'):
        task_data['required_skills'] = json.dumps(task_data['required_skills'])
    db_task = models.Task(**task_data, project_id=project_id, created_at=datetime.utcnow())
    db.add(db_task)
    db.commit()
    db.refresh(db_task)
    return db_task

def get_tasks(db: Session, project_id: int, skip: int = 0, limit: int = 100):
    return db.query(models.Task).filter(models.Task.project_id == project_id).offset(skip).limit(limit).all()

def create_team_member(db: Session, team_member: schemas.TeamMemberCreate):
    skills_json = json.dumps(team_member.skills) if team_member.skills else None
    db_team_member = models.TeamMember(
        name=team_member.name,
        email=team_member.email,
        role=team_member.role,
        skills=skills_json
    )
    db.add(db_team_member)
    db.commit()
    db.refresh(db_team_member)
    
    # Convert the database model to the Pydantic schema
    return schemas.TeamMember(
        id=db_team_member.id,
        name=db_team_member.name,
        email=db_team_member.email,
        role=db_team_member.role,
        skills=json.loads(db_team_member.skills) if db_team_member.skills else None,
        assigned_tasks=[]  # New team members won't have assigned tasks yet
    )


def get_team_members(db: Session, skip: int = 0, limit: int = 100):
    db_team_members = db.query(models.TeamMember).offset(skip).limit(limit).all()
    return [
        schemas.TeamMember(
            id=tm.id,
            name=tm.name,
            email=tm.email,
            role=tm.role,
            skills=json.loads(tm.skills) if tm.skills else None,
            assigned_tasks=[schemas.Task.from_orm(task) for task in tm.assigned_tasks]
        )
        for tm in db_team_members
    ]

def update_task(db: Session, task_id: int, task_update: dict):
    db_task = db.query(models.Task).filter(models.Task.id == task_id).first()
    if db_task:
        for key, value in task_update.items():
            setattr(db_task, key, value)
        db.commit()
        db.refresh(db_task)
    return db_task

def get_task(db: Session, task_id: int):
    return db.query(models.Task).filter(models.Task.id == task_id).first()

def assign_team_member_to_project(db: Session, project_id: int, team_member_id: int):
    project = db.query(models.Project).filter(models.Project.id == project_id).first()
    team_member = db.query(models.TeamMember).filter(models.TeamMember.id == team_member_id).first()
    
    if not project or not team_member:
        raise HTTPException(status_code=404, detail="Project or Team Member not found")
    
    project.team_members.append(team_member)
    db.commit()
    db.refresh(project)
    
    # Convert the project to a ProjectOut schema
    return schemas.ProjectOut(
        id=project.id,
        name=project.name,
        description=project.description,
        start_date=project.start_date,
        end_date=project.end_date,
        status=project.status,
        created_at=project.created_at,
        updated_at=project.updated_at,
        tasks=[schemas.Task.from_orm(task) for task in project.tasks],
        team_members=[schemas.TeamMember(
            id=tm.id,
            name=tm.name,
            email=tm.email,
            role=tm.role,
            skills=json.loads(tm.skills) if tm.skills else None,
            assigned_tasks=[schemas.Task.from_orm(task) for task in tm.assigned_tasks]
        ) for tm in project.team_members]
    )