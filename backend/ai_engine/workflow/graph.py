from langgraph.graph import StateGraph, END
from typing import Dict, Any
from backend.ai_engine.agents.task_agent import TaskAgent
from backend.ai_engine.agents.priority_agent import PriorityAgent
from backend.ai_engine.agents.suggestion_agent import SuggestionAgent
from backend.ai_engine.agents.report_agent import ReportAgent
from backend.ai_engine.agents.collaboration_agent import CollaborationAgent
from backend.ai_engine.rag.retriever import Retriever
from backend.database.database import SessionLocal

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def create_workflow():
    """this function creates a state graph workflow that defines the sequence of steps to be executed in the AI engine. 
    The workflow consists of several nodes, each representing a specific task or action to be performed. 
    The workflow starts with the "create_task" node, where a new task is created based on the input description and project ID. 
    The workflow then moves to the "assign_priority" node, where the priority of the task is assigned using the PriorityAgent. 
    Next, the workflow moves to the "generate_suggestions" node, where suggestions are generated for the task using the SuggestionAgent. 
    The workflow then moves to the "suggest_collaboration" node, where collaboration suggestions are generated using the CollaborationAgent. 
    Finally, the workflow moves to the "generate_report" node, where a report is generated based on the tasks created. 
    The workflow is compiled and returned as a callable function that can be executed to run the AI engine. 
    If any errors occur during the creation of the workflow, an error message is printed, and None is returned. 
    The workflow function is then called to create the workflow instance, which is stored in the "workflow" variable. 
    The workflow instance is used to execute the AI engine and perform the task management operations."""

    try:
        workflow = StateGraph(Dict)

        db = next(get_db())
        retriever = Retriever(db)
        task_agent = TaskAgent(retriever)
        priority_agent = PriorityAgent(retriever)
        suggestion_agent = SuggestionAgent(retriever)
        report_agent = ReportAgent(retriever)
        collaboration_agent = CollaborationAgent(retriever)

        workflow.add_node("create_task", lambda state: create_task_node(state, task_agent))
        workflow.add_node("assign_priority", lambda state: assign_priority_node(state, priority_agent))
        workflow.add_node("generate_suggestions", lambda state: generate_suggestions_node(state, suggestion_agent))
        workflow.add_node("suggest_collaboration", lambda state: suggest_collaboration_node(state, collaboration_agent))
        workflow.add_node("generate_report", lambda state: generate_report_node(state, report_agent))

        workflow.add_edge("create_task", "assign_priority")
        workflow.add_edge("assign_priority", "generate_suggestions")
        workflow.add_edge("generate_suggestions", "suggest_collaboration")
        
        workflow.add_conditional_edges(
            "suggest_collaboration",
            lambda state: "generate_report" if state.get("generate_report", False) else END,
            {
                "generate_report": "generate_report",
                END: END
            }
        )
        workflow.add_edge("generate_report", END)

        workflow.set_entry_point("create_task")

        return workflow.compile()
    except Exception as e:
        print(f"Error creating workflow: {e}")
        return None
workflow = create_workflow()

def create_task_node(state: Dict[str, Any], task_agent: TaskAgent) -> Dict[str, Any]:
    new_task = task_agent.create_task(state['input_description'], state['project_id'])
    new_task['project_id'] = state['project_id']  # Ensure project_id is included
    state['tasks'].append(new_task)
    return state

def assign_priority_node(state: Dict[str, Any], priority_agent: PriorityAgent) -> Dict[str, Any]:
    for task in state['tasks']:
        if task['status'] == 'New':
            priority_info = priority_agent.assign_priority(task)
            task['priority'] = priority_info['priority']
            task['priority_reasoning'] = priority_info['reasoning']
    return state

def generate_suggestions_node(state: Dict[str, Any], suggestion_agent: SuggestionAgent) -> Dict[str, Any]:
    for task in state['tasks']:
        if task['status'] == 'New':
            task['suggestions'] = suggestion_agent.generate_suggestions(task)
    return state

def suggest_collaboration_node(state: Dict[str, Any], collaboration_agent: CollaborationAgent) -> Dict[str, Any]:
    for task in state['tasks']:
        if task['status'] == 'New':
            task['collaboration'] = collaboration_agent.suggest_collaboration(task)
    return state

def generate_report_node(state: Dict[str, Any], report_agent: ReportAgent) -> Dict[str, Any]:
    state['report'] = report_agent.generate_report(state['tasks'])
    return state

