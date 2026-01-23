<<<<<<< HEAD
from flask import Flask

app = Flask(__name__)

@app.route("/")
def home():
    return "AI Study & Productivity Assistant is running!"
=======
from app import create_app

app = create_app()
>>>>>>> f7c8b65 (Fix app package initialization and confirm Flask app runs)

if __name__ == "__main__":
    app.run(debug=True)
