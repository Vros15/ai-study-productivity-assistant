# imports
from flask import Flask, render_template, request, redirect, url_for, flash, session, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, timedelta
import os
from dotenv import load_dotenv
import requests

# load environment variables from .env file
load_dotenv()

# initialize Flask app
app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production')
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///study_assistant.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# setup database
db = SQLAlchemy(app)

# setup login manager for user authentication
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'
login_manager.login_message = 'Please log in to access this page.'

# Hugging Face API setup for AI features
HF_API_TOKEN = os.getenv('HUGGINGFACE_API_TOKEN', '')
HF_API_URL = "https://api-inference.huggingface.co/models/mistralai/Mistral-7B-Instruct-v0.2"

# Database Models - tables for storing data

# User table - stores user account info
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(200), nullable=False)  # hashed password for security
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    # relationships to other tables
    assignments = db.relationship('Assignment', backref='user', lazy=True, cascade='all, delete-orphan')
    study_plans = db.relationship('StudyPlan', backref='user', lazy=True, cascade='all, delete-orphan')

# Assignment table - stores all assignments
class Assignment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=True)
    due_date = db.Column(db.DateTime, nullable=False)
    priority = db.Column(db.String(20), default='medium')  # can be: low, medium, high
    status = db.Column(db.String(20), default='pending')  # can be: pending, completed, overdue
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)  # links to user
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

# StudyPlan table - stores AI-generated study plans
class StudyPlan(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.Text, nullable=False)  # the actual study plan text
    assignment_ids = db.Column(db.String(500), nullable=True)  # which assignments are in this plan
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

# this is required by Flask-Login to load users
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Routes - these handle different pages/URLs

# home page
@app.route('/')
def index():
    # if already logged in, go straight to dashboard
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    return render_template('index.html')

# registration page
@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    
    if request.method == 'POST':
        # get form data
        username = request.form.get('username', '').strip()
        email = request.form.get('email', '').strip()
        password = request.form.get('password', '')
        
        # check if all fields are filled
        if not username or not email or not password:
            flash('All fields are required!', 'error')
            return render_template('register.html')
        
        # password length check
        if len(password) < 6:
            flash('Password must be at least 6 characters long!', 'error')
            return render_template('register.html')
        
        # make sure username isn't taken
        if User.query.filter_by(username=username).first():
            flash('Username already exists!', 'error')
            return render_template('register.html')
        
        # make sure email isn't already used
        if User.query.filter_by(email=email).first():
            flash('Email already registered!', 'error')
            return render_template('register.html')
        
        # everything looks good, create the account
        new_user = User(
            username=username,
            email=email,
            password_hash=generate_password_hash(password)  # hash password for security
        )
        db.session.add(new_user)
        db.session.commit()
        
        flash('Account successfully created! Please login.', 'success')
        return redirect(url_for('login'))
    
    return render_template('register.html')

# login page
@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '')
        
        # make sure both fields are filled
        if not username or not password:
            flash('Username and password are required!', 'error')
            return render_template('login.html')
        
        # try to find the user
        user = User.query.filter_by(username=username).first()
        
        # check if user exists and password matches
        if user and check_password_hash(user.password_hash, password):
            login_user(user)
            flash('Login successful!', 'success')
            # redirect to where they were trying to go, or dashboard
            next_page = request.args.get('next')
            return redirect(next_page if next_page else url_for('dashboard'))
        else:
            flash('Invalid username or password!', 'error')
    
    return render_template('login.html')

# logout
@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out.', 'success')
    return redirect(url_for('index'))

# main dashboard page
@app.route('/dashboard')
@login_required
def dashboard():
    # get all assignments for logged in user
    assignments = Assignment.query.filter_by(user_id=current_user.id).order_by(Assignment.due_date.asc()).all()
    
    # check if any assignments are overdue and update them
    for assignment in assignments:
        if assignment.status != 'completed' and assignment.due_date < datetime.now():
            assignment.status = 'overdue'
    db.session.commit()
    
    # calculate some stats to display
    total_assignments = len(assignments)
    completed_assignments = len([a for a in assignments if a.status == 'completed'])
    pending_assignments = len([a for a in assignments if a.status == 'pending'])
    overdue_assignments = len([a for a in assignments if a.status == 'overdue'])
    
    return render_template('dashboard.html', 
                         assignments=assignments,
                         total=total_assignments,
                         completed=completed_assignments,
                         pending=pending_assignments,
                         overdue=overdue_assignments,
                         now=datetime.now())

