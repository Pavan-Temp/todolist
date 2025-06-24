import streamlit as st
from datetime import datetime
from db_util import add_task, get_user_tasks, update_task_status, init_db, cleanup_old_tasks
import json

CUTOFF_HOUR = 16  # 3:00 PM cutoff

# Load users
with open("users.json", "r") as f:
    USERS = json.load(f)

# Initialize and clean database
init_db()
cleanup_old_tasks()

# Streamlit config and styling
st.set_page_config(page_title="Smart To-Do", page_icon="📝", layout="centered")

st.markdown("""
    <style>
    .css-1aumxhk, .css-1v0mbdj, .stButton>button {
        background-color: #0072C6;
        color: white;
        font-weight: 600;
        border-radius: 5px;
    }
    .stTextInput>div>div>input {
        padding: 10px;
        border: 1px solid #ddd;
    }

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

# Session state
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
    st.session_state.username = ""

# Login screen
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

# Cutoff time
def is_before_cutoff():
    return datetime.now().hour < CUTOFF_HOUR

# Main To-Do interface
def main_app():
    st.markdown(f"""
        <h2 style='text-align: center;'>📝 Daily To-Do List</h2>
        <h4 style='text-align: center; color: gray;'>Welcome, <span style='color: #0072C6'>{st.session_state.username}</span>!</h4>
        <hr style='border: 1px solid #eee;'>
    """, unsafe_allow_html=True)

    editable = is_before_cutoff()
    tasks = get_user_tasks(st.session_state.username)

    st.markdown("### ✅ Today's Tasks")

    if tasks:
        for task in tasks:
            task_text = task["task"]
            completed = task["completed"] == "True"

            col1, col2 = st.columns([0.08, 0.92])
            with col1:
                checked = st.checkbox("", value=completed, key=task_text)
            with col2:
                styled_text = f"<div class='task-card'><div class='task-text {'task-complete' if checked else ''}'>{task_text}</div></div>"
                st.markdown(styled_text, unsafe_allow_html=True)

            # Update if toggled
            if checked != completed:
                update_task_status(st.session_state.username, task_text, checked)
                st.experimental_rerun()
    else:
        st.info("No tasks added yet for today.")

    st.markdown("---")

    # Task input section
    if editable:
        st.markdown("### ➕ Add New Task")
        with st.form("add_form", clear_on_submit=True):
            new_task = st.text_input("What's on your mind today?")
            submitted = st.form_submit_button("Add Task ✅")
            if submitted and new_task.strip():
                add_task(st.session_state.username, new_task.strip())
                st.experimental_rerun()
    else:
        st.warning("🚫 Adding new tasks is disabled after 3:00 PM.")

    st.markdown("---")
    if st.button("🔒 Logout"):
        st.session_state.logged_in = False
        st.session_state.username = ""
        st.experimental_rerun()

# Launch app
if st.session_state.logged_in:
    main_app()
else:
    login()
