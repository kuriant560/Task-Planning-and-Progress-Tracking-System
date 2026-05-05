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
    
    # Migration: Add completed_date if it doesn't exist
    try:
        c.execute('ALTER TABLE tasks ADD COLUMN completed_date TEXT')
    except sqlite3.OperationalError:
        pass # Column already exists
        
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

def add_task(user_id, title, desc, priority, status, due_date, assignee):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    comp_date = date.today().isoformat() if status == 'Completed' else None
    c.execute('INSERT INTO tasks (user_id, title, description, priority, status, due_date, assignee, completed_date) VALUES (?, ?, ?, ?, ?, ?, ?, ?)',
              (user_id, title, desc, priority, status, due_date, assignee, comp_date))
    conn.commit()
    conn.close()

def get_tasks(user_id):
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    c.execute('SELECT * FROM tasks WHERE user_id = ? ORDER BY due_date ASC', (user_id,))
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
