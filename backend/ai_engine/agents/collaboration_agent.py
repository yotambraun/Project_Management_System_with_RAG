# from langchain_community.chat_models import ChatOpenAI
from langchain_groq import ChatGroq
from langchain.prompts import ChatPromptTemplate
from langchain.output_parsers import PydanticOutputParser
from pydantic import BaseModel, Field
from typing import List, Dict , Any
from backend.ai_engine.rag.retriever import Retriever
from dotenv import load_dotenv
import os

load_dotenv()

class TeamFormation(BaseModel):
    member_name: str = Field(description="Name of the team member")
    role: str = Field(description="Assigned role for the task")

class CollaborationOutput(BaseModel):
    team_formation: List[TeamFormation] = Field(description="Suggested team formation for the task")
    communication_plan: str = Field(description="Suggested communication plan for the team")

class CollaborationAgent:
    """CollaborationAgent class to suggest team formation and communication plan for a task"""
    def __init__(self, retriever: Retriever,model_name: str = "gpt-3.5-turbo"):
        self.llm = ChatGroq(groq_api_key=os.getenv("GROQ_API_KEY"),
        model="mixtral-8x7b-32768",
        temperature=0,
        max_tokens=None,
        timeout=None,
        max_retries=2,)
        self.parser = PydanticOutputParser(pydantic_object=CollaborationOutput)
        self.retriever = retriever
        
        self.collaboration_prompt = ChatPromptTemplate.from_template(
            "Suggest a team formation and communication plan for the following task:\n"
            "Task: {task_description}\n"
            "Available team members: {available_team_members}\n"
            "Project context: {project_context}\n"
            "Similar past collaborations: {similar_collaborations}\n"
            "{format_instructions}"
        )

    def suggest_collaboration(self, task: Dict[str, Any], project_id: int) -> Dict[str, Any]:
        """Suggest team formation and communication plan for a task"""
        available_team_members = self.retriever.get_available_team_members(project_id)
        project_context = self.retriever.get_project_context(project_id)
        similar_collaborations = self.retriever.get_similar_collaborations(task['description'], project_id)

        prompt = self.collaboration_prompt.format(
            task_description=f"{task['title']} (Duration: {task['estimated_duration']}, Skills: {', '.join(task['required_skills'])})",
            available_team_members=available_team_members,
            project_context=project_context,
            similar_collaborations=similar_collaborations,
            format_instructions=self.parser.get_format_instructions()
        )
        response = self.llm(prompt)
        collaboration_info = self.parser.parse(response.content)
        
        return collaboration_info.dict()