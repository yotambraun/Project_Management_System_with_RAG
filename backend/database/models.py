from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Table, Date, Boolean, Float
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime

Base = declarative_base()
project_team_members = Table('project_team_members', Base.metadata,
    Column('project_id', Integer, ForeignKey('projects.id')),
    Column('team_member_id', Integer, ForeignKey('team_members.id'))
)


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    is_active = Column(Boolean, default=True)

    projects = relationship("Project", back_populates="owner")

class Project(Base):
    __tablename__ = 'projects'

    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    description = Column(String)
    start_date = Column(Date)
    end_date = Column(Date)
    status = Column(String)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime)

    owner_id = Column(Integer, ForeignKey("users.id"))
    owner = relationship("User", back_populates="projects")
    tasks = relationship("Task", back_populates="project")
    team_members = relationship("TeamMember", secondary=project_team_members, back_populates="projects")

class Task(Base):
    __tablename__ = 'tasks'

    id = Column(Integer, primary_key=True)
    title = Column(String, nullable=False)
    description = Column(String)
    status = Column(String, nullable=False)
    priority = Column(String)
    priority_reasoning = Column(String)
    estimated_duration = Column(Float)
    actual_duration = Column(Float)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime)
    due_date = Column(Date)
    required_skills = Column(String)  # Store as JSON string

    project_id = Column(Integer, ForeignKey('projects.id'))
    project = relationship("Project", back_populates="tasks")
    assigned_to_id = Column(Integer, ForeignKey('team_members.id'))
    assigned_to = relationship("TeamMember", back_populates="assigned_tasks")

class TeamMember(Base):
    __tablename__ = 'team_members'

    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    email = Column(String, unique=True)
    role = Column(String)
    skills = Column(String)

    assigned_tasks = relationship("Task", back_populates="assigned_to")
    projects = relationship("Project", secondary=project_team_members, back_populates="team_members")