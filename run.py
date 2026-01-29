"""
File: run.py
Project: AI Study & Productivity Assistant
Course: UMGC CMSC 495
Author(s): Victor Rosario, Akshay Sonilal-Rambarran, Jorge Armijosmurillo, Nicholas Porpora
Description:
    Entry point for the Flask web application. This file initializes
    the application using the app factory pattern and starts the
    development server.
"""

from app import create_app

app = create_app()

if __name__ == "__main__":
    app.run(debug=True)
