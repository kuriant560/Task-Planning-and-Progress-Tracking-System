import sqlite3
import hashlib
from datetime import date

DB_NAME = "task_planner.db"

def init_db():
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    email TEXT UNIQUE,
                    password TEXT
                )''')
                
    c.execute('''CREATE TABLE IF NOT EXISTS projects (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT,
                    description TEXT,
                    owner_id INTEGER,
                    FOREIGN KEY (owner_id) REFERENCES users(id)
                )''')
                
    c.execute('''CREATE TABLE IF NOT EXISTS project_members (
                    project_id INTEGER,
                    user_email TEXT,
                    PRIMARY KEY (project_id, user_email),
                    FOREIGN KEY (project_id) REFERENCES projects(id)
                )''')
                
    c.execute('''CREATE TABLE IF NOT EXISTS tasks (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER,
                    title TEXT,
                    description TEXT,
                    priority TEXT,
                    status TEXT DEFAULT 'To Do',
                    due_date TEXT,
                    assignee TEXT,
                    FOREIGN KEY (user_id) REFERENCES users(id)
                )''')
    
    # Migrations
    try:
        c.execute('ALTER TABLE tasks ADD COLUMN completed_date TEXT')
    except sqlite3.OperationalError:
        pass
        
    try:
        c.execute('ALTER TABLE tasks ADD COLUMN project_id INTEGER REFERENCES projects(id)')
    except sqlite3.OperationalError:
        pass
        
    # Handle orphaned tasks (data migration)
    c.execute('SELECT id, user_id, assignee FROM tasks WHERE project_id IS NULL')
    orphans = c.fetchall()
    
    if orphans:
        # Create a default project for the first user
        owner_id = orphans[0][1]
        c.execute('SELECT email FROM users WHERE id = ?', (owner_id,))
        user_row = c.fetchone()
        owner_email = user_row[0] if user_row else "unknown@example.com"
        
        c.execute('INSERT INTO projects (name, description, owner_id) VALUES (?, ?, ?)', 
                  ("Personal Workspace", "Default workspace for existing tasks", owner_id))
        default_proj_id = c.lastrowid
        
        c.execute('INSERT OR IGNORE INTO project_members (project_id, user_email) VALUES (?, ?)', 
                  (default_proj_id, owner_email))
                  
        for t in orphans:
            c.execute('UPDATE tasks SET project_id = ? WHERE id = ?', (default_proj_id, t[0]))
            
            # Make sure assignee is in the project
            if t[2]:
                c.execute('INSERT OR IGNORE INTO project_members (project_id, user_email) VALUES (?, ?)', 
                          (default_proj_id, t[2]))
        
    conn.commit()
    conn.close()

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def register_user(email, password):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    try:
        c.execute('INSERT INTO users (email, password) VALUES (?, ?)', (email, hash_password(password)))
        conn.commit()
        user_id = c.lastrowid
        return True, user_id
    except sqlite3.IntegrityError:
        return False, "Email already registered."
    finally:
        conn.close()

def authenticate_user(email, password):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute('SELECT id, password FROM users WHERE email = ?', (email,))
    user = c.fetchone()
    conn.close()
    if user and user[1] == hash_password(password):
        return True, user[0]
    return False, "Invalid email or password."

def get_all_users():
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute('SELECT email FROM users')
    users = c.fetchall()
    conn.close()
    return [u[0] for u in users]

# --- PROJECT METHODS ---

def create_project(name, description, owner_id, owner_email):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute('INSERT INTO projects (name, description, owner_id) VALUES (?, ?, ?)', (name, description, owner_id))
    proj_id = c.lastrowid
    # Owner is automatically a member
    c.execute('INSERT INTO project_members (project_id, user_email) VALUES (?, ?)', (proj_id, owner_email))
    conn.commit()
    conn.close()
    return proj_id

def add_member_to_project(project_id, user_email):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    try:
        c.execute('INSERT INTO project_members (project_id, user_email) VALUES (?, ?)', (project_id, user_email))
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        return False
    finally:
        conn.close()

def get_user_projects(user_email):
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    # Fetch projects where user is owner or member
    c.execute('''
        SELECT DISTINCT p.* FROM projects p
        LEFT JOIN project_members pm ON p.id = pm.project_id
        WHERE p.owner_id = (SELECT id FROM users WHERE email = ?) OR pm.user_email = ?
    ''', (user_email, user_email))
    projects = c.fetchall()
    conn.close()
    return [dict(p) for p in projects]

def get_or_create_classroom_project(owner_id, owner_email):
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    
    # Check if it exists for this user
    c.execute('SELECT id FROM projects WHERE owner_id = ? AND name = ?', (owner_id, 'Google Classroom'))
    proj = c.fetchone()
    
    if proj:
        conn.close()
        return proj['id']
        
    # Create it
    c.execute('INSERT INTO projects (name, description, owner_id) VALUES (?, ?, ?)', ('Google Classroom', 'Automatically synced coursework assignments.', owner_id))
    proj_id = c.lastrowid
    c.execute('INSERT INTO project_members (project_id, user_email) VALUES (?, ?)', (proj_id, owner_email))
    conn.commit()
    conn.close()
    return proj_id

def get_project_members(project_id):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute('SELECT user_email FROM project_members WHERE project_id = ?', (project_id,))
    members = c.fetchall()
    conn.close()
    return [m[0] for m in members]

# --- TASK METHODS ---

def add_task(user_id, title, desc, priority, status, due_date, assignee, project_id):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    comp_date = date.today().isoformat() if status == 'Completed' else None
    c.execute('INSERT INTO tasks (user_id, title, description, priority, status, due_date, assignee, completed_date, project_id) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)',
              (user_id, title, desc, priority, status, due_date, assignee, comp_date, project_id))
    conn.commit()
    conn.close()

def get_tasks(user_id, user_email):
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    
    # We want to fetch tasks that belong to projects the user is a member of.
    c.execute('''
        SELECT t.*, p.name as project_name 
        FROM tasks t
        LEFT JOIN projects p ON t.project_id = p.id
        LEFT JOIN project_members pm ON p.id = pm.project_id
        WHERE p.owner_id = ? OR pm.user_email = ?
        ORDER BY t.due_date ASC
    ''', (user_id, user_email))
    
    # Also fetch tasks where project_id IS NULL just in case, but they should be migrated
    tasks = c.fetchall()
    
    # Remove duplicates because LEFT JOIN on project_members can return multiple rows if multiple members exist
    # Wait, the WHERE clause filters it down, but if user is owner AND member, it could duplicate?
    # Actually, let's just do a clean IN query
    c.execute('''
        SELECT t.*, p.name as project_name 
        FROM tasks t
        LEFT JOIN projects p ON t.project_id = p.id
        WHERE t.project_id IN (
            SELECT project_id FROM project_members WHERE user_email = ?
        ) OR t.project_id IN (
            SELECT id FROM projects WHERE owner_id = ?
        )
        ORDER BY t.due_date ASC
    ''', (user_email, user_id))
    tasks = c.fetchall()
    
    conn.close()
    return [dict(t) for t in tasks]

def get_project_tasks(project_id):
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    c.execute('SELECT * FROM tasks WHERE project_id = ?', (project_id,))
    tasks = c.fetchall()
    conn.close()
    return [dict(t) for t in tasks]

def update_task_status(task_id, new_status):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    comp_date = date.today().isoformat() if new_status == 'Completed' else None
    c.execute('UPDATE tasks SET status = ?, completed_date = ? WHERE id = ?', (new_status, comp_date, task_id))
    conn.commit()
    conn.close()

def delete_task(task_id):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute('DELETE FROM tasks WHERE id = ?', (task_id,))
    conn.commit()
    conn.close()
