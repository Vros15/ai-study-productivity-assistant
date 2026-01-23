from flask import Blueprint

main = Blueprint('main', __name__)

@main.route("/")
def home():
    return "AI Study & Productivity Assistant is running (Database Ready)!"

