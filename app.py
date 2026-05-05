import streamlit as st
import datetime
import pandas as pd
from database import init_db, register_user, authenticate_user, add_task, get_tasks, update_task_status, delete_task

# --- PAGE CONFIGURATION ---
st.set_page_config(
    page_title="TaskFlow Premium",
    page_icon="🌊",
    layout="wide",
    initial_sidebar_state="expanded"
)

def render_html(html_str):
    st.html(html_str)

# --- CUSTOM CSS WITH THEME SYSTEM ---
def inject_custom_css():
    is_light = st.session_state.get('theme_toggle', False)
    
    bg_color = "#F9FAFB" if is_light else "#0B0B12"
    card_bg = "#FFFFFF" if is_light else "#12121A"
    card_alt = "#F3F4F6" if is_light else "#161622"
    border_color = "rgba(0,0,0,0.1)" if is_light else "rgba(255,255,255,0.05)"
    border_hover = "rgba(0,0,0,0.2)" if is_light else "rgba(255,255,255,0.1)"
    text_color = "#111827" if is_light else "#FFFFFF"
    text_muted = "#6B7280" if is_light else "#9CA3AF"
    btn_hover_bg = "rgba(0,0,0,0.05)" if is_light else "rgba(255,255,255,0.05)"
    
    render_html(f"""
        <style>
        :root {{
            --bg-color: {bg_color};
            --card-bg: {card_bg};
            --card-alt: {card_alt};
            --border-color: {border_color};
            --border-hover: {border_hover};
            --text-color: {text_color};
            --text-muted: {text_muted};
            --btn-hover-bg: {btn_hover_bg};
        }}
        
        /* Base Theme */
        .stApp {{
            background-color: var(--bg-color) !important;
            font-family: 'Inter', 'Roboto', sans-serif !important;
            color: var(--text-color) !important;
            -webkit-font-smoothing: antialiased;
        }}
        
        h1, h2, h3, h4, h5, h6, .stMarkdown p {{ color: var(--text-color) !important; letter-spacing: -0.01em; }}
        p {{ color: var(--text-muted) !important; }}
        
        /* Hide right-side Streamlit menu but keep the top bar for sidebar toggle */
        header[data-testid="stHeader"] {{
            background-color: transparent !important;
        }}
        [data-testid="stToolbar"] {{visibility: hidden !important;}}
        footer {{visibility: hidden;}}
        
        /* Force sidebar toggle visibility and color */
        [data-testid="collapsedControl"] {{
            display: flex !important;
            visibility: visible !important;
            color: #A855F7 !important;
            background-color: var(--card-bg) !important;
            border: 1px solid var(--border-color) !important;
            border-radius: 8px !important;
            padding: 0.5rem !important;
            margin: 1rem !important;
            z-index: 999999 !important;
        }}
        [data-testid="collapsedControl"] svg {{
            fill: #A855F7 !important;
            stroke: #A855F7 !important;
            color: #A855F7 !important;
        }}
        
        .block-container {{ padding-top: 3.5rem !important; }}
        
        /* --- SIDEBAR --- */
        [data-testid="stSidebar"] {{
            background-color: var(--bg-color) !important;
            border-right: 1px solid var(--border-color) !important;
            padding-top: 1rem;
        }}
        
        .brand-text {{
            background: linear-gradient(90deg, #A855F7 0%, #EC4899 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            font-size: 1.5rem;
            font-weight: 700;
            margin-bottom: 2rem;
            padding-left: 1rem;
            letter-spacing: -0.02em;
        }}
        
        [data-testid="stSidebar"] .stButton > button[kind="primary"] {{
            background: linear-gradient(90deg, #A855F7 0%, #EC4899 100%) !important;
            color: #FFFFFF !important;
            border: none !important;
            box-shadow: 0 4px 15px -3px rgba(168, 85, 247, 0.4) !important;
            justify-content: flex-start !important;
            padding: 0.75rem 1rem !important;
            border-radius: 12px !important;
            font-weight: 600 !important;
        }}
        [data-testid="stSidebar"] .stButton > button[kind="secondary"] {{
            background-color: transparent !important;
            color: var(--text-muted) !important;
            border: none !important;
            box-shadow: none !important;
            justify-content: flex-start !important;
            padding: 0.75rem 1rem !important;
            border-radius: 12px !important;
            font-weight: 500 !important;
            transition: all 0.3s ease;
        }}
        [data-testid="stSidebar"] .stButton > button[kind="secondary"]:hover {{
            color: var(--text-color) !important;
            background-color: var(--btn-hover-bg) !important;
        }}

        .profile-block {{
            background-color: var(--card-bg);
            border-radius: 12px;
            padding: 0.75rem;
            display: flex;
            align-items: center;
            gap: 10px;
            margin-top: auto;
            border: 1px solid var(--border-color);
            transition: all 0.3s ease;
        }}
        .profile-block:hover {{ border-color: var(--border-hover); }}
        .avatar-circle {{
            width: 32px; height: 32px; border-radius: 50%;
            background: linear-gradient(135deg, #A855F7, #EC4899);
            display: flex; align-items: center; justify-content: center;
            font-weight: bold; font-size: 12px; color: white;
            box-shadow: 0 2px 10px rgba(168, 85, 247, 0.5);
        }}
        .profile-info {{ display: flex; flex-direction: column; line-height: 1.2; }}
        .profile-name {{ font-size: 14px; font-weight: 600; color: var(--text-color);}}
        .profile-email {{ font-size: 12px; color: var(--text-muted); overflow: hidden; text-overflow: ellipsis; max-width: 150px;}}
        
        /* --- MAIN CONTENT BLOCKS --- */
        
        .login-title {{
            text-align: center; font-size: 2.5rem; font-weight: 700;
            background: linear-gradient(90deg, #A855F7 0%, #EC4899 100%);
            -webkit-background-clip: text; -webkit-text-fill-color: transparent;
            margin-bottom: 0.5rem; letter-spacing: -0.02em;
        }}
        
        .dark-card {{
            background-color: var(--card-bg);
            border: 1px solid var(--border-color);
            border-radius: 16px;
            padding: 1.5rem;
            margin-bottom: 1rem;
            transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        }}
        
        [data-testid="stVerticalBlockBorderWrapper"] {{
            background-color: var(--card-bg) !important;
            border: 1px solid var(--border-color) !important;
            border-radius: 16px !important;
            transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
            padding: 0.5rem !important;
        }}
        [data-testid="stVerticalBlockBorderWrapper"]:hover {{
            transform: translateY(-2px);
            box-shadow: 0 10px 25px -5px rgba(0,0,0,0.15);
            border-color: var(--border-hover) !important;
        }}
        
        .overdue-card [data-testid="stVerticalBlockBorderWrapper"] {{
            border-color: rgba(239, 68, 68, 0.5) !important;
            box-shadow: 0 0 15px rgba(239, 68, 68, 0.2) !important;
        }}
        
        .metric-card {{
            background-color: var(--card-bg);
            border: 1px solid var(--border-color);
            border-radius: 16px; padding: 1.25rem;
            display: flex; flex-direction: column; justify-content: space-between; height: 100%;
            transition: all 0.3s ease;
        }}
        .metric-card:hover {{ transform: translateY(-2px); border-color: var(--border-hover); }}
        .metric-icon {{
            width: 40px; height: 40px; border-radius: 10px;
            display: flex; align-items: center; justify-content: center; margin-bottom: 1rem;
        }}
        .metric-value {{ font-size: 2.25rem; font-weight: 800; color: var(--text-color); margin-bottom: 0.25rem; letter-spacing: -0.05em;}}
        .metric-label {{ font-size: 0.875rem; color: var(--text-muted); }}
        
        @keyframes fillBar {{ from {{ width: 0%; opacity: 0; }} to {{ opacity: 1; }} }}
        .progress-bar-container {{
            width: 100%; height: 8px; background-color: var(--card-alt);
            border-radius: 999px; margin-top: 1rem; margin-bottom: 1rem; overflow: hidden;
        }}
        .progress-bar-fill {{
            height: 100%; background: linear-gradient(90deg, #A855F7 0%, #EC4899 100%);
            border-radius: 999px; box-shadow: 0 0 10px rgba(236, 72, 153, 0.5);
            animation: fillBar 1s cubic-bezier(0.4, 0, 0.2, 1) forwards;
        }}
        
        .task-badge {{
            font-size: 0.75rem; padding: 0.25rem 0.75rem; border-radius: 999px;
            font-weight: 500; border: 1px solid var(--border-color);
            background-color: var(--btn-hover-bg); backdrop-filter: blur(4px);
        }}
        .badge-progress {{ color: #3B82F6; border-color: rgba(59, 130, 246, 0.3); background-color: rgba(59, 130, 246, 0.1);}}
        .badge-completed {{ color: #10B981; border-color: rgba(16, 185, 129, 0.3); background-color: rgba(16, 185, 129, 0.1);}}
        .badge-todo {{ color: #A855F7; border-color: rgba(168, 85, 247, 0.3); background-color: rgba(168, 85, 247, 0.1);}}
        .badge-high {{ color: #EF4444; border-color: rgba(239, 68, 68, 0.3); background-color: rgba(239, 68, 68, 0.1);}}
        .badge-medium {{ color: #F59E0B; border-color: rgba(245, 158, 11, 0.3); background-color: rgba(245, 158, 11, 0.1);}}
        .badge-low {{ color: #3B82F6; border-color: rgba(59, 130, 246, 0.3); background-color: rgba(59, 130, 246, 0.1);}}
        .badge-overdue {{ color: #EF4444; font-weight: bold; }}
        
        .stButton > button[kind="primary"] {{
            background: linear-gradient(90deg, #A855F7 0%, #EC4899 100%) !important;
            color: white !important; border: none !important; border-radius: 8px !important; font-weight: 600 !important;
            transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1) !important;
            box-shadow: 0 4px 15px -3px rgba(168, 85, 247, 0.4) !important;
        }}
        .stButton > button[kind="primary"]:hover {{
            box-shadow: 0 8px 25px -5px rgba(168, 85, 247, 0.6) !important;
            transform: translateY(-1px) !important;
        }}
        .stButton > button[kind="primary"]:active {{ transform: scale(0.97) !important; }}
        
        .stButton > button[kind="secondary"] {{
            background-color: var(--btn-hover-bg) !important;
            color: var(--text-color) !important; border: 1px solid var(--border-hover) !important;
            border-radius: 8px !important; transition: all 0.2s ease !important;
        }}
        .stButton > button[kind="secondary"]:hover {{
            background-color: var(--border-color) !important; border-color: var(--border-hover) !important;
        }}
        .stButton > button[kind="secondary"]:active {{ transform: scale(0.97) !important; }}

        .stTextInput > div > div > input, .stSelectbox > div > div > select,
        .stDateInput > div > div > input, .stTextArea > div > div > textarea {{
            background-color: var(--card-alt) !important; border: 1px solid var(--border-color) !important;
            color: var(--text-color) !important; border-radius: 8px !important; transition: all 0.3s ease; padding: 0.75rem !important;
        }}
        .stTextInput > div > div > input:focus, .stSelectbox > div > div > select:focus,
        .stTextArea > div > div > textarea:focus {{ border-color: #A855F7 !important; box-shadow: 0 0 0 1px #A855F7 !important; }}
        
        .back-btn-col .stButton > button {{
            background: transparent !important; border: 1px solid var(--border-color) !important; color: var(--text-muted) !important;
            padding: 0.25rem 0.75rem !important; border-radius: 999px !important; font-size: 0.875rem !important; font-weight: 500 !important;
            display: inline-flex; align-items: center; justify-content: center;
        }}
        .back-btn-col .stButton > button:hover {{
            color: var(--text-color) !important; border-color: var(--border-hover) !important; background-color: var(--btn-hover-bg) !important;
        }}
        </style>
    """)

