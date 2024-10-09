from typing import Dict, Any, List
from pydantic import BaseModel, Field


class Task(BaseModel):
    title: str
    description: str
    status: str
    priority: str = None
    estimated_duration: float
    actual_duration: float = None
    required_skills: List[str]
    suggestions: Dict[str, Any] = None
    collaboration: Dict[str, Any] = None

class WorkflowState(BaseModel):
    project_id: int
    input_description: str
    tasks: List[Task] = Field(default_factory=list)
    generate_report: bool = False
    report: Dict[str, Any] = None

class StateManager:
    @staticmethod
    def initialize_state(project_id: int, input_description: str) -> WorkflowState:
        return WorkflowState(
            project_id=project_id,
            input_description=input_description
        )

    @staticmethod
    def update_state(state: WorkflowState, updates: Dict[str, Any]) -> WorkflowState:
        for key, value in updates.items():
            if hasattr(state, key):
                setattr(state, key, value)
        return state

    @staticmethod
    def add_task(state: WorkflowState, task: Dict[str, Any]) -> WorkflowState:
        state.tasks.append(Task(**task))
        return state

    @staticmethod
    def update_task(state: WorkflowState, task_index: int, updates: Dict[str, Any]) -> WorkflowState:
        if 0 <= task_index < len(state.tasks):
            task = state.tasks[task_index]
            for key, value in updates.items():
                if hasattr(task, key):
                    setattr(task, key, value)
        return state

    @staticmethod
    def set_generate_report(state: WorkflowState, generate: bool) -> WorkflowState:
        state.generate_report = generate
        return state

    @staticmethod
    def get_state_summary(state: WorkflowState) -> Dict[str, Any]:
        return {
            "project_id": state.project_id,
            "total_tasks": len(state.tasks),
            "tasks_by_status": {status: sum(1 for task in state.tasks if task.status == status) for status in set(task.status for task in state.tasks)},
            "generate_report": state.generate_report
        }

    @staticmethod
    def get_task_by_title(state: WorkflowState, title: str) -> Task:
        for task in state.tasks:
            if task.title == title:
                return task
        return None

    @staticmethod
    def get_all_tasks(state: WorkflowState) -> List[Task]:
        return state.tasks

    @staticmethod
    def clear_tasks(state: WorkflowState) -> WorkflowState:
        state.tasks = []
        return state