import sqlite3
import os
from flask import g, current_app

def get_db():
    """Get a database connection for the current request context."""
    if "db" not in g:
        db_path = current_app.config["DATABASE"]
        g.db = sqlite3.connect(db_path)
        g.db.row_factory = sqlite3.Row
        # Enable foreign key support in SQLite
        g.db.execute("PRAGMA foreign_keys = ON;")
    return g.db

def close_db(e=None):
    """Close the database connection if it exists."""
    db = g.pop("db", None)
    if db is not None:
        db.close()

def init_db(app=None):
    """Initialize database tables using schema.sql."""
    if app:
        with app.app_context():
            db = get_db()
            schema_path = os.path.join(os.path.dirname(__file__), "schema.sql")
            with open(schema_path, "r", encoding="utf-8") as f:
                db.executescript(f.read())
            db.commit()
    else:
        db = get_db()
        schema_path = os.path.join(os.path.dirname(__file__), "schema.sql")
        with open(schema_path, "r", encoding="utf-8") as f:
            db.executescript(f.read())
        db.commit()

# ==========================================
# Student Database Helpers
# ==========================================

def get_all_students():
    """Retrieve all students ordered by name."""
    db = get_db()
    cursor = db.execute(
        "SELECT student_id, name, roll_number, course, semester, email, created_at "
        "FROM students ORDER BY name ASC"
    )
    rows = cursor.fetchall()
    return [dict(row) for row in rows]

def get_student_by_id(student_id):
    """Retrieve a single student by student_id."""
    db = get_db()
    cursor = db.execute(
        "SELECT student_id, name, roll_number, course, semester, email, created_at "
        "FROM students WHERE student_id = ?",
        (student_id,)
    )
    row = cursor.fetchone()
    return dict(row) if row else None

def get_student_by_roll(roll_number):
    """Retrieve a student by roll_number."""
    db = get_db()
    cursor = db.execute(
        "SELECT student_id, name, roll_number, course, semester, email, created_at "
        "FROM students WHERE roll_number = ?",
        (roll_number,)
    )
    row = cursor.fetchone()
    return dict(row) if row else None

def get_student_by_email(email):
    """Retrieve a student by email."""
    db = get_db()
    cursor = db.execute(
        "SELECT student_id, name, roll_number, course, semester, email, created_at "
        "FROM students WHERE email = ?",
        (email,)
    )
    row = cursor.fetchone()
    return dict(row) if row else None

def create_student(name, roll_number, course, semester, email):
    """Insert a new student using parameterized query."""
    db = get_db()
    cursor = db.execute(
        "INSERT INTO students (name, roll_number, course, semester, email) "
        "VALUES (?, ?, ?, ?, ?)",
        (name.strip(), roll_number.strip().upper(), course.strip(), int(semester), email.strip().lower())
    )
    db.commit()
    return cursor.lastrowid

def update_student(student_id, name, roll_number, course, semester, email):
    """Update student details by student_id."""
    db = get_db()
    cursor = db.execute(
        "UPDATE students "
        "SET name = ?, roll_number = ?, course = ?, semester = ?, email = ? "
        "WHERE student_id = ?",
        (name.strip(), roll_number.strip().upper(), course.strip(), int(semester), email.strip().lower(), student_id)
    )
    db.commit()
    return cursor.rowcount

def delete_student(student_id):
    """Delete student by student_id (cascades tasks)."""
    db = get_db()
    cursor = db.execute("DELETE FROM students WHERE student_id = ?", (student_id,))
    db.commit()
    return cursor.rowcount

# ==========================================
# Task Database Helpers
# ==========================================

def get_all_tasks(status=None, student_id=None):
    """Retrieve tasks with student info, with optional status and student filters."""
    db = get_db()
    query = (
        "SELECT t.task_id, t.student_id, t.title, t.description, t.deadline, t.status, t.created_at, "
        "       s.name AS student_name, s.roll_number "
        "FROM tasks t "
        "JOIN students s ON t.student_id = s.student_id "
    )
    conditions = []
    params = []

    if status:
        conditions.append("t.status = ?")
        params.append(status)

    if student_id is not None:
        conditions.append("t.student_id = ?")
        params.append(student_id)

    if conditions:
        query += " WHERE " + " AND ".join(conditions)

    query += " ORDER BY t.deadline ASC, t.task_id DESC"

    cursor = db.execute(query, tuple(params))
    rows = cursor.fetchall()
    return [dict(row) for row in rows]