# assignments page - shows all assignments with filtering
@app.route('/assignments')
@login_required
def assignments():
    priority_filter = request.args.get('priority', 'all')
    status_filter = request.args.get('status', 'all')
    
    query = Assignment.query.filter_by(user_id=current_user.id)
    
    # apply filters if selected
    if priority_filter != 'all':
        query = query.filter_by(priority=priority_filter)
    
    if status_filter != 'all':
        query = query.filter_by(status=status_filter)
    
    assignments = query.order_by(Assignment.due_date.asc()).all()
    
    return render_template('assignments.html', 
                         assignments=assignments,
                         priority_filter=priority_filter,
                         status_filter=status_filter,
                         now=datetime.now())

# add new assignment
@app.route('/assignment/add', methods=['GET', 'POST'])
@login_required
def add_assignment():
    if request.method == 'POST':
        title = request.form.get('title', '').strip()
        description = request.form.get('description', '').strip()
        due_date_str = request.form.get('due_date', '')
        priority = request.form.get('priority', 'medium')
        
        # make sure required fields are filled
        if not title:
            flash('Assignment title is required!', 'error')
            return render_template('add_assignment.html')
        
        if not due_date_str:
            flash('Due date is required!', 'error')
            return render_template('add_assignment.html')
        
        try:
            # convert date string to datetime object
            due_date = datetime.strptime(due_date_str, '%Y-%m-%d')
        except ValueError:
            flash('Invalid date format!', 'error')
            return render_template('add_assignment.html')
        
        # create the new assignment
        new_assignment = Assignment(
            title=title,
            description=description,
            due_date=due_date,
            priority=priority,
            user_id=current_user.id
        )
        db.session.add(new_assignment)
        db.session.commit()
        
        flash('Assignment created successfully!', 'success')
        return redirect(url_for('dashboard'))
    
    return render_template('add_assignment.html')

# edit existing assignment
@app.route('/assignment/edit/<int:assignment_id>', methods=['GET', 'POST'])
@login_required
def edit_assignment(assignment_id):
    assignment = Assignment.query.get_or_404(assignment_id)
    
    # make sure it's the user's assignment
    if assignment.user_id != current_user.id:
        flash('Unauthorized access!', 'error')
        return redirect(url_for('dashboard'))
    
    if request.method == 'POST':
        title = request.form.get('title', '').strip()
        description = request.form.get('description', '').strip()
        due_date_str = request.form.get('due_date', '')
        priority = request.form.get('priority', 'medium')
        
        if not title or not due_date_str:
            flash('Title and due date are required!', 'error')
            return render_template('edit_assignment.html', assignment=assignment)
        
        try:
            due_date = datetime.strptime(due_date_str, '%Y-%m-%d')
        except ValueError:
            flash('Invalid date format!', 'error')
            return render_template('edit_assignment.html', assignment=assignment)
        
        # update assignment details
        assignment.title = title
        assignment.description = description
        assignment.due_date = due_date
        assignment.priority = priority
        assignment.updated_at = datetime.utcnow()
        
        db.session.commit()
        
        flash('Assignment updated successfully!', 'success')
        return redirect(url_for('dashboard'))
    
    return render_template('edit_assignment.html', assignment=assignment)

# delete an assignment
@app.route('/assignment/delete/<int:assignment_id>', methods=['POST'])
@login_required
def delete_assignment(assignment_id):
    assignment = Assignment.query.get_or_404(assignment_id)
    
    # security check - make sure it's their assignment
    if assignment.user_id != current_user.id:
        flash('Unauthorized access!', 'error')
        return redirect(url_for('dashboard'))
    
    db.session.delete(assignment)
    db.session.commit()
    
    flash('Assignment deleted successfully!', 'success')
    return redirect(url_for('dashboard'))

# mark assignment as complete/incomplete
@app.route('/assignment/complete/<int:assignment_id>', methods=['POST'])
@login_required
def complete_assignment(assignment_id):
    assignment = Assignment.query.get_or_404(assignment_id)
    
    if assignment.user_id != current_user.id:
        return jsonify({'error': 'Unauthorized'}), 403
    
    # mark it as done
    assignment.status = 'completed'
    db.session.commit()
    
    return jsonify({'success': True, 'message': 'Assignment marked as completed!'})

