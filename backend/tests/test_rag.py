import pytest
from unittest.mock import Mock, patch
from backend.ai_engine.rag.vector_store import VectorStore
from backend.ai_engine.rag.retriever import Retriever

@pytest.fixture
def mock_db():
    return Mock()

@pytest.fixture
def mock_vector_store():
    with patch('backend.ai_engine.rag.vector_store.FAISS') as mock_faiss:
        mock_vs = VectorStore()
        mock_vs.vector_store = Mock()
        yield mock_vs

def test_vector_store_creation(mock_vector_store):
    texts = ["Test document 1", "Test document 2"]
    metadatas = [{"source": "test1"}, {"source": "test2"}]
    
    mock_vector_store.create_vector_store(texts, metadatas)
    
    mock_vector_store.vector_store.from_documents.assert_called_once()

def test_vector_store_similarity_search(mock_vector_store):
    mock_vector_store.vector_store.similarity_search.return_value = [
        Mock(page_content="Similar document 1", metadata={"source": "test1"}),
        Mock(page_content="Similar document 2", metadata={"source": "test2"})
    ]
    
    results = mock_vector_store.similarity_search("test query", k=2)
    
    assert len(results) == 2
    assert results[0].page_content == "Similar document 1"
    assert results[1].metadata["source"] == "test2"

def test_retriever_get_similar_tasks(mock_db):
    with patch('backend.ai_engine.rag.retriever.vector_store') as mock_vs:
        mock_vs.similarity_search.return_value = [
            Mock(metadata={"title": "Similar Task 1"}, page_content="Description 1"),
            Mock(metadata={"title": "Similar Task 2"}, page_content="Description 2")
        ]
        
        retriever = Retriever(mock_db)
        similar_tasks = retriever.get_similar_tasks("New task description", project_id=1, k=2)
        
        assert len(similar_tasks) == 2
        assert similar_tasks[0]["title"] == "Similar Task 1"
        assert similar_tasks[1]["description"] == "Description 2"

def test_retriever_get_project_context(mock_db):
    mock_db.query().filter().first.return_value = Mock(
        name="Test Project",
        description="A test project",
        start_date="2023-01-01",
        end_date="2023-12-31",
        status="In Progress"
    )
    
    retriever = Retriever(mock_db)
    context = retriever.get_project_context(project_id=1)
    
    assert context["name"] == "Test Project"
    assert context["status"] == "In Progress"

def test_retriever_get_team_skills(mock_db):
    mock_db.query().filter().all.return_value = [
        Mock(name="Alice", skills=["Python", "JavaScript"]),
        Mock(name="Bob", skills=["Java", "C++"])
    ]
    
    retriever = Retriever(mock_db)
    skills = retriever.get_team_skills(project_id=1)
    
    assert skills == {
        "Alice": ["Python", "JavaScript"],
        "Bob": ["Java", "C++"]
    }

def test_retriever_get_similar_projects(mock_db):
    with patch('backend.ai_engine.rag.retriever.vector_store') as mock_vs:
        mock_vs.similarity_search.return_value = [
            Mock(metadata={"name": "Similar Project 1"}, page_content="Description 1"),
            Mock(metadata={"name": "Similar Project 2"}, page_content="Description 2")
        ]
        
        retriever = Retriever(mock_db)
        similar_projects = retriever.get_similar_projects(project_id=1, k=2)
        
        assert len(similar_projects) == 2
        assert similar_projects[0]["name"] == "Similar Project 1"
        assert similar_projects[1]["description"] == "Description 2"
