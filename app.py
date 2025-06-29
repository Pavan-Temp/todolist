import streamlit as st
from datetime import datetime
from db_util import (
    add_task, get_user_tasks,
    update_task_status, init_db,
    cleanup_old_tasks, delete_task
)
from pytz import timezone
import json

# Cutoff logic: 3 PM (15) to next day 4 AM (4)
def is_within_cutoff():
    ist = timezone("Asia/Kolkata")
    hour = datetime.now(ist).hour
    return hour >= 18 or hour < 4  # 3 PM to 4 AM

# Load users
with open("users.json", "r") as f:
    USERS = json.load(f)
USERS["admin"] = "admin123"  # Admin user

# Initialize DB
init_db()
cleanup_old_tasks()

# Streamlit config and style
st.set_page_config(page_title="Smart To-Do", page_icon="📝", layout="centered")

st.markdown("""
    <style>
    /* Bigger checkboxes */
    div[data-baseweb="checkbox"] > div {
        transform: scale(1.5);
        margin-right: 10px;
    }

    /* Task Card Styles */
    .task-card {
        background-color: rgba(255, 255, 255, 0.05);
        padding: 14px 20px;
        margin-bottom: 12px;
        border-left: 5px solid #00cc66;
        border-radius: 10px;
        box-shadow: 0 2px 6px rgba(0,0,0,0.1);
        transition: all 0.2s ease-in-out;
        color: #fff;
    }
    .task-card:hover {
        background-color: rgba(0, 114, 198, 0.2);
        transform: scale(1.01);
    }
    .task-text {
        font-size: 20px;
        font-weight: 500;
        margin: 0;
    }
    .task-complete {
        text-decoration: line-through;
        opacity: 0.6;
    }
    </style>
""", unsafe_allow_html=True)

# Session defaults
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
    st.session_state.username = ""

# Login UI
def login():
    st.title("Login to To-Do")
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")
    if st.button("Login"):
        if username in USERS and USERS[username] == password:
            st.session_state.logged_in = True
            st.session_state.username = username
            st.experimental_rerun()
        else:
            st.error("Invalid credentials.")

# Main UI
def main_app():
    username = st.session_state.username
    is_admin = username == "admin"
    editable = is_within_cutoff()

    st.markdown(f"""
        <h2 style='text-align: center;'>📝 Daily To-Do List</h2>
        <h4 style='text-align: center; color: gray;'>Welcome, 
        <span style='color: #0072C6'>{username}</span>!</h4>
        <hr style='border: 1px solid #eee;'>
    """, unsafe_allow_html=True)

    tasks = get_user_tasks(None if is_admin else username)

    st.markdown("### ✅ Tasks")
    if tasks:
        for task in tasks:
            task_id = task["id"]
            task_text = task["task"]
            completed = task["completed"] == "True"
            user = task["username"]

            col1, col2, col3 = st.columns([0.08, 0.82, 0.10])
            with col1:
                checked = st.checkbox(" ", value=completed, key=f"cb_{task_id}")
            with col2:
                task_display = f"<div class='task-card'><div class='task-text {'task-complete' if checked else ''}'>{task_text}"
                if is_admin:
                    task_display += f" <span style='color: #888;'>(by {user})</span>"
                task_display += "</div></div>"
                st.markdown(task_display, unsafe_allow_html=True)
            with col3:
                if is_admin and st.button("🗑️", key=f"del_{task_id}"):
                    delete_task(task_id)
                    st.experimental_rerun()

            # Update task status if changed
            if checked != completed:
                update_task_status(user, task_text, checked)
                st.experimental_rerun()
    else:
        st.info("No tasks added yet.")

    st.markdown("---")

    # Add Task
    if editable:
        st.markdown("### ➕ Add New Task")
        with st.form("add_form", clear_on_submit=True):
            new_task = st.text_input("What's on your mind today?")
            submitted = st.form_submit_button("Add Task ✅")
            if submitted and new_task.strip():
                add_task(username, new_task.strip())
                st.experimental_rerun()
    else:
        st.warning("🚫 Task addition allowed only between 6 PM and 4 AM.")

    st.markdown("---")

    # Logout
    if st.button("🔒 Logout"):
        st.session_state.logged_in = False
        st.session_state.username = ""
        st.experimental_rerun()

# Run
if st.session_state.logged_in:
    main_app()
else:
    login()