# AI study plan page - generates personalized study plans
@app.route('/ai-study-plan', methods=['GET', 'POST'])
@login_required
def ai_study_plan():
    if request.method == 'POST':
        # get the assignments user selected
        selected_assignment_ids = request.form.getlist('assignment_ids')
        
        if not selected_assignment_ids:
            flash('Please select at least one assignment!', 'error')
            return redirect(url_for('ai_study_plan'))
        
        # grab the selected assignments from database
        assignments = Assignment.query.filter(
            Assignment.id.in_(selected_assignment_ids),
            Assignment.user_id == current_user.id
        ).all()
        
        if not assignments:
            flash('No valid assignments selected!', 'error')
            return redirect(url_for('ai_study_plan'))
        
        # use AI to generate study plan
        try:
            study_plan_content = generate_study_plan(assignments)
            
            # save the study plan to database
            study_plan = StudyPlan(
                content=study_plan_content,
                assignment_ids=','.join(selected_assignment_ids),
                user_id=current_user.id
            )
            db.session.add(study_plan)
            db.session.commit()
            
            return render_template('study_plan_result.html', 
                                 study_plan=study_plan_content,
                                 assignments=assignments,
                                 now=datetime.now())
        except Exception as e:
            flash(f'Error generating study plan: {str(e)}', 'error')
            return redirect(url_for('ai_study_plan'))
    
    # show form with pending assignments
    assignments = Assignment.query.filter_by(
        user_id=current_user.id,
        status='pending'
    ).order_by(Assignment.due_date.asc()).all()
    
    return render_template('ai_study_plan.html', assignments=assignments, now=datetime.now())

# AI summary page - generates summaries for assignments
@app.route('/ai-summary', methods=['GET', 'POST'])
@login_required
def ai_summary():
    if request.method == 'POST':
        assignment_id = request.form.get('assignment_id')
        notes = request.form.get('notes', '').strip()
        
        # need either an assignment or notes
        if not assignment_id and not notes:
            flash('Please select an assignment or enter notes!', 'error')
            return redirect(url_for('ai_summary'))
        
        assignment = None
        if assignment_id:
            assignment = Assignment.query.get(assignment_id)
            # make sure it's their assignment
            if not assignment or assignment.user_id != current_user.id:
                flash('Invalid assignment!', 'error')
                return redirect(url_for('ai_summary'))
        
        # generate the AI summary
        try:
            summary = generate_summary(assignment, notes)
            return render_template('summary_result.html', 
                                 summary=summary,
                                 assignment=assignment)
        except Exception as e:
            flash(f'Error generating summary: {str(e)}', 'error')
            return redirect(url_for('ai_summary'))
    
    # show form with all assignments
    assignments = Assignment.query.filter_by(user_id=current_user.id).order_by(Assignment.due_date.asc()).all()
    return render_template('ai_summary.html', assignments=assignments)

# progress tracking page
@app.route('/progress')
@login_required
def progress():
    assignments = Assignment.query.filter_by(user_id=current_user.id).all()
    
    # calculate statistics
    total = len(assignments)
    completed = len([a for a in assignments if a.status == 'completed'])
    pending = len([a for a in assignments if a.status == 'pending'])
    overdue = len([a for a in assignments if a.status == 'overdue'])
    
    completion_rate = (completed / total * 100) if total > 0 else 0
    
    # breakdown by priority
    high_priority = len([a for a in assignments if a.priority == 'high'])
    medium_priority = len([a for a in assignments if a.priority == 'medium'])
    low_priority = len([a for a in assignments if a.priority == 'low'])
    
    # get recent study plans
    study_plans = StudyPlan.query.filter_by(user_id=current_user.id).order_by(StudyPlan.created_at.desc()).limit(5).all()
    
    return render_template('progress.html',
                         total=total,
                         completed=completed,
                         pending=pending,
                         overdue=overdue,
                         completion_rate=round(completion_rate, 1),
                         high_priority=high_priority,
                         medium_priority=medium_priority,
                         low_priority=low_priority,
                         study_plans=study_plans,
                         assignments=assignments)

