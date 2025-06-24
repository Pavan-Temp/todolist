import sqlite3
from datetime import datetime, timedelta

DB_NAME = "todo.db"

def init_db():
    with sqlite3.connect(DB_NAME) as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS tasks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT NOT NULL,
                task TEXT NOT NULL,
                completed TEXT NOT NULL,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        """)
        conn.commit()

def add_task(username, task):
    with sqlite3.connect(DB_NAME) as conn:
        conn.execute("INSERT INTO tasks (username, task, completed) VALUES (?, ?, ?)", (username, task, "False"))
        conn.commit()

def get_user_tasks(username):
    with sqlite3.connect(DB_NAME) as conn:
        cur = conn.cursor()
        if username == "admin":
            cur.execute("SELECT id, username, task, completed, timestamp FROM tasks")
        else:
            cur.execute("SELECT id, username, task, completed, timestamp FROM tasks WHERE username = ?", (username,))
        rows = cur.fetchall()
        return [
            {
                "id": row[0],
                "username": row[1],
                "task": row[2],
                "completed": row[3],
                "timestamp": row[4]
            }
            for row in rows
        ]

def update_task_status(username, task, completed):
    with sqlite3.connect(DB_NAME) as conn:
        conn.execute(
            "UPDATE tasks SET completed = ?, timestamp = CURRENT_TIMESTAMP WHERE username = ? AND task = ?",
            (str(completed), username, task)
        )
        conn.commit()

def delete_task(task_id):
    with sqlite3.connect(DB_NAME) as conn:
        conn.execute("DELETE FROM tasks WHERE id = ?", (task_id,))
        conn.commit()

def cleanup_old_tasks():
    threshold = datetime.now() - timedelta(hours=24)
    with sqlite3.connect(DB_NAME) as conn:
        conn.execute("""
            DELETE FROM tasks 
            WHERE completed = "True" 
            AND timestamp < ?
        """, (threshold.strftime("%Y-%m-%d %H:%M:%S"),))
        conn.commit()
