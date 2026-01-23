from flask import Blueprint, redirect, url_for, request, render_template
from flask_login import login_user, logout_user, login_required, current_user
from app.models import User, Assignment
from app import db
from datetime import datetime

main = Blueprint("main", __name__)

@main.route("/")
def home():
    return redirect(url_for("main.dashboard"))

@main.route("/login")
def login():
    user = User.query.first()
    if user:
        login_user(user)
        return redirect(url_for("main.dashboard"))
    return "No users exist yet."

@main.route("/dashboard")
@login_required
def dashboard():
    assignments = Assignment.query.filter_by(user_id=current_user.id).all()
    return render_template("dashboard.html", assignments=assignments)

@main.route("/assignments/add", methods=["POST"])
@login_required
def add_assignment():
    title = request.form.get("title")
    description = request.form.get("description")
    due_date = request.form.get("due_date")
    priority = request.form.get("priority")

    assignment = Assignment(
        title=title,
        description=description,
        due_date=datetime.strptime(due_date, "%Y-%m-%d"),
        priority=priority,
        user_id=current_user.id
    )

    db.session.add(assignment)
    db.session.commit()

    return redirect(url_for("main.dashboard"))

@main.route("/assignments/delete/<int:assignment_id>")
@login_required
def delete_assignment(assignment_id):
    assignment = Assignment.query.get_or_404(assignment_id)

    if assignment.user_id != current_user.id:
        return "Unauthorized", 403

    db.session.delete(assignment)
    db.session.commit()

    return redirect(url_for("main.dashboard"))

@main.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("main.home"))
