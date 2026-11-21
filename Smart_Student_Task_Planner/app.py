import sqlite3
from datetime import date
from pathlib import Path

import pandas as pd
import streamlit as st

DB_PATH = Path(__file__).with_name("student_tasks.db")

st.set_page_config(page_title="Smart Student Task Planner", page_icon="📚", layout="wide")


def get_connection():
    return sqlite3.connect(DB_PATH)


def init_db():
    with get_connection() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS tasks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                task_type TEXT NOT NULL,
                subject TEXT,
                due_date TEXT NOT NULL,
                priority TEXT NOT NULL,
                status TEXT NOT NULL DEFAULT 'Pending',
                notes TEXT
            )
        """)


def load_tasks():
    with get_connection() as conn:
        return pd.read_sql_query("SELECT * FROM tasks ORDER BY due_date ASC, id DESC", conn)


def add_task(title, task_type, subject, due_date, priority, notes):
    with get_connection() as conn:
        conn.execute(
            """INSERT INTO tasks
            (title, task_type, subject, due_date, priority, notes)
            VALUES (?, ?, ?, ?, ?, ?)""",
            (title, task_type, subject, due_date.isoformat(), priority, notes),
        )


def update_status(task_id, status):
    with get_connection() as conn:
        conn.execute("UPDATE tasks SET status = ? WHERE id = ?", (status, int(task_id)))


def delete_task(task_id):
    with get_connection() as conn:
        conn.execute("DELETE FROM tasks WHERE id = ?", (int(task_id),))


init_db()
st.title("📚 Smart Student Task Planner")
st.caption("Organise assignments, exams, deadlines and daily study tasks in one place.")

tasks = load_tasks()
today = date.today().isoformat()

total = len(tasks)
completed = int((tasks["status"] == "Completed").sum()) if total else 0
pending = total - completed
due_today = int((tasks["due_date"] == today).sum()) if total else 0
overdue = int(((tasks["due_date"] < today) & (tasks["status"] != "Completed")).sum()) if total else 0

m1, m2, m3, m4 = st.columns(4)
m1.metric("Total tasks", total)
m2.metric("Not completed", pending)
m3.metric("Due today", due_today)
m4.metric("Overdue", overdue)

st.divider()
tab1, tab2 = st.tabs(["➕ Add a task", "📋 View and manage tasks"])

with tab1:
    st.subheader("Add a new task")
    with st.form("add_task_form", clear_on_submit=True):
        title = st.text_input("Task title *", placeholder="Example: Complete DBMS assignment")
        c1, c2 = st.columns(2)
        task_type = c1.selectbox("Task type", ["Assignment", "Exam", "Project", "Study", "Other"])
        subject = c2.text_input("Subject", placeholder="Example: DBMS")
        c3, c4 = st.columns(2)
        due_date = c3.date_input("Due date", value=date.today())
        priority = c4.selectbox("Priority", ["Low", "Medium", "High"], index=1)
        notes = st.text_area("Notes (optional)", placeholder="Add any details...")
        submitted = st.form_submit_button("Save task", type="primary")
        if submitted:
            if not title.strip():
                st.error("Please enter a task title.")
            else:
                add_task(title.strip(), task_type, subject.strip(), due_date, priority, notes.strip())
                st.success("Task added successfully!")
                st.rerun()

with tab2:
    st.subheader("Your tasks")
    if tasks.empty:
        st.info("No tasks yet. Add your first task in the 'Add a task' tab.")
    else:
        search = st.text_input("Search by title or subject")
        f1, f2 = st.columns(2)
        status_filter = f1.selectbox("Filter by status", ["All", "Pending", "In Progress", "Completed"])
        type_filter = f2.selectbox("Filter by type", ["All"] + sorted(tasks["task_type"].dropna().unique().tolist()))

        shown = tasks.copy()
        if search:
            mask = (
                shown["title"].str.contains(search, case=False, na=False)
                | shown["subject"].str.contains(search, case=False, na=False)
            )
            shown = shown[mask]
        if status_filter != "All":
            shown = shown[shown["status"] == status_filter]
        if type_filter != "All":
            shown = shown[shown["task_type"] == type_filter]

        display = shown.copy()
        display["Due date"] = display["due_date"]
        display = display.rename(columns={
            "title": "Task", "task_type": "Type", "subject": "Subject",
            "priority": "Priority", "status": "Status"
        })
        st.dataframe(
            display[["id", "Task", "Type", "Subject", "Due date", "Priority", "Status"]],
            use_container_width=True,
            hide_index=True,
        )

        st.markdown("#### Update or delete a task")
        task_options = {
            f'#{row.id} — {row.title} ({row.due_date})': int(row.id)
            for row in shown.itertuples()
        }
        if task_options:
            selected_label = st.selectbox("Choose a task", list(task_options.keys()))
            selected_id = task_options[selected_label]
            selected_row = tasks[tasks["id"] == selected_id].iloc[0]
            c1, c2 = st.columns([2, 1])
            new_status = c1.selectbox(
                "Change status",
                ["Pending", "In Progress", "Completed"],
                index=["Pending", "In Progress", "Completed"].index(selected_row["status"]),
                key=f"status_{selected_id}",
            )
            if c1.button("Update status"):
                update_status(selected_id, new_status)
                st.success("Status updated.")
                st.rerun()
            if c2.button("Delete task", type="secondary"):
                delete_task(selected_id)
                st.success("Task deleted.")
                st.rerun()

        st.markdown("#### Progress")
        progress = completed / total if total else 0
        st.progress(progress, text=f"{completed} of {total} tasks completed")
        status_counts = tasks["status"].value_counts().reindex(
            ["Pending", "In Progress", "Completed"], fill_value=0
        )
        st.bar_chart(status_counts)

        csv = tasks.to_csv(index=False).encode("utf-8")
        st.download_button("⬇️ Export tasks as CSV", csv, "student_tasks.csv", "text/csv")

st.divider()
st.caption("Your tasks are saved locally in an SQLite database file named student_tasks.db.")
