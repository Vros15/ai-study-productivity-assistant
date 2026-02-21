"""
File: app/routes.py
Description:
    Defines application routes and request handling logic.
"""

from flask import Blueprint, redirect, url_for, request, render_template
from flask_login import login_user, logout_user, login_required, current_user
from app.models import User, Assignment
from app import db
from datetime import datetime

main = Blueprint("main", __name__)


@main.route("/")
def home():
    """
    Redirects users to the dashboard.
    """
    return redirect(url_for("main.dashboard"))


@main.route("/login")
def login():
    """
    Temporary login route for testing authentication.
    Automatically logs in the first user in the database.
    """
    user = User.query.first()
    if user:
        login_user(user)
        return redirect(url_for("main.dashboard"))
    return "No users exist yet."


@main.route("/dashboard")
@login_required
def dashboard():
    """
    Displays the user dashboard and assignments.
    """
    assignments = Assignment.query.filter_by(
        user_id=current_user.id
    ).all()

    return render_template("dashboard.html", assignments=assignments)


@main.route("/assignments/add", methods=["POST"])
@login_required
def add_assignment():
    """
    Adds a new assignment for the logged-in user.
    Includes validation for date input.
    """
    date_input = request.form.get("due_date")

    try:
        parsed_date = datetime.strptime(date_input, "%Y-%m-%d")
    except (ValueError, TypeError):
        return "Invalid date format. Please use YYYY-MM-DD.", 400

    assignment = Assignment(
        title=request.form.get("title"),
        description=request.form.get("description"),
        due_date=parsed_date,
        priority=request.form.get("priority"),
        user_id=current_user.id
    )

    db.session.add(assignment)
    db.session.commit()

    return redirect(url_for("main.dashboard"))


@main.route("/assignments/delete/<int:assignment_id>", methods=["POST"])
@login_required
def delete_assignment(assignment_id):
    """
    Deletes an assignment owned by the logged-in user.
    """
    assignment = Assignment.query.get_or_404(assignment_id)

    if assignment.user_id != current_user.id:
        return "Unauthorized", 403

    db.session.delete(assignment)
    db.session.commit()

    return redirect(url_for("main.dashboard"))


@main.route("/logout")
@login_required
def logout():
    """
    Logs out the current user.
    """
    logout_user()
    return redirect(url_for("main.home"))