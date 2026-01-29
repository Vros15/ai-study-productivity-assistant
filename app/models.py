"""
File: app/models.py
Description:
    Database models for the AI Study & Productivity Assistant.
    Defines User and Assignment entities.
"""

from app import db, login_manager
from flask_login import UserMixin
from datetime import datetime

class User(UserMixin, db.Model):
    """
    User model representing registered users of the system.
    """
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)

    assignments = db.relationship("Assignment", backref="user", lazy=True)

class Assignment(db.Model):
    """
    Assignment model representing coursework tasks.
    """
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    due_date = db.Column(db.DateTime, nullable=False)
    priority = db.Column(db.String(20), default="Medium")
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)

@login_manager.user_loader
def load_user(user_id):
    """
    Loads a user from the database for session management.

    Args:
        user_id (int): User ID stored in session

    Returns:
        User: User object if found
    """
    return User.query.get(int(user_id))
