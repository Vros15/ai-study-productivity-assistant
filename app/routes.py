from flask import Blueprint, redirect, url_for
from flask_login import login_user, logout_user, login_required
from app.models import User

main = Blueprint("main", __name__)

@main.route("/")
def home():
    return "AI Study & Productivity Assistant is running (Auth Ready)!"

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
    return "Welcome to your dashboard!"

@main.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("main.home"))
