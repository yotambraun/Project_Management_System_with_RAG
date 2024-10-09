from pydantic import BaseModel, Field, validator
from typing import List, Optional
from datetime import datetime, date
import json


class TaskBase(BaseModel):
    title: str
    description: Optional[str] = None
    status: Optional[str] = "New"
    priority: Optional[str] = None
    estimated_duration: Optional[float] = None
    due_date: Optional[date] = None
    required_skills: Optional[List[str]] = None

class TaskCreate(TaskBase):
    pass

class Task(TaskBase):
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None
    project_id: int
    assigned_to_id: Optional[int] = None
    priority: Optional[str] = None
    priority_reasoning: Optional[str] = None

    @validator('required_skills', pre=True)
    def parse_required_skills(cls, v):
        if isinstance(v, str):
            return json.loads(v)
        return v

    class Config:
        from_attributes = True
        
class TeamMemberBase(BaseModel):
    name: str
    email: str
    role: Optional[str] = None
    skills: Optional[List[str]] = None

class TeamMemberCreate(TeamMemberBase):
    pass

class TeamMemberInDB(TeamMemberBase):
    id: int
    skills: Optional[str] = None  # This will be the JSON string stored in the database

    class Config:
        from_attributes = True

class ProjectBase(BaseModel):
    name: str
    description: Optional[str] = None
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    status: Optional[str] = None

class ProjectCreate(ProjectBase):
    pass

class TeamMemberBase(BaseModel):
    id: int
    name: str
    email: str
    role: Optional[str] = None
    skills: Optional[List[str]] = None

class TeamMember(TeamMemberBase):
    id: int
    assigned_tasks: List[Task] = []

    class Config:
        from_attributes = True

class ProjectOut(ProjectBase):
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None
    tasks: List[Task] = []
    team_members: List[TeamMember] = []

    class Config:
        from_attributes = True

class Project(ProjectBase):
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None
    tasks: List[Task] = []
    team_members: List[TeamMemberBase] = []

    class Config:
        from_attributes = True

class UserBase(BaseModel):
    username: str
    email: str

class UserCreate(UserBase):
    password: str

class User(UserBase):
    id: int
    is_active: bool
    projects: List[Project] = []

    class Config:
        from_attributes = True