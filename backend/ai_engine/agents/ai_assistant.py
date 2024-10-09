from langchain_groq import ChatGroq
from langchain.prompts import ChatPromptTemplate
from backend.ai_engine.rag.retriever import Retriever
from dotenv import load_dotenv
from langchain.schema import HumanMessage, SystemMessage
import os
import json

load_dotenv()

class AIAssistant:
    def __init__(self, retriever: Retriever):
        self.llm = ChatGroq(
            groq_api_key=os.getenv("GROQ_API_KEY"),
            model_name="mixtral-8x7b-32768",
            temperature=0.5,
            max_tokens=1024,
        )
        self.retriever = retriever

    def answer_question(self, project_id: int, question: str) -> str:
        project_context = self.retriever.get_project_context(project_id)
        related_info = self.retriever.get_related_information(question)
        
        formatted_project_context = json.dumps(project_context, indent=2)
        formatted_related_info = json.dumps(related_info, indent=2)
        
        system_message = SystemMessage(content="You are an AI assistant for a project management system. Answer the following question based on the provided context.")
        human_message = HumanMessage(content=f"""
            Project context: {formatted_project_context}
            Related information: {formatted_related_info}
            Question: {question}
            Answer:
            """)
                
        messages = [system_message, human_message]
        
        print(f"Sending to AI:\n{human_message.content}")  # Debug print
        
        try:
            response = self.llm.invoke(messages)
            print(f"AI response:\n{response.content}")  # Debug print
            return response.content
        except Exception as e:
            print(f"Error in AI chat: {str(e)}")
            return f"I'm sorry, but I encountered an error while trying to answer your question. Error: {str(e)}"