# --- NAVIGATION HISTORY ---
def change_page(new_page):
    if 'page_history' not in st.session_state: st.session_state.page_history = []
    if not st.session_state.page_history or st.session_state.page_history[-1] != st.session_state.current_page:
        st.session_state.page_history.append(st.session_state.current_page)
    st.session_state.current_page = new_page
    st.rerun()

def go_back():
    if 'page_history' in st.session_state and st.session_state.page_history:
        st.session_state.current_page = st.session_state.page_history.pop()
        st.rerun()

def render_back_button():
    if 'page_history' in st.session_state and len(st.session_state.page_history) > 0:
        render_html('<div class="back-btn-col">')
        if st.button("← Go Back", key="back_btn"): go_back()
        render_html('</div>')
        st.markdown("<br>", unsafe_allow_html=True)

# --- SESSION STATE INITIALIZATION ---
def init_session_state():
    if 'logged_in' not in st.session_state: st.session_state.logged_in = False
    if 'current_page' not in st.session_state: st.session_state.current_page = 'Dashboard'
    if 'page_history' not in st.session_state: st.session_state.page_history = []
    if 'auth_mode' not in st.session_state: st.session_state.auth_mode = 'login'
    
    # Force logout if hot-reload corrupted the session
    if st.session_state.logged_in and ('user_email' not in st.session_state or 'user_id' not in st.session_state):
        st.session_state.logged_in = False

