"""
Test Data Seeder for AI Study Assistant
Run this script to populate the database with sample data for testing
"""

from app import app, db, User, Assignment, generate_password_hash
from datetime import datetime, timedelta

def seed_test_data():
    """Create test user and sample assignments"""
    with app.app_context():
        # Check if test user already exists
        test_user = User.query.filter_by(username='testuser').first()
        
        if test_user:
            print("Test user already exists. Skipping user creation.")
        else:
            # Create test user
            test_user = User(
                username='testuser',
                email='test@example.com',
                password_hash=generate_password_hash('test123')
            )
            db.session.add(test_user)
            db.session.commit()
            print("✅ Created test user: testuser / test123")
        
        # Create sample assignments
        assignments = [
            {
                'title': 'Research Paper on AI Ethics',
                'description': 'Write a 10-page research paper exploring the ethical implications of artificial intelligence in modern society.',
                'due_date': datetime.now() + timedelta(days=7),
                'priority': 'high'
            },
            {
                'title': 'Database Design Project',
                'description': 'Design and implement a relational database for a school management system.',
                'due_date': datetime.now() + timedelta(days=14),
                'priority': 'high'
            },
            {
                'title': 'Software Testing Lab',
                'description': 'Complete unit testing exercises for the calculator application.',
                'due_date': datetime.now() + timedelta(days=3),
                'priority': 'medium'
            },
            {
                'title': 'Weekly Discussion Post',
                'description': 'Respond to this week\'s discussion prompt about Agile methodologies.',
                'due_date': datetime.now() + timedelta(days=2),
                'priority': 'medium'
            },
            {
                'title': 'Chapter 5 Reading Assignment',
                'description': 'Read Chapter 5 of Software Engineering textbook and take notes.',
                'due_date': datetime.now() + timedelta(days=5),
                'priority': 'low'
            },
            {
                'title': 'Practice Quiz - Data Structures',
                'description': 'Complete the practice quiz on arrays, linked lists, and trees.',
                'due_date': datetime.now() + timedelta(days=4),
                'priority': 'low'
            },
            {
                'title': 'Team Meeting Preparation',
                'description': 'Prepare presentation slides for weekly team standup meeting.',
                'due_date': datetime.now() + timedelta(days=1),
                'priority': 'high'
            }
        ]
        
        # Add assignments
        for assignment_data in assignments:
            # Check if similar assignment exists
            existing = Assignment.query.filter_by(
                title=assignment_data['title'],
                user_id=test_user.id
            ).first()
            
            if not existing:
                assignment = Assignment(
                    title=assignment_data['title'],
                    description=assignment_data['description'],
                    due_date=assignment_data['due_date'],
                    priority=assignment_data['priority'],
                    status='pending',
                    user_id=test_user.id
                )
                db.session.add(assignment)
                print(f"✅ Added: {assignment_data['title']}")
            else:
                print(f"⏭️  Skipped (already exists): {assignment_data['title']}")
        
        db.session.commit()
        print("\n✨ Test data seeding completed!")
        print("\n📝 Login credentials:")
        print("   Username: testuser")
        print("   Password: test123")
        print(f"\n📊 Total assignments: {len(assignments)}")

if __name__ == '__main__':
    print("🌱 Seeding test data...\n")
    seed_test_data()
