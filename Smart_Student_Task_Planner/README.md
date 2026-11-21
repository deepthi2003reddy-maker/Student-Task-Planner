# Smart Student Task Planner

A beginner-friendly B.Tech CSE mini project built with Python, Streamlit and SQLite.

## Features
- Add assignments, exams, projects and daily study tasks
- Set subject, due date and priority
- Track Pending, In Progress and Completed tasks
- Search and filter tasks
- Update task status or delete tasks
- Dashboard for due-today and overdue tasks
- Progress chart
- Export tasks to CSV
- Automatically saves tasks in SQLite

## Requirements
- Python 3.10 or newer
- Visual Studio Code
- Internet connection for installing Python packages (first time only)

## Run in VS Code (Windows)

1. Extract the ZIP file.
2. Open VS Code.
3. Select **File → Open Folder** and choose `Smart_Student_Task_Planner`.
4. Open **Terminal → New Terminal**.
5. Run these commands one by one:

```powershell
python -m venv .venv
.venv\Scripts\activate
python -m pip install -r requirements.txt
streamlit run app.py
```

6. The app opens in your browser at `http://localhost:8501`.

If `python` is not recognised, install Python from https://www.python.org/downloads/ and tick **Add Python to PATH** during installation.

## Project files
- `app.py` — main application
- `requirements.txt` — required Python packages
- `student_tasks.db` — created automatically when the app runs
