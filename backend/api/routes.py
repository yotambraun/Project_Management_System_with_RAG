from fastapi import APIRouter, Depends, HTTPException, Response
from sqlalchemy.orm import Session
from typing import List
import logging
from backend.database import crud, schemas
from backend.api.dependencies import get_db
from backend.ai_engine.workflow.graph import workflow
from backend.ai_engine.agents.ai_assistant import AIAssistant
from backend.ai_engine.rag.retriever import Retriever
from backend.ai_engine.agents.priority_agent import PriorityAgent
from backend.ai_engine.agents.suggestion_agent import SuggestionAgent
from backend.ai_engine.agents.report_agent import ReportAgent
from backend.ai_engine.utils.helpers import model_to_dict
from pydantic import BaseModel
import json
from io import BytesIO
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet

router = APIRouter()
logging.basicConfig(level=logging.INFO)


@router.post("/users/", response_model=schemas.User)
def create_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    db_user = crud.get_user_by_email(db, email=user.email)
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    return crud.create_user(db=db, user=user)

@router.get("/users/", response_model=List[schemas.User])
def read_users(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    users = crud.get_users(db, skip=skip, limit=limit)
    return users

@router.post("/projects/", response_model=schemas.Project)
def create_project(project: schemas.ProjectCreate, db: Session = Depends(get_db)):
    return crud.create_project(db=db, project=project, user_id=1)

@router.get("/projects/", response_model=List[schemas.ProjectOut])
def read_projects(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    projects = crud.get_projects(db, skip=skip, limit=limit)
    return projects

@router.get("/projects/{project_id}", response_model=schemas.Project)
def read_project(project_id: int, db: Session = Depends(get_db)):
    db_project = crud.get_project(db, project_id=project_id)
    if db_project is None:
        raise HTTPException(status_code=404, detail="Project not found")
    return db_project

@router.post("/projects/{project_id}/tasks/", response_model=schemas.Task)
def create_task(project_id: int, task: schemas.TaskCreate, db: Session = Depends(get_db)):
    project = crud.get_project(db, project_id=project_id)
    if project is None:
        raise HTTPException(status_code=404, detail="Project not found")
    
    logging.info(f"Creating task for project {project_id}: {task}")
    
    try:
        db_task = crud.create_task(db=db, task=task, project_id=project_id)
        return db_task
    except Exception as e:
        logging.error(f"Error creating task: {str(e)}")
        raise HTTPException(status_code=500, detail=f"An error occurred while creating the task: {str(e)}")

@router.get("/projects/{project_id}/tasks/", response_model=List[schemas.Task])
def read_tasks(project_id: int, skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    tasks = crud.get_tasks(db, project_id=project_id, skip=skip, limit=limit)
    return tasks

@router.post("/team-members/", response_model=schemas.TeamMember)
def create_team_member(team_member: schemas.TeamMemberCreate, db: Session = Depends(get_db)):
    return crud.create_team_member(db=db, team_member=team_member)

@router.get("/team-members/", response_model=List[schemas.TeamMember])
def read_team_members(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    team_members = crud.get_team_members(db, skip=skip, limit=limit)
    return team_members

class AIQuestion(BaseModel):
    question: str

@router.post("/projects/{project_id}/ai-chat/")
def ai_chat(project_id: int, ai_question: AIQuestion, db: Session = Depends(get_db)):
    print(f"Received question for project {project_id}: {ai_question.question}")
    project = crud.get_project(db, project_id=project_id)
    if project is None:
        raise HTTPException(status_code=404, detail="Project not found")
    
    retriever = Retriever(db)
    ai_assistant = AIAssistant(retriever)
    
    try:
        answer = ai_assistant.answer_question(project_id, ai_question.question)
        print(f"AI response: {answer}")
        return {"answer": answer}
    except Exception as e:
        print(f"Error in AI chat: {str(e)}")
        raise HTTPException(status_code=500, detail=f"An error occurred: {str(e)}")

@router.post("/projects/{project_id}/tasks/{task_id}/prioritize/", response_model=schemas.Task)
def prioritize_task(project_id: int, task_id: int, db: Session = Depends(get_db)):
    task = crud.get_task(db, task_id=task_id)
    if task is None or task.project_id != project_id:
        raise HTTPException(status_code=404, detail="Task not found or does not belong to the specified project")
    
    retriever = Retriever(db)
    priority_agent = PriorityAgent(retriever)
    
    # Convert SQLAlchemy model to dictionary
    task_dict = {c.name: getattr(task, c.name) for c in task.__table__.columns}
    
    # Ensure the task dictionary has all required fields
    task_dict['project_id'] = project_id
    if 'required_skills' in task_dict and task_dict['required_skills']:
        task_dict['required_skills'] = task_dict['required_skills'].split(',')
    else:
        task_dict['required_skills'] = []

    try:
        priority_info = priority_agent.assign_priority(task_dict)
        updated_task = crud.update_task(db, task_id=task_id, task_update={
            'priority': priority_info['priority'],
            'priority_reasoning': priority_info['reasoning']
        })
        return updated_task
    except Exception as e:
        print(f"Error in prioritize_task: {e}")
        raise HTTPException(status_code=500, detail="An error occurred while prioritizing the task")

@router.post("/projects/{project_id}/tasks/{task_id}/suggest/")
def suggest_for_task(project_id: int, task_id: int, db: Session = Depends(get_db)):
    task = crud.get_task(db, task_id=task_id)
    if task is None or task.project_id != project_id:
        raise HTTPException(status_code=404, detail="Task not found or does not belong to the specified project")
    
    retriever = Retriever(db)
    suggestion_agent = SuggestionAgent(retriever)
    
    task_dict = model_to_dict(task)
    suggestions = suggestion_agent.generate_suggestions(task_dict, project_id)
    return suggestions

@router.post("/projects/{project_id}/report/")
def generate_project_report(project_id: int, db: Session = Depends(get_db), pdf: bool = False):
    project = crud.get_project(db, project_id=project_id)
    if project is None:
        raise HTTPException(status_code=404, detail="Project not found")
    
    tasks = crud.get_tasks(db, project_id=project_id)
    
    retriever = Retriever(db)
    report_agent = ReportAgent(retriever)
    
    # Convert SQLAlchemy model instances to dictionaries
    task_dicts = []
    for task in tasks:
        task_dict = {c.name: getattr(task, c.name) for c in task.__table__.columns}
        # Handle the 'required_skills' field separately
        if task.required_skills:
            task_dict['required_skills'] = json.loads(task.required_skills)
        task_dicts.append(task_dict)
    
    logging.info(f"Generating report for project {project_id} with {len(task_dicts)} tasks")
    
    try:
        report = report_agent.generate_report(task_dicts)
        logging.info("Report generated successfully")
        
        if pdf:
            # Generate PDF
            buffer = BytesIO()
            doc = SimpleDocTemplate(buffer, pagesize=letter)
            styles = getSampleStyleSheet()
            story = []

            # Add content to the PDF
            story.append(Paragraph("Project Report", styles['Title']))
            story.append(Spacer(1, 12))
            story.append(Paragraph("Summary", styles['Heading2']))
            story.append(Paragraph(report['summary'], styles['Normal']))
            story.append(Spacer(1, 12))
            story.append(Paragraph("Key Metrics", styles['Heading2']))
            for key, value in report['key_metrics'].items():
                story.append(Paragraph(f"{key}: {value}", styles['Normal']))
            story.append(Spacer(1, 12))
            story.append(Paragraph("Risks", styles['Heading2']))
            for risk in report['risks']:
                story.append(Paragraph(f"• {risk}", styles['Normal']))
            story.append(Spacer(1, 12))
            story.append(Paragraph("Recommendations", styles['Heading2']))
            for recommendation in report['recommendations']:
                story.append(Paragraph(f"• {recommendation}", styles['Normal']))

            doc.build(story)
            buffer.seek(0)
            return Response(content=buffer.getvalue(), media_type="application/pdf", headers={"Content-Disposition": "attachment; filename=project_report.pdf"})
        else:
            return report
    except Exception as e:
        logging.error(f"Error generating report: {str(e)}")
        raise HTTPException(status_code=500, detail=f"An error occurred while generating the report: {str(e)}")

@router.post("/projects/{project_id}/team-members/{team_member_id}", response_model=schemas.ProjectOut)
def assign_team_member_to_project(
    project_id: int, 
    team_member_id: int, 
    db: Session = Depends(get_db)
):
    return crud.assign_team_member_to_project(db, project_id, team_member_id)