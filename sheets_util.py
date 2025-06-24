import streamlit as st
from google.oauth2 import service_account
import gspread
from datetime import datetime

# use correct scopes
SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive"
]

def get_sheet():
    creds = service_account.Credentials.from_service_account_info(
        st.secrets["gcp_service_account"],
        scopes=SCOPES
    )
    client = gspread.authorize(creds)
    sheet = client.open("TodoData").worksheet("Tasks")
    return sheet

def add_task(username, task):
    sheet = get_sheet()
    today = datetime.now().strftime("%Y-%m-%d")
    sheet.append_row([username, today, task, "False"])

def get_user_tasks(username):
    sheet = get_sheet()
    rows = sheet.get_all_records()
    today = datetime.now().strftime("%Y-%m-%d")
    return [r for r in rows if r['username'] == username and r['date'] == today]

def update_task_status(username, task, completed=True):
    sheet = get_sheet()
    rows = sheet.get_all_records()
    today = datetime.now().strftime("%Y-%m-%d")
    for idx, row in enumerate(rows):
        if row["username"] == username and row["task"] == task and row["date"] == today:
            sheet.update_cell(idx + 2, 4, str(completed))
            break
