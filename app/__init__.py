"""
File: app/__init__.py
Description:
    Application factory for the AI Study & Productivity Assistant.
    Initializes Flask, database connections, and authentication.
"""

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from dotenv import load_dotenv
import os

db = SQLAlchemy()
login_manager = LoginManager()

def create_app():
    """
    Creates and configures the Flask application.

    Returns:
        app (Flask): Configured Flask application instance
    """
    load_dotenv()

    app = Flask(__name__)
    app.config["SECRET_KEY"] = os.getenv("SECRET_KEY", "dev-secret-key")
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///site.db"
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    db.init_app(app)
    login_manager.init_app(app)
    login_manager.login_view = "main.login"

    from app.routes import main
    app.register_blueprint(main)

    with app.app_context():
        db.create_all()

    return app
