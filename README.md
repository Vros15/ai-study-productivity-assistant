# AI Study & Productivity Assistant

## 📌 Project Overview
The **AI Study & Productivity Assistant** is a web-based application designed to help college students manage assignments, track deadlines, generate study plans, and receive AI-powered academic support. The system focuses on improving time management, organization, and study efficiency through an intuitive interface and AI integration.

This project is developed as part of **UMGC CMSC 495 – Current Trends and Projects in Computer Science**.

---

## 🧑‍💻 Team Members
- Victor Rosario  
- Jorge Armijosmurillo  
- Akshay Sonilal-Rambarran  

---

## 🛠️ Technology Stack
- Python 3.x  
- Flask  
- Flask-Login  
- Flask-SQLAlchemy  
- OpenAI API  
- HTML / CSS / JavaScript  
- Git & GitHub  

---

## 📁 Project Structure


ai-study-productivity-assistant/
├── run.py
├── requirements.txt
├── .gitignore
├── .env # Not committed
├── venv/ # Not committed
├── app/ # Application package (routes, models, AI logic)
└── README.md


---

## 🚀 Team Setup Instructions

### 1️⃣ Install Required Software
- **Git**  
  https://git-scm.com/downloads

- **Python 3.x**  
  ⚠️ Make sure to check **“Add Python to PATH”**  
  https://www.python.org/downloads/

- **VS Code (recommended)**  
  https://code.visualstudio.com/

Restart your terminal after installation.

---

### 2️⃣ Clone the Repository
Open **Git Bash (Windows)** or **Terminal (Mac/Linux)**:

```bash
git clone https://github.com/Vros15/ai-study-productivity-assistant.git
cd ai-study-productivity-assistant

3️⃣ Switch to the Development Branch
git checkout dev


Confirm:

git branch


You should see:

* dev
  main

4️⃣ Create and Activate Virtual Environment
python -m venv venv


Activate it:

Windows (Git Bash):

source venv/Scripts/activate


Mac/Linux:

source venv/bin/activate


You should see (venv) in the terminal.

5️⃣ Install Dependencies
pip install -r requirements.txt

6️⃣ Create .env File (DO NOT COMMIT)

Create a file named .env in the project root:

OPENAI_API_KEY=your_api_key_here


⚠️ Never commit .env to GitHub
(It is already included in .gitignore.)

7️⃣ Run the Application
python run.py


Open your browser and go to:

http://127.0.0.1:5000


If you see:

AI Study & Productivity Assistant is running!


✅ Setup is complete.

🔒 Git Workflow Rules

To avoid conflicts and broken code, follow these rules strictly:

❌ Never commit directly to main

❌ Never commit directly to dev

✅ Always work in a feature branch

✅ Merge changes into dev using a Pull Request

🔀 Creating a Feature Branch
git checkout dev
git pull origin dev
git checkout -b feature-your-feature-name


Examples:

feature-auth

feature-ai-service

feature-dashboard

⬆️ Pushing Your Work
git add .
git commit -m "Brief description of changes"
git push origin feature-your-feature-name


Then open a Pull Request → dev on GitHub.

🧪 Testing & Development Notes

Always pull latest dev before starting work

Commit small, logical changes

Use clear commit messages

If something breaks, ask before pushing

📌 Contribution Expectations

All team members are expected to:

Follow the Git workflow

Test code before pushing

Document major changes

Communicate blockers early

📄 License

This project is developed for academic purposes as part of a UMGC capstone course.
