# from langchain_community.chat_models import ChatOpenAI
from langchain_groq import ChatGroq
from langchain.prompts import ChatPromptTemplate
from langchain.output_parsers import PydanticOutputParser
from pydantic import BaseModel, Field
from backend.ai_engine.rag.retriever import Retriever
from dotenv import load_dotenv
from langchain.schema import HumanMessage, SystemMessage
import os

load_dotenv()


class PriorityOutput(BaseModel):
    priority: str = Field(description="Priority level of the task (High, Medium, Low)")
    reasoning: str = Field(description="Reasoning behind the priority assignment")

class PriorityAgent:
    """PriorityAgent class to assign a priority to a task"""
    def __init__(self, retriever: Retriever, model_name: str = "gpt-3.5-turbo"):
        self.llm = ChatGroq(groq_api_key=os.getenv("GROQ_API_KEY"),
        model="mixtral-8x7b-32768",
        temperature=0,
        max_tokens=None,
        timeout=None,
        max_retries=2,)
        self.parser = PydanticOutputParser(pydantic_object=PriorityOutput)
        self.retriever = retriever
        
        self.priority_prompt = ChatPromptTemplate.from_template(
            "Assign a priority to the following task: {task_description}\n"
            "Consider the task's complexity, estimated duration, and required skills.\n"
            "Project context: {project_context}\n"
            "Similar tasks priorities: {similar_tasks_priorities}\n"
            "{format_instructions}"
        )

    def assign_priority(self, task: dict) -> dict:
        """Assign a priority to a task
        for example:
        task = {
            "title": "Design a new logo",
            "description": "Design a new logo for the company website",
            "estimated_duration": "2 days",
            "required_skills": ["Graphic Design", "Adobe Illustrator"],
            "project_id": 1
        }
        if the task is to design a new logo, the agent should assign a priority level (High, Medium, Low) and provide reasoning.
        if error occurs, return default priority and reasoning.
        """
        project_context = self.retriever.get_project_context(task['project_id'])
        similar_tasks_priorities = self.retriever.get_similar_tasks_priorities(task['description'], task['project_id'])
        team_skills = self.retriever.get_team_skills(task['project_id'])

        task_description = f"{task['title']}"
        if task.get('estimated_duration'):
            task_description += f" (Duration: {task['estimated_duration']})"
        if task.get('required_skills'):
            task_description += f" (Skills: {', '.join(task['required_skills'])})"

        messages = [
            SystemMessage(content="You are a task prioritization assistant for a project management system."),
            HumanMessage(content=f"Assign a priority to the following task: {task_description}\n"
                                 f"Consider the task's complexity, estimated duration, and required skills.\n"
                                 f"Project context: {project_context}\n"
                                 f"Similar tasks priorities: {similar_tasks_priorities}\n"
                                 f"Team skills: {team_skills}\n"
                                 f"Provide the priority (High, Medium, or Low) and reasoning.")
        ]
        
        try:
            response = self.llm(messages)
            priority_info = self.parser.parse(response.content)
            return priority_info.dict()
        except Exception as e:
            print(f"Error in assign_priority: {e}")
            return {"priority": "Medium", "reasoning": "Default priority assigned due to error."}