# --- VIEWS ---
def auth_view():
    st.markdown("<br><br>", unsafe_allow_html=True)
    is_login = st.session_state.auth_mode == 'login'
    title = "Welcome Back" if is_login else "Create Account"
    subtitle = "Sign in to continue to TaskFlow" if is_login else "Join TaskFlow to manage your projects"
    
    render_html(f"<div class='login-title'>{title}</div><p style='text-align: center; margin-bottom: 3rem;'>{subtitle}</p>")
    
    col1, col2, col3 = st.columns([1, 1.5, 1])
    with col2:
        with st.container(border=True):
            st.markdown("<br>", unsafe_allow_html=True)
            email = st.text_input("Email Address", value="" if not is_login else "test@example.com")
            password = st.text_input("Password", type="password")
            if is_login:
                c_left, c_right = st.columns(2)
                with c_left: st.checkbox("Remember me")
                with c_right: render_html("<div style='text-align: right; color: #A855F7; font-size: 0.875rem; padding-top: 0.5rem; cursor: pointer;'>Forgot password?</div>")
            st.markdown("<br>", unsafe_allow_html=True)
            
            if st.button("Sign In →" if is_login else "Sign Up →", use_container_width=True, type="primary"):
                if not email or not password:
                    st.error("Please fill in all fields.")
                else:
                    if is_login:
                        success, res = authenticate_user(email, password)
                        if success:
                            st.session_state.logged_in = True
                            st.session_state.user_id = res
                            st.session_state.user_email = email
                            st.rerun()
                        else: st.error(res)
                    else:
                        success, res = register_user(email, password)
                        if success:
                            st.success("Registration successful! Logging you in...")
                            st.session_state.logged_in = True
                            st.session_state.user_id = res
                            st.session_state.user_email = email
                            st.rerun()
                        else: st.error(res)
            
            toggle_text = "Don't have an account?" if is_login else "Already have an account?"
            toggle_link = "Sign up for free" if is_login else "Sign in"
            col_t1, col_t2, col_t3 = st.columns([1, 2, 1])
            with col_t2:
                if st.button(f"{toggle_text} {toggle_link}", use_container_width=True, key="toggle_auth"):
                    st.session_state.auth_mode = 'register' if is_login else 'login'
                    st.rerun()
        render_html("<div style='text-align: center; margin-top: 2.5rem; font-size: 0.75rem; color: #6B7280;'>By continuing, you agree to our <span style='color: #A855F7;'>Terms</span> and <span style='color: #A855F7;'>Privacy Policy</span></div>")

