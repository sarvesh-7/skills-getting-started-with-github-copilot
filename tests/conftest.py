import pytest
from fastapi.testclient import TestClient
from src.app import app


@pytest.fixture
def client():
    """Fixture to provide a test client for the FastAPI app"""
    return TestClient(app)


@pytest.fixture
def sample_activity_data():
    """Fixture providing sample activity data for testing"""
    return {
        "description": "Test activity for testing",
        "schedule": "Test schedule",
        "max_participants": 10,
        "participants": ["test@example.com"]
    }


@pytest.fixture
def test_email():
    """Fixture providing a test email address"""
    return "testuser@mergington.edu"