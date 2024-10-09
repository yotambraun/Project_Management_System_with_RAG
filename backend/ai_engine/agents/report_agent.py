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
import json
from datetime import datetime

load_dotenv()

class ReportOutput(BaseModel):
    summary: str = Field(description="Summary of the project status, including tasks and assigned team members")
    key_metrics: Dict[str, float] = Field(description="Key metrics of the project")
    risks: List[str] = Field(description="Identified risks in the project")
    recommendations: List[str] = Field(description="List of recommendations for project improvement")

class ReportAgent:
    def __init__(self, retriever: Retriever, model_name: str = "gpt-3.5-turbo"):
        self.llm = ChatGroq(
            groq_api_key=os.getenv("GROQ_API_KEY"),
            model="mixtral-8x7b-32768",
            temperature=0,
            max_tokens=None,
            timeout=None,
            max_retries=2,
        )
        self.parser = PydanticOutputParser(pydantic_object=ReportOutput)
        self.retriever = retriever
        self.report_prompt = ChatPromptTemplate.from_template(
            "Generate a project report based on the following information:\n"
            "Tasks: {tasks}\n"
            "Project context: {project_context}\n"
            "Similar past projects: {similar_projects}\n"
            "Please include in the summary section a list of tasks with their assigned team members (if available).\n"
            "{format_instructions}"
        )

    def generate_report(self, tasks: List[Dict[str, Any]]) -> Dict[str, Any]:
        if not tasks:
            return {
                "summary": "No tasks available for report generation.",
                "key_metrics": {},
                "risks": ["No tasks to analyze risks."],
                "recommendations": ["Start by adding tasks to the project."]
            }

        project_id = tasks[0].get('project_id')
        project_context = self.retriever.get_project_context(project_id) if project_id else {}
        similar_projects = self.retriever.get_similar_projects(project_id) if project_id else []

        # Convert datetime objects to strings
        def json_serial(obj):
            if isinstance(obj, datetime):
                return obj.isoformat()
            raise TypeError(f"Type {type(obj)} not serializable")

        # Enhance task information with team members if available in project context
        team_members = project_context.get('team_members', [])
        for task in tasks:
            task['assigned_to'] = team_members[task['id'] % len(team_members)] if team_members else "Unassigned"

        system_message = SystemMessage(content="You are an AI assistant tasked with generating project reports.")
        human_message = HumanMessage(content=self.report_prompt.format(
            tasks=json.dumps(tasks, default=json_serial, indent=2),
            project_context=json.dumps(project_context, default=json_serial, indent=2),
            similar_projects=json.dumps(similar_projects, default=json_serial, indent=2),
            format_instructions=self.parser.get_format_instructions()
        ))

        messages = [system_message, human_message]

        try:
            response = self.llm.invoke(messages)
            report_info = self.parser.parse(response.content)
            return report_info.dict()
        except Exception as e:
            print(f"Error in generate_report: {e}")
            return {
                "summary": "An error occurred while generating the report.",
                "key_metrics": {},
                "risks": ["Unable to analyze risks due to an error."],
                "recommendations": ["Please try again or contact support if the issue persists."]
            }