def render_sidebar():
    with st.sidebar:
        render_html('<div class="brand-text">TaskFlow</div>')
        pages = [("Dashboard 📊", "Dashboard"), ("Tasks ✅", "Tasks"), ("Calendar 📅", "Calendar"), ("Projects 📁", "Projects")]
        for display_name, internal_name in pages:
            btn_type = "primary" if st.session_state.current_page == internal_name else "secondary"
            if st.button(display_name, key=f"nav_{internal_name}", use_container_width=True, type=btn_type):
                change_page(internal_name)
                
        render_html("<br>" * 5)
        email_prefix = st.session_state.user_email.split('@')[0].capitalize()
        render_html(f"""
            <div class="profile-block">
                <div class="avatar-circle">{email_prefix[:2].upper()}</div>
                <div class="profile-info">
                    <span class="profile-name">{email_prefix}</span>
                    <span class="profile-email">{st.session_state.user_email}</span>
                </div>
            </div>
        """)
        if st.button("Log out", key="logout_btn", use_container_width=True):
            st.session_state.clear()
            st.rerun()

def get_status_badge(status):
    c = "badge-todo" if status == 'To Do' else "badge-progress" if status == 'In Progress' else "badge-completed"
    return f'<span class="task-badge {c}">○ {status}</span>'

def get_priority_badge(priority):
    c = "badge-high" if priority == 'High' else "badge-medium" if priority == 'Medium' else "badge-low"
    return f'<span class="task-badge {c}">{priority}</span>'

