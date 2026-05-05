import sqlite3
import datetime
from database import register_user, authenticate_user, add_task

def seed_db():
    email = "test@example.com"
    password = "test1234"
    
    # 1. Register or Authenticate User
    success, result = register_user(email, password)
    if not success:
        # User might already exist, authenticate to get ID
        success, result = authenticate_user(email, password)
        if not success:
            print("Failed to authenticate or register.")
            return
            
    user_id = result
    print(f"User ID: {user_id}")
    
    # Generate relative dates
    today = datetime.date.today()
    yesterday = today - datetime.timedelta(days=1)
    day_before = today - datetime.timedelta(days=2)
    two_days_before = today - datetime.timedelta(days=3)
    tomorrow = today + datetime.timedelta(days=1)
    next_week = today + datetime.timedelta(days=5)
    
    # 2. Sample Tasks
    tasks = [
        # Completed Tasks (To show productivity graph)
        ("Design Figma Mockups", "Create high-fidelity UI/UX mockups for the dashboard.", "Low", "Completed", two_days_before),
        ("Setup Streamlit Environment", "Install dependencies and configure virtual environment.", "Medium", "Completed", day_before),
        ("Initialize SQLite Database", "Create database schema and connect to Python backend.", "High", "Completed", yesterday),
        
        # In Progress Tasks
        ("Develop Authentication Flow", "Implement SHA-256 hashing and user registration logic.", "High", "In Progress", today),
        ("Integrate Analytics Dashboard", "Build charts to display user productivity.", "Medium", "In Progress", today),
        
        # To Do Tasks
        ("Prepare Presentation Slides", "Create slides for the final project evaluation.", "High", "To Do", tomorrow),
        ("Write Project Report", "Document architecture, design decisions, and database schema.", "Medium", "To Do", next_week),
        
        # Overdue Task (To trigger red glow and smart insight)
        ("Fix Sidebar Navigation Bug", "Investigate why the sidebar toggle is occasionally invisible.", "Low", "To Do", yesterday)
    ]
    
    for t in tasks:
        add_task(user_id, t[0], t[1], t[2], t[3], t[4].strftime("%Y-%m-%d"), email)
        
    print("Database seeded successfully with sample data!")

if __name__ == "__main__":
    seed_db()
