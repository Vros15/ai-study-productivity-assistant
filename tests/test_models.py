"""
File: test_models.py
Description:
    Unit tests for database models.
"""

from app.models import User, Assignment
from datetime import datetime

def test_user_model_creation():
    """
    Verifies User model attributes.
    """
    user = User(
        username="testuser",
        email="test@example.com",
        password="password"
    )
    assert user.username == "testuser"
    assert user.email == "test@example.com"

def test_assignment_model_creation():
    """
    Verifies Assignment model attributes.
    """
    assignment = Assignment(
        title="Test Assignment",
        description="Test Description",
        due_date=datetime.utcnow(),
        priority="High",
        user_id=1
    )
    assert assignment.title == "Test Assignment"
    assert assignment.priority == "High"