def check_overdue(due_date_str, status):
    if status == 'Completed' or not due_date_str: return False
    try:
        return datetime.datetime.strptime(due_date_str, "%Y-%m-%d").date() < datetime.date.today()
    except:
        return False

def dashboard_view():
    tasks = get_tasks(st.session_state.user_id)
    today = datetime.date.today()
    
    overdue_count = sum(1 for t in tasks if check_overdue(t['due_date'], t['status']))
    due_today_count = sum(1 for t in tasks if t['due_date'] == today.strftime("%Y-%m-%d") and t['status'] != 'Completed')
    
    if overdue_count > 0:
        st.error(f"🔴 Smart Insight: You have {overdue_count} overdue task(s). Prioritize them!")
    if due_today_count > 0:
        st.warning(f"🟡 Smart Insight: You have {due_today_count} task(s) due today.")
    
    email_prefix = st.session_state.user_email.split('@')[0].capitalize()
    render_html(f"<h2>Hello, {email_prefix} 👋</h2><p style='margin-bottom: 2rem;'>Here's what's happening with your projects today.</p>")
    
    total = len(tasks)
    in_prog = sum(1 for t in tasks if t['status'] == 'In Progress')
    comp = sum(1 for t in tasks if t['status'] == 'Completed')
    todo = total - in_prog - comp
    pct = int((comp / total * 100)) if total > 0 else 0
    
    c1, c2, c3, c4 = st.columns(4)
    for col, m in zip([c1, c2, c3, c4], [
        {"val": str(total), "lbl": "Total Tasks", "bg": "rgba(168, 85, 247, 0.1)", "c": "#A855F7"},
        {"val": str(in_prog), "lbl": "In Progress", "bg": "rgba(59, 130, 246, 0.1)", "c": "#3B82F6"},
        {"val": str(comp), "lbl": "Completed", "bg": "rgba(16, 185, 129, 0.1)", "c": "#10B981"},
        {"val": f"{pct}%", "lbl": "Productivity", "bg": "rgba(236, 72, 153, 0.1)", "c": "#EC4899"}
    ]):
        with col:
            render_html(f"<div class='metric-card'><div class='metric-icon' style='background-color: {m['bg']}; color: {m['c']};'>◓</div><div><div class='metric-value'>{m['val']}</div><div class='metric-label'>{m['lbl']}</div></div></div>")
            
    # Chart Row
    col_prog, col_chart = st.columns([1, 1])
    with col_prog:
        render_html(f"""
            <div class="dark-card" style="margin-top: 1rem; height: 100%;">
                <div style="display: flex; justify-content: space-between;">
                    <div><h4 style="margin: 0;">Overall Progress</h4><p style="font-size: 0.875rem; margin-top: 0.25rem;">{comp} of {total} tasks completed</p></div>
                    <div style="font-size: 1.5rem; font-weight: 700; color: #EC4899;">{pct}%</div>
                </div>
                <div class="progress-bar-container"><div class="progress-bar-fill" style="width: {pct}%;"></div></div>
                <div style="display: flex; gap: 1rem; margin-top: 1rem;">
                    <div style="flex: 1; background: var(--card-alt); padding: 1rem; border-radius: 8px; text-align: center;"><div style="color: #10B981; font-weight: bold; font-size: 1.25rem;">{comp}</div><div style="font-size: 0.75rem; color: var(--text-muted);">Completed</div></div>
                    <div style="flex: 1; background: var(--card-alt); padding: 1rem; border-radius: 8px; text-align: center;"><div style="color: #3B82F6; font-weight: bold; font-size: 1.25rem;">{in_prog}</div><div style="font-size: 0.75rem; color: var(--text-muted);">In Progress</div></div>
                    <div style="flex: 1; background: var(--card-alt); padding: 1rem; border-radius: 8px; text-align: center;"><div style="color: var(--text-muted); font-weight: bold; font-size: 1.25rem;">{todo}</div><div style="font-size: 0.75rem; color: var(--text-muted);">To Do</div></div>
                </div>
            </div>
        """)
    with col_chart:
        st.markdown("#### Weekly Productivity Trend")
        df_tasks = pd.DataFrame(tasks)
        if not df_tasks.empty and 'completed_date' in df_tasks.columns:
            comp_tasks = df_tasks[df_tasks['status'] == 'Completed'].copy()
            if not comp_tasks.empty:
                comp_tasks['completed_date'] = pd.to_datetime(comp_tasks['completed_date']).dt.date
                last_7_days = [(today - datetime.timedelta(days=i)) for i in range(6, -1, -1)]
                counts = [len(comp_tasks[comp_tasks['completed_date'] == d]) for d in last_7_days]
                chart_data = pd.DataFrame({"Completed": counts}, index=[d.strftime("%b %d") for d in last_7_days])
                st.line_chart(chart_data)
            else:
                st.info("Complete some tasks to see your productivity trend!")
        else:
            st.info("Complete some tasks to see your productivity trend!")

