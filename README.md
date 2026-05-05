# TaskFlow: Task Planning & Progress Tracking System 🌊

![Python](https://img.shields.io/badge/Python-3.11+-blue.svg)
![Streamlit](https://img.shields.io/badge/Streamlit-Framework-FF4B4B.svg)
![SQLite](https://img.shields.io/badge/SQLite-Database-003B57.svg)
![Status](https://img.shields.io/badge/Status-Completed-success.svg)

TaskFlow is a premium, modern SaaS-style productivity application built entirely in Python using Streamlit. Designed with a strict focus on high-fidelity UI/UX, the application provides a robust suite of tools to manage projects, track deadlines, and visualize personal productivity.

This project was developed for the **Software Engineering and Project Management (SEPM)** curriculum.

---

## ✨ Core Features

### 🔐 Secure Authentication System
- Real-time user registration and login functionality.
- Passwords are securely hashed using **SHA-256** encryption before being stored in the database.
- Multi-user support: Users only have access to their own tasks via strict Foreign Key relations.

### 📊 Advanced Dashboard & Analytics
- **Live Metrics**: Automatically calculates Total Tasks, In Progress, Completed, and an overall Productivity Percentage.
- **Weekly Productivity Trend**: A dynamic line chart that plots historical task completion rates over the last 7 days.
- **Smart Insights**: Contextual alerts that automatically warn you if you have tasks due today or tasks that are overdue.

### 📋 Interactive Kanban Board
- A structured 3-column layout (**To Do**, **In Progress**, **Completed**).
- **1-Click Actions**: Simulated drag-and-drop workflow allows users to move tasks between stages instantly with a single button click.
- **Smart Overdue Feedback**: Tasks with a missed deadline automatically glow with a red border and display an `⚠️ Overdue` badge.

### 📅 Calendar Timeline View
- All active tasks are automatically grouped and sorted chronologically by their exact due date, providing a clear visual timeline of upcoming deadlines.

### 🎨 Premium UI/UX & Theme System
- Complete overhaul of default Streamlit styles using injected Custom CSS.
- Features glassmorphism, gradient text, micro-animations, and custom hover states.
- **Dynamic Theme Engine**: Includes a toggle to instantly switch the entire app between a Deep Dark Mode and a Crisp Light Mode using CSS Variables.

---

## 🛠️ Technology Stack

- **Frontend & Routing**: Streamlit (`st.html`, native containers, custom CSS injection)
- **Backend Logic**: Python 3
- **Database**: SQLite3 (Local persistent `.db` file)
- **Security**: Python `hashlib` (SHA-256)
- **Data Manipulation**: Pandas (for generating timeline analytics)

---

## 🚀 Installation & Setup

1. **Clone the Repository**
   ```bash
   git clone https://github.com/kuriant560/Task-Planning-and-Progress-Tracking-System.git
   cd Task-Planning-and-Progress-Tracking-System
   ```

2. **Create a Virtual Environment**
   ```bash
   python3 -m venv .venv
   source .venv/bin/activate  # On Windows use: .venv\Scripts\activate
   ```

3. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Run the Application**
   ```bash
   streamlit run app.py
   ```
   *The application will automatically initialize the `task_planner.db` SQLite database on its first run.*

---

## 📂 Project Structure

- `app.py`: The main entry point containing all Streamlit routing, UI views, and custom CSS injection.
- `database.py`: Modularized backend handling all SQLite connection logic, migrations, and CRUD operations.
- `seed.py`: A helper script designed to instantly populate the database with realistic sample data for testing and presentations.
- `task_planner.db`: The persistent SQLite database (auto-generated upon running).

---

## 💡 Usage Example

1. **Register**: Create a new account on the login page.
2. **Add a Task**: Navigate to "Add Task", set a title, priority, and select a due date in the past.
3. **See Smart Features**: Visit the Dashboard to see the automated Overdue alert, and visit the Tasks page to see the card glowing red.
4. **Complete a Task**: Click the `[→ Completed]` button on a card and watch your Dashboard Productivity Trend chart instantly react!
