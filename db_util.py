from datetime import datetime, timedelta
import sqlite3

def init_db():
    conn = sqlite3.connect("tasks.db")
    c = conn.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS tasks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL,
            task TEXT NOT NULL,
            completed BOOLEAN NOT NULL DEFAULT 0,
            date TEXT NOT NULL
        )
    """)
    conn.commit()
    conn.close()

def cleanup_old_tasks():
    conn = sqlite3.connect("tasks.db")
    c = conn.cursor()
    cutoff_date = (datetime.now() - timedelta(days=2)).strftime("%Y-%m-%d")
    c.execute("DELETE FROM tasks WHERE date < ?", (cutoff_date,))
    conn.commit()
    conn.close()

def add_task(username, task):
    today = datetime.now().strftime("%Y-%m-%d")
    conn = sqlite3.connect("tasks.db")
    c = conn.cursor()
    c.execute("INSERT INTO tasks (username, task, completed, date) VALUES (?, ?, 0, ?)", (username, task, today))
    conn.commit()
    conn.close()

def get_user_tasks(username):
    today = datetime.now().strftime("%Y-%m-%d")
    conn = sqlite3.connect("tasks.db")
    c = conn.cursor()
    c.execute("SELECT task, completed FROM tasks WHERE username = ? AND date = ?", (username, today))
    rows = c.fetchall()
    conn.close()
    return [{"task": row[0], "completed": str(bool(row[1]))} for row in rows]

def update_task_status(username, task, completed):
    today = datetime.now().strftime("%Y-%m-%d")
    conn = sqlite3.connect("tasks.db")
    c = conn.cursor()
    c.execute("UPDATE tasks SET completed = ? WHERE username = ? AND task = ? AND date = ?", (int(completed), username, task, today))
    conn.commit()
    conn.close()