def render_task_card(task):
    is_overdue = check_overdue(task['due_date'], task['status'])
    overdue_class = "overdue-card" if is_overdue else ""
    
    render_html(f"<div class='{overdue_class}'>")
    with st.container(border=True):
        badge = get_priority_badge(task['priority'])
        overdue_badge = f'<span class="task-badge badge-overdue" style="margin-left: 0.5rem;">⚠️ Overdue</span>' if is_overdue else ''
        
        render_html(f"""
            <div style="display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 0.5rem;">
                <div style="font-weight: 600; font-size: 1.1rem; color: var(--text-color); word-break: break-word;">{task['title']}</div>
            </div>
            <div style="margin-bottom: 0.75rem;">{badge}{overdue_badge}</div>
            <div style="font-size: 0.875rem; color: var(--text-muted); margin-bottom: 1rem; line-height: 1.5; overflow: hidden; text-overflow: ellipsis; display: -webkit-box; -webkit-line-clamp: 2; -webkit-box-orient: vertical;">{task['description']}</div>
            <div style="margin-bottom: 0.5rem; font-size: 0.875rem; color: var(--text-muted);">📅 {task['due_date']}</div>
        """)
        
        c1, c2 = st.columns(2)
        with c1:
            if task['status'] == 'To Do':
                if st.button("→ In Progress", key=f"prog_{task['id']}", use_container_width=True):
                    update_task_status(task['id'], 'In Progress')
                    st.rerun()
            elif task['status'] == 'In Progress':
                if st.button("→ Completed", key=f"comp_{task['id']}", use_container_width=True):
                    update_task_status(task['id'], 'Completed')
                    st.rerun()
            elif task['status'] == 'Completed':
                if st.button("↺ Reopen", key=f"reopen_{task['id']}", use_container_width=True):
                    update_task_status(task['id'], 'To Do')
                    st.rerun()
        with c2:
            if st.button("Delete", key=f"del_{task['id']}", use_container_width=True):
                delete_task(task['id'])
                st.rerun()
    render_html("</div>")

def tasks_view():
    col1, col2 = st.columns([3, 1])
    with col1:
        render_html("<h2>Tasks Board ✅</h2>")
    with col2:
        render_html("<br>")
        if st.button("➕ Add Task", type="primary", use_container_width=True):
            change_page('Add Task')

    with st.expander("🔍 Filter & Search", expanded=False):
        f1, f2, f3, f4 = st.columns(4)
        with f1: search_q = st.text_input("Search Title")
        with f2: filter_prio = st.selectbox("Priority", ["All", "High", "Medium", "Low"])
        with f3: filter_stat = st.selectbox("Status", ["All", "To Do", "In Progress", "Completed"])
        with f4: filter_overdue = st.checkbox("Overdue Only")

    tasks = get_tasks(st.session_state.user_id)
    
    # Apply filters
    if search_q: tasks = [t for t in tasks if search_q.lower() in t['title'].lower()]
    if filter_prio != "All": tasks = [t for t in tasks if t['priority'] == filter_prio]
    if filter_stat != "All": tasks = [t for t in tasks if t['status'] == filter_stat]
    if filter_overdue: tasks = [t for t in tasks if check_overdue(t['due_date'], t['status'])]
    
    todo = [t for t in tasks if t['status'] == 'To Do']
    inprogress = [t for t in tasks if t['status'] == 'In Progress']
    completed = [t for t in tasks if t['status'] == 'Completed']
    
    st.markdown("<br>", unsafe_allow_html=True)
    c_todo, c_prog, c_comp = st.columns(3)
    
    with c_todo:
        render_html(f"<div style='background: rgba(168, 85, 247, 0.1); color: #A855F7; padding: 0.5rem; border-radius: 8px; font-weight: 600; margin-bottom: 1rem; text-align: center;'>To Do ({len(todo)})</div>")
        for t in todo: render_task_card(t)
    with c_prog:
        render_html(f"<div style='background: rgba(59, 130, 246, 0.1); color: #3B82F6; padding: 0.5rem; border-radius: 8px; font-weight: 600; margin-bottom: 1rem; text-align: center;'>In Progress ({len(inprogress)})</div>")
        for t in inprogress: render_task_card(t)
    with c_comp:
        render_html(f"<div style='background: rgba(16, 185, 129, 0.1); color: #10B981; padding: 0.5rem; border-radius: 8px; font-weight: 600; margin-bottom: 1rem; text-align: center;'>Completed ({len(completed)})</div>")
        for t in completed: render_task_card(t)