# AI Helper Functions - these handle the AI features

# convert markdown text to HTML
def markdown_to_html(text):
    # Replace headers
    text = text.replace('### ', '<h4>').replace('\n##', '</h4>\n<h3>').replace('\n#', '</h3>\n<h2>')
    
    # Handle bold text with regex
    import re
    text = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', text)
    
    # Handle lists - convert markdown lists to HTML
    lines = text.split('\n')
    html_lines = []
    in_list = False
    
    for line in lines:
        stripped = line.strip()
        if stripped.startswith('- ') or stripped.startswith('* '):
            if not in_list:
                html_lines.append('<ul>')
                in_list = True
            html_lines.append(f'<li>{stripped[2:]}</li>')
        elif stripped and stripped[0].isdigit() and '. ' in stripped[:5]:
            # handle numbered lists
            if not in_list:
                html_lines.append('<ol>')
                in_list = 'ol'
            content = stripped.split('. ', 1)[1] if '. ' in stripped else stripped
            html_lines.append(f'<li>{content}</li>')
        else:
            if in_list:
                html_lines.append('</ol>' if in_list == 'ol' else '</ul>')
                in_list = False
            if stripped:
                html_lines.append(f'<p>{line}</p>')
            else:
                html_lines.append('')
    
    if in_list:
        html_lines.append('</ol>' if in_list == 'ol' else '</ul>')
    
    return '\n'.join(html_lines)

# call Hugging Face API to get AI response
def call_huggingface_api(prompt, max_new_tokens=800):
    if not HF_API_TOKEN:
        return None
    
    headers = {"Authorization": f"Bearer {HF_API_TOKEN}"}
    
    payload = {
        "inputs": prompt,
        "parameters": {
            "max_new_tokens": max_new_tokens,
            "temperature": 0.7,
            "top_p": 0.95,
            "do_sample": True
        }
    }
    
    try:
        response = requests.post(HF_API_URL, headers=headers, json=payload, timeout=30)
        response.raise_for_status()
        result = response.json()
        
        if isinstance(result, list) and len(result) > 0:
            return result[0].get('generated_text', '')
        elif isinstance(result, dict):
            return result.get('generated_text', '')
        return None
    except Exception as e:
        print(f"Hugging Face API Error: {e}")
        return None

# generate study plan using AI
def generate_study_plan(assignments):
    # prepare assignment info for the AI
    assignment_info = []
    for a in assignments:
        days_until_due = (a.due_date - datetime.now()).days
        assignment_info.append(f"- {a.title} (Due: {a.due_date.strftime('%Y-%m-%d')}, Priority: {a.priority}, Days remaining: {days_until_due})")
    
    prompt = f"""[INST] You are a helpful academic study assistant. Create a personalized study plan for these assignments:

{chr(10).join(assignment_info)}

Provide:
1. A recommended study schedule
2. Time allocation for each assignment based on priority and due date
3. Specific study strategies and tips
4. Milestones and checkpoints

Format the response clearly. [/INST]"""

    # try using Hugging Face AI first
    ai_response = call_huggingface_api(prompt, max_new_tokens=800)
    
    if ai_response:
        # extract only the response part (after [/INST])
        if '[/INST]' in ai_response:
            ai_response = ai_response.split('[/INST]')[-1].strip()
        # convert from markdown to HTML
        return markdown_to_html(ai_response)
    
    # if AI fails, use basic fallback
    return generate_fallback_study_plan(assignments)

