from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from backend.database.database import Base
from backend.main import app
from backend.api.dependencies import get_db, get_current_active_user
from backend.database import crud, schemas
import pytest
from unittest.mock import Mock

SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"

engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base.metadata.create_all(bind=engine)

def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db

# Mock the current user for testing
mock_user = schemas.User(id=1, username="testuser", email="test@example.com", is_active=True)
app.dependency_overrides[get_current_active_user] = lambda: mock_user

client = TestClient(app)

@pytest.fixture(autouse=True)
def setup_db():
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)

def test_create_project():
    response = client.post(
        "/api/v1/projects/",
        json={"name": "Test Project", "description": "A test project"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Test Project"
    assert "id" in data

def test_read_projects():
    # Create a few projects first
    client.post("/api/v1/projects/", json={"name": "Project 1", "description": "Description 1"})
    client.post("/api/v1/projects/", json={"name": "Project 2", "description": "Description 2"})

    response = client.get("/api/v1/projects/")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) >= 2

def test_read_project():
    # First, create a project
    create_response = client.post(
        "/api/v1/projects/",
        json={"name": "Test Project", "description": "A test project"}
    )
    project_id = create_response.json()["id"]

    # Then, read the project
    read_response = client.get(f"/api/v1/projects/{project_id}")
    assert read_response.status_code == 200
    data = read_response.json()
    assert data["name"] == "Test Project"
    assert data["id"] == project_id

def test_create_task():
    # First, create a project
    project_response = client.post(
        "/api/v1/projects/",
        json={"name": "Test Project", "description": "A test project"}
    )
    project_id = project_response.json()["id"]

    # Then, create a task
    task_response = client.post(
        f"/api/v1/projects/{project_id}/tasks/",
        json={"description": "Test task description"}
    )
    assert task_response.status_code == 200
    data = task_response.json()
    assert "title" in data
    assert data["project_id"] == project_id

def test_read_tasks():
    # First, create a project
    project_response = client.post(
        "/api/v1/projects/",
        json={"name": "Test Project", "description": "A test project"}
    )
    project_id = project_response.json()["id"]

    # Create a few tasks
    client.post(f"/api/v1/projects/{project_id}/tasks/", json={"description": "Task 1"})
    client.post(f"/api/v1/projects/{project_id}/tasks/", json={"description": "Task 2"})

    # Read tasks
    response = client.get(f"/api/v1/projects/{project_id}/tasks/")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) >= 2

def test_generate_project_report():
    # First, create a project
    project_response = client.post(
        "/api/v1/projects/",
        json={"name": "Test Project", "description": "A test project"}
    )
    project_id = project_response.json()["id"]

    # Create some tasks
    client.post(f"/api/v1/projects/{project_id}/tasks/", json={"description": "Task 1"})
    client.post(f"/api/v1/projects/{project_id}/tasks/", json={"description": "Task 2"})

    # Generate report
    response = client.post(f"/api/v1/projects/{project_id}/report/")
    assert response.status_code == 200
    data = response.json()
    assert "summary" in data
    assert "key_metrics" in data
    assert "risks" in data
    assert "recommendations" in data

def test_nonexistent_project():
    response = client.get("/api/v1/projects/9999")
    assert response.status_code == 404

def test_unauthorized_access():
    # Create a project
    project_response = client.post(
        "/api/v1/projects/",
        json={"name": "Test Project", "description": "A test project"}
    )
    project_id = project_response.json()["id"]

    # Mock a different user
    different_user = schemas.User(id=2, username="otheruser", email="other@example.com", is_active=True)
    app.dependency_overrides[get_current_active_user] = lambda: different_user

    # Try to access the project
    response = client.get(f"/api/v1/projects/{project_id}")
    assert response.status_code == 403

    # Reset the mock
    app.dependency_overrides[get_current_active_user] = lambda: mock_user