def calendar_view():
    render_html("<h2>Calendar 📅</h2><p>View tasks by upcoming deadlines.</p>")
    tasks = get_tasks(st.session_state.user_id)
    active_tasks = [t for t in tasks if t['status'] != 'Completed']
    active_tasks.sort(key=lambda x: x['due_date'])
    
    if not active_tasks:
        st.success("No active tasks! You're all caught up.")
        return
        
    grouped = {}
    for t in active_tasks:
        grouped.setdefault(t['due_date'], []).append(t)
        
    for d_date, d_tasks in grouped.items():
        st.markdown(f"### 📅 {d_date}")
        for t in d_tasks:
            badge = get_priority_badge(t['priority'])
            s_badge = get_status_badge(t['status'])
            render_html(f"""
            <div style="background: var(--card-bg); padding: 1rem; border-radius: 8px; margin-bottom: 0.5rem; border: 1px solid var(--border-color); display: flex; justify-content: space-between;">
                <div><strong>{t['title']}</strong><div style="margin-top:0.25rem;">{badge} {s_badge}</div></div>
            </div>
            """)

def add_task_view():
    render_html("<h2>Create New Task</h2>")
    with st.container(border=True):
        with st.form("add_task_form", border=False):
            t_name = st.text_input("Task Title *", placeholder="e.g., Design new landing page")
            t_desc = st.text_area("Description", placeholder="Provide details about the task...")
            c_p, c_s, c_d = st.columns(3)
            with c_p: t_prio = st.selectbox("Priority", ["Low", "Medium", "High"], index=1)
            with c_s: t_stat = st.selectbox("Initial Status", ["To Do", "In Progress", "Completed"])
            with c_d: t_dead = st.date_input("Due Date *")
            
            c1, c2 = st.columns(2)
            with c1: cancel = st.form_submit_button("Cancel", use_container_width=True)
            with c2: submit = st.form_submit_button("Create Task", type="primary", use_container_width=True)
                
            if submit:
                if not t_name: st.error("Task Title is required.")
                else:
                    add_task(st.session_state.user_id, t_name, t_desc, t_prio, t_stat, t_dead.strftime("%Y-%m-%d"), st.session_state.user_email)
                    st.success("Task added successfully!")
                    change_page('Tasks')
            if cancel: change_page('Tasks')

def projects_view():
    render_html("<h2>Projects 📁</h2><p>Manage your active projects</p>")
    with st.container(border=True):
        for title, pct, color, desc in [("🟣 Website Redesign", "65%", "#A855F7", "Complete UI overhaul"), ("🔵 Mobile App", "42%", "#3B82F6", "iOS and Android apps")]:
            render_html(f"""
            <div style="background: var(--card-alt); padding: 1.5rem; border-radius: 12px; margin-bottom: 1rem; border: 1px solid var(--border-color);">
                <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 0.5rem;">
                    <div><div style="font-weight: 600; font-size: 1.1rem;">{title}</div><div style="font-size: 0.875rem; color: var(--text-muted);">{desc}</div></div>
                    <span style="font-weight: 600; color: {color}; font-size: 1.25rem;">{pct}</span>
                </div>
                <div class="progress-bar-container" style="height: 6px; margin-top: 1rem;"><div class="progress-bar-fill" style="width: {pct}; background: {color};"></div></div>
            </div>
            """)

def main():
    init_db()
    inject_custom_css()
    init_session_state()
    
    if not st.session_state.logged_in: auth_view()
    else:
        render_sidebar()
        render_back_button()
        
        pages = {"Dashboard": dashboard_view, "Tasks": tasks_view, "Add Task": add_task_view, "Calendar": calendar_view, "Projects": projects_view}
        pages.get(st.session_state.current_page, lambda: st.write("Page Not Found"))()

if __name__ == "__main__":
    main()
