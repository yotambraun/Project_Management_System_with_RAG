# from langchain_community.chat_models import ChatOpenAI
from langchain_groq import ChatGroq
from langchain.prompts import ChatPromptTemplate
from langchain.output_parsers import PydanticOutputParser
from langchain.schema import HumanMessage, SystemMessage
from pydantic import BaseModel, Field
from typing import List, Dict, Any
from backend.ai_engine.rag.retriever import Retriever
from dotenv import load_dotenv
import os
import re


load_dotenv()

class SuggestionOutput(BaseModel):
    suggestions: List[str] = Field(description="List of suggestions for completing the task")
    resources: List[str] = Field(description="List of recommended resources for the task")

class SuggestionAgent:
    def __init__(self, retriever: Retriever,model_name: str = "gpt-3.5-turbo"):
        self.llm = ChatGroq(groq_api_key=os.getenv("GROQ_API_KEY"),
        model="mixtral-8x7b-32768",
        temperature=0,
        max_tokens=None,
        timeout=None,
        max_retries=2,)
        self.parser = PydanticOutputParser(pydantic_object=SuggestionOutput)
        self.retriever = retriever
        
        self.suggestion_prompt = ChatPromptTemplate.from_template(
            "Provide suggestions and resources for completing the following task:\n"
            "Task: {task_description}\n"
            "Project context: {project_context}\n"
            "Similar completed tasks: {similar_tasks}\n"
            "Team member skills: {team_skills}\n"
            "{format_instructions}"
        )

    def generate_suggestions(self, task: Dict[str, Any], project_id: int) -> Dict[str, Any]:
        project_context = self.retriever.get_project_context(project_id)
        similar_tasks = self.retriever.get_similar_completed_tasks(task['description'], project_id)
        team_skills = self.retriever.get_team_skills(project_id)

        task_description = f"{task['title']} (Duration: {task['estimated_duration']}, Skills: {', '.join(task['required_skills'])})"
        system_message = SystemMessage(content="You are a project management AI assistant. Provide suggestions and resources for completing the given task.")
        human_message = HumanMessage(content=f"""
        Task: {task_description}
        Project context: {project_context}
        Similar completed tasks: {similar_tasks}
        Team member skills: {team_skills}

        Please provide suggestions for completing this task and recommend relevant resources.
        """)

        messages = [system_message, human_message]

        response = self.llm.invoke(messages)
        
        # Parse the response content manually
        content = response.content
        suggestions = re.findall(r'\d+\.\s*\*\*(.*?)\*\*:', content, re.DOTALL)
        resources = re.findall(r'\d+\.\s*\*\*(.*?)\*\*:', content.split("Recommended resources:")[1], re.DOTALL) if "Recommended resources:" in content else []

        suggestion_info = {
            "suggestions": suggestions,
            "resources": resources
        }
        
        return suggestion_info