# backup study plan generator (no AI needed)
def generate_fallback_study_plan(assignments):
    plan = "<h2>Personalized Study Plan</h2>"
    plan += "<h3>Your Assignments</h3>"
    
    # sort by due date and priority
    sorted_assignments = sorted(assignments, key=lambda x: (x.due_date, {'high': 1, 'medium': 2, 'low': 3}[x.priority]))
    
    for i, assignment in enumerate(sorted_assignments, 1):
        days_until_due = (assignment.due_date - datetime.now()).days
        plan += f"<h4>{i}. {assignment.title}</h4>"
        plan += "<ul>"
        plan += f"<li><strong>Due Date:</strong> {assignment.due_date.strftime('%B %d, %Y')}</li>"
        plan += f"<li><strong>Priority:</strong> {assignment.priority.capitalize()}</li>"
        plan += f"<li><strong>Days Remaining:</strong> {days_until_due}</li>"
        
        # give recommendations based on time left
        if days_until_due <= 3:
            plan += f"<li><strong>Recommendation:</strong> This assignment is due soon! Prioritize completing this today.</li>"
        elif days_until_due <= 7:
            plan += f"<li><strong>Recommendation:</strong> Allocate 1-2 hours daily to complete this assignment.</li>"
        else:
            plan += f"<li><strong>Recommendation:</strong> Plan to work on this assignment regularly over the next {days_until_due} days.</li>"
        
        plan += "</ul>"
    
    plan += "<h3>Study Tips</h3>"
    plan += "<ul>"
    plan += "<li>Break large assignments into smaller tasks</li>"
    plan += "<li>Schedule regular study sessions</li>"
    plan += "<li>Take short breaks every 50 minutes</li>"
    plan += "<li>Start with high-priority items</li>"
    plan += "<li>Review completed work before submission</li>"
    plan += "</ul>"
    
    return plan

# generate summary for assignment or notes using AI
def generate_summary(assignment, notes):
    if assignment:
        prompt = f"""[INST] You are a helpful academic study assistant. Provide a concise study summary for this assignment:

Title: {assignment.title}
Description: {assignment.description or 'No description provided'}
Due Date: {assignment.due_date.strftime('%Y-%m-%d')}
Priority: {assignment.priority}
Additional notes: {notes if notes else 'None'}

Provide:
1. Key points to focus on
2. Suggested approach
3. Time management tips [/INST]"""
    else:
        prompt = f"""[INST] You are a helpful study assistant. Provide a study summary and key takeaways for these notes:

{notes}

Organize the information clearly and highlight important points. [/INST]"""

    # try using Hugging Face AI first
    ai_response = call_huggingface_api(prompt, max_new_tokens=600)
    
    if ai_response:
        # extract the response (after [/INST])
        if '[/INST]' in ai_response:
            ai_response = ai_response.split('[/INST]')[-1].strip()
        # convert markdown to HTML
        return markdown_to_html(ai_response)
    
    # fallback if AI isn't working
    return generate_fallback_summary(assignment, notes)

# backup summary generator (no AI needed)
def generate_fallback_summary(assignment, notes):
    summary = "<h2>Study Summary</h2>"
    
    if assignment:
        summary += f"<h3>Assignment: {assignment.title}</h3>"
        days_until_due = (assignment.due_date - datetime.now()).days
        
        summary += "<h4>Key Information</h4>"
        summary += "<ul>"
        summary += f"<li><strong>Due Date:</strong> {assignment.due_date.strftime('%B %d, %Y')} ({days_until_due} days remaining)</li>"
        summary += f"<li><strong>Priority Level:</strong> {assignment.priority.capitalize()}</li>"
        summary += "</ul>"
        
        if assignment.description:
            summary += f"<h4>Description</h4><p>{assignment.description}</p>"
        
        summary += "<h4>Suggested Approach</h4>"
        summary += "<ol>"
        summary += "<li>Review all assignment requirements carefully</li>"
        summary += "<li>Break down the assignment into manageable tasks</li>"
        summary += "<li>Create a timeline for completion</li>"
        summary += "<li>Gather necessary resources and materials</li>"
        summary += "<li>Start with the most challenging parts first</li>"
        summary += "</ol>"
        
        # urgent warning if due soon
        if days_until_due <= 3:
            summary += '<div class="alert alert-warning">⚠️ <strong>Urgent:</strong> This assignment is due very soon. Focus your efforts on completing it as soon as possible.</div>'
    
    if notes:
        summary += f"<h4>Additional Notes</h4><p>{notes}</p>"
    
    summary += "<h4>Study Tips</h4>"
    summary += "<ul>"
    summary += "<li>Stay organized and keep track of your progress</li>"
    summary += "<li>Take regular breaks to maintain focus</li>"
    summary += "<li>Seek help if you encounter difficulties</li>"
    summary += "<li>Review your work before final submission</li>"
    summary += "</ul>"
    
    return summary

# setup database tables
def init_db():
    with app.app_context():
        db.create_all()
        print("Database initialized successfully!")

# run the app
if __name__ == '__main__':
    init_db()
    app.run(debug=True, host='0.0.0.0', port=5000)
