import pytest
from unittest.mock import Mock, patch
from backend.ai_engine.agents.task_agent import TaskAgent
from backend.ai_engine.agents.priority_agent import PriorityAgent
from backend.ai_engine.agents.suggestion_agent import SuggestionAgent
from backend.ai_engine.agents.report_agent import ReportAgent
from backend.ai_engine.agents.collaboration_agent import CollaborationAgent

@pytest.fixture
def mock_retriever():
    return Mock()

def test_task_agent(mock_retriever):
    with patch('backend.ai_engine.agents.task_agent.Retriever', return_value=mock_retriever):
        task_agent = TaskAgent()
        mock_retriever.get_similar_tasks.return_value = [{"title": "Similar Task", "description": "A similar task"}]
        mock_retriever.get_project_context.return_value = {"name": "Test Project", "description": "A test project"}
        
        task = task_agent.create_task("Create a new feature", project_id=1)
        
        assert "title" in task
        assert "estimated_duration" in task
        assert "required_skills" in task
        assert task["status"] == "New"

def test_priority_agent(mock_retriever):
    with patch('backend.ai_engine.agents.priority_agent.Retriever', return_value=mock_retriever):
        priority_agent = PriorityAgent()
        mock_retriever.get_project_context.return_value = {"name": "Test Project", "description": "A test project"}
        mock_retriever.get_similar_tasks_priorities.return_value = [{"title": "Similar Task", "priority": "High"}]
        
        task = {
            "title": "Implement user authentication",
            "estimated_duration": 16,
            "required_skills": ["Python", "Security"]
        }
        priority_info = priority_agent.assign_priority(task, project_id=1)
        
        assert "priority" in priority_info
        assert "reasoning" in priority_info

def test_suggestion_agent(mock_retriever):
    with patch('backend.ai_engine.agents.suggestion_agent.Retriever', return_value=mock_retriever):
        suggestion_agent = SuggestionAgent()
        mock_retriever.get_project_context.return_value = {"name": "Test Project", "description": "A test project"}
        mock_retriever.get_similar_completed_tasks.return_value = [{"title": "Similar Task", "description": "A completed similar task"}]
        mock_retriever.get_team_skills.return_value = {"Alice": ["Python", "JavaScript"], "Bob": ["Java", "C++"]}
        
        task = {
            "title": "Implement data visualization",
            "estimated_duration": 24,
            "required_skills": ["Python", "D3.js"]
        }
        suggestions = suggestion_agent.generate_suggestions(task, project_id=1)
        
        assert "suggestions" in suggestions
        assert "resources" in suggestions

def test_report_agent(mock_retriever):
    with patch('backend.ai_engine.agents.report_agent.Retriever', return_value=mock_retriever):
        report_agent = ReportAgent()
        mock_retriever.get_project_context.return_value = {"name": "Test Project", "description": "A test project"}
        mock_retriever.get_project_tasks.return_value = [
            {"title": "Task 1", "status": "Completed"},
            {"title": "Task 2", "status": "In Progress"}
        ]
        mock_retriever.get_team_performance.return_value = {"task_completion_rate": 0.5}
        mock_retriever.get_similar_projects.return_value = [{"name": "Similar Project", "description": "A similar project"}]
        
        report = report_agent.generate_report(project_id=1)
        
        assert "summary" in report
        assert "key_metrics" in report
        assert "risks" in report
        assert "recommendations" in report

def test_collaboration_agent(mock_retriever):
    with patch('backend.ai_engine.agents.collaboration_agent.Retriever', return_value=mock_retriever):
        collaboration_agent = CollaborationAgent()
        mock_retriever.get_project_context.return_value = {"name": "Test Project", "description": "A test project"}
        mock_retriever.get_available_team_members.return_value = [
            {"name": "Alice", "skills": ["Python", "JavaScript"]},
            {"name": "Bob", "skills": ["Java", "C++"]}
        ]
        mock_retriever.get_similar_collaborations.return_value = [{"task": "Similar Task", "collaboration": "Previous collaboration info"}]
        
        task = {
            "title": "Develop API",
            "estimated_duration": 40,
            "required_skills": ["Python", "RESTful API"]
        }
        collaboration_info = collaboration_agent.suggest_collaboration(task, project_id=1)
        
        assert "team_formation" in collaboration_info
        assert "communication_plan" in collaboration_info