def get_task_by_id(task_id):
    """Retrieve a single task by task_id."""
    db = get_db()
    cursor = db.execute(
        "SELECT t.task_id, t.student_id, t.title, t.description, t.deadline, t.status, t.created_at, "
        "       s.name AS student_name, s.roll_number "
        "FROM tasks t "
        "JOIN students s ON t.student_id = s.student_id "
        "WHERE t.task_id = ?",
        (task_id,)
    )
    row = cursor.fetchone()
    return dict(row) if row else None

def create_task(student_id, title, description, deadline, status="Pending"):
    """Insert a new task using parameterized query."""
    db = get_db()
    cursor = db.execute(
        "INSERT INTO tasks (student_id, title, description, deadline, status) "
        "VALUES (?, ?, ?, ?, ?)",
        (int(student_id), title.strip(), description.strip() if description else "", deadline.strip(), status.strip())
    )
    db.commit()
    return cursor.lastrowid

def update_task(task_id, title, description, deadline, status):
    """Update task details by task_id."""
    db = get_db()
    cursor = db.execute(
        "UPDATE tasks "
        "SET title = ?, description = ?, deadline = ?, status = ? "
        "WHERE task_id = ?",
        (title.strip(), description.strip() if description else "", deadline.strip(), status.strip(), task_id)
    )
    db.commit()
    return cursor.rowcount

def update_task_status(task_id, status):
    """Update only status of a task."""
    db = get_db()
    cursor = db.execute(
        "UPDATE tasks SET status = ? WHERE task_id = ?",
        (status.strip(), task_id)
    )
    db.commit()
    return cursor.rowcount

def delete_task(task_id):
    """Delete a task by task_id."""
    db = get_db()
    cursor = db.execute("DELETE FROM tasks WHERE task_id = ?", (task_id,))
    db.commit()
    return cursor.rowcount

# ==========================================
# Dashboard Statistics Helpers
# ==========================================

def get_dashboard_stats():
    """Calculate aggregate performance metrics."""
    db = get_db()

    # Total students
    cur_students = db.execute("SELECT COUNT(*) AS count FROM students")
    total_students = cur_students.fetchone()["count"]

    # Total tasks, completed tasks, pending tasks
    cur_tasks = db.execute(
        "SELECT "
        "   COUNT(*) AS total_tasks, "
        "   SUM(CASE WHEN status = 'Completed' THEN 1 ELSE 0 END) AS completed_tasks, "
        "   SUM(CASE WHEN status = 'Pending' THEN 1 ELSE 0 END) AS pending_tasks "
        "FROM tasks"
    )
    task_stats = cur_tasks.fetchone()
    total_tasks = task_stats["total_tasks"] or 0
    completed_tasks = task_stats["completed_tasks"] or 0
    pending_tasks = task_stats["pending_tasks"] or 0

    if total_tasks > 0:
        completion_percentage = round((completed_tasks / total_tasks) * 100, 1)
    else:
        completion_percentage = 0.0

    # Student-wise breakdown for performance insights
    cur_student_breakdown = db.execute(
        "SELECT s.student_id, s.name, s.roll_number, s.course, "
        "       COUNT(t.task_id) AS total_assigned, "
        "       SUM(CASE WHEN t.status = 'Completed' THEN 1 ELSE 0 END) AS total_completed, "
        "       SUM(CASE WHEN t.status = 'Pending' THEN 1 ELSE 0 END) AS total_pending "
        "FROM students s "
        "LEFT JOIN tasks t ON s.student_id = t.student_id "
        "GROUP BY s.student_id, s.name, s.roll_number, s.course "
        "ORDER BY total_assigned DESC, s.name ASC"
    )
    student_stats = []
    for r in cur_student_breakdown.fetchall():
        row_dict = dict(r)
        assigned = row_dict["total_assigned"] or 0
        comp = row_dict["total_completed"] or 0
        row_dict["completion_rate"] = round((comp / assigned) * 100, 1) if assigned > 0 else 0.0
        student_stats.append(row_dict)

    return {
        "total_students": total_students,
        "total_tasks": total_tasks,
        "completed_tasks": completed_tasks,
        "pending_tasks": pending_tasks,
        "completion_percentage": completion_percentage,
        "student_performance": student_stats
    }
