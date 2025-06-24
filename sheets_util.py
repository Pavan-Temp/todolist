import gspread
from oauth2client.service_account import ServiceAccountCredentials
from datetime import datetime

SHEET_NAME = "TodoData"  # your spreadsheet name

def get_sheet():
    scope = ['https://spreadsheets.google.com/feeds',
             'https://www.googleapis.com/auth/drive']
    # Use secrets from Streamlit Cloud
    creds = service_account.Credentials.from_service_account_info(
    st.secrets["gcp_service_account"],
    scopes=["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"]
    )
    client = gspread.authorize(creds)
    sheet = client.open(SHEET_NAME).worksheet("Tasks")
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
    for idx, row in enumerate(rows):
        if row["username"] == username and row["task"] == task and row["date"] == datetime.now().strftime("%Y-%m-%d"):
            sheet.update_cell(idx + 2, 4, str(completed))  # completed is column 4
            break
