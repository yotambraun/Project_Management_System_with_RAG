import os
from langchain_groq import ChatGroq
from langchain.prompts import ChatPromptTemplate
from langchain.output_parsers import PydanticOutputParser
from pydantic import BaseModel, Field
from typing import List
import datetime
from dotenv import load_dotenv
from backend.ai_engine.rag.retriever import Retriever
from langchain.schema import HumanMessage, SystemMessage

load_dotenv()
class TaskOutput(BaseModel):
    title: str = Field(description="Title of the task")
    estimated_duration: float = Field(description="Estimated duration of the task in hours")
    required_skills: List[str] = Field(description="List of skills required for the task")
    priority: str = Field(description="Priority of the task (High, Medium, Low)")

class TaskAgent:
    def __init__(self, retriever: Retriever):
        self.llm = ChatGroq(groq_api_key=os.getenv("GROQ_API_KEY"),
        model="mixtral-8x7b-32768",
        temperature=0,
        max_tokens=None,
        timeout=None,
        max_retries=2,)
        self.parser = PydanticOutputParser(pydantic_object=TaskOutput)
        self.retriever = retriever
        
        self.task_creation_prompt = ChatPromptTemplate.from_template(
            "Create a task based on the following description: {description}. "
            "Consider these similar tasks: {similar_tasks}. "
            "Project context: {project_context}. "
            "{format_instructions}"
        )

    def create_task(self, description: str, project_id: int) -> dict:
        try:
            similar_tasks = self.retriever.get_similar_tasks(description, project_id)
            project_context = self.retriever.get_project_context(project_id)
            team_skills = self.retriever.get_team_skills(project_id)
        except Exception as e:
            print(f"Error retrieving data: {e}")
            similar_tasks = []
            project_context = {}
            team_skills = {}

        messages = [
            SystemMessage(content="You are a task creation assistant for a project management system."),
            HumanMessage(content=f"Create a task based on the following description: {description}. "
                                 f"Consider these similar tasks: {similar_tasks}. "
                                 f"Project context: {project_context}. "
                                 f"Available team skills: {team_skills}. "
                                 f"Provide a title, estimated duration, and required skills.")
        ]

        try:
            response = self.llm(messages)
            print(f"LLM Response: {response}")  # Debug print
            task_info = self.parser.parse(response.content)
            return {
                'title': task_info.title,
                'description': description,
                'estimated_duration': task_info.estimated_duration,
                'required_skills': task_info.required_skills,
                'created_at': datetime.datetime.now().isoformat(),
                'status': 'New',
                'project_id': project_id
            }
        except Exception as e:
            print(f"Error in create_task: {e}")
            return {
                'title': f"Task: {description[:50]}",
                'description': description,
                'estimated_duration': None,
                'required_skills': [],
                'created_at': datetime.datetime.now().isoformat(),
                'status': 'New',
                'project_id': project_id
            }