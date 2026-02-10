"""
File: test_app.py
Description:
    Unit tests for Flask application initialization.
"""

from app import create_app

def test_app_creation():
    """
    Verifies that the Flask app is created successfully.
    """
    app = create_app()
    assert app is not None
