import re
from datetime import datetime
import sqlite3
from flask import Blueprint, request, jsonify
from database import (
    get_all_students,
    get_student_by_id,
    get_student_by_roll,
    get_student_by_email,
    create_student,
    update_student,
    delete_student,
    get_all_tasks,
    get_task_by_id,
    create_task,
    update_task,
    update_task_status,
    delete_task,
    get_dashboard_stats
)

api_bp = Blueprint("api", __name__, url_prefix="/api")

EMAIL_REGEX = r"^[\w\.-]+@[\w\.-]+\.\w+$"

# =======================================================
# MODULE 1: Student Management Endpoints
# =======================================================

@api_bp.route("/students", methods=["GET"])
def list_students():
    """Retrieve all students."""
    students = get_all_students()
    return jsonify({"success": True, "count": len(students), "students": students}), 200

@api_bp.route("/students", methods=["POST"])
def add_student():
    """Add a new student with validation."""
    data = request.get_json() or {}

    name = data.get("name")
    roll_number = data.get("roll_number")
    course = data.get("course")
    semester = data.get("semester")
    email = data.get("email")

    # Validation
    if not name or not str(name).strip():
        return jsonify({"success": False, "error": "Student name is required."}), 400

    if not roll_number or not str(roll_number).strip():
        return jsonify({"success": False, "error": "Roll number is required."}), 400

    if not course or not str(course).strip():
        return jsonify({"success": False, "error": "Course is required."}), 400

    if semester is None:
        return jsonify({"success": False, "error": "Semester is required."}), 400

    try:
        semester = int(semester)
        if semester < 1 or semester > 8:
            return jsonify({"success": False, "error": "Semester must be an integer between 1 and 8."}), 400
    except (ValueError, TypeError):
        return jsonify({"success": False, "error": "Semester must be a valid integer between 1 and 8."}), 400

    if not email or not str(email).strip():
        return jsonify({"success": False, "error": "Email is required."}), 400

    if not re.match(EMAIL_REGEX, email.strip()):
        return jsonify({"success": False, "error": "Invalid email format."}), 400

    # Uniqueness checks
    if get_student_by_roll(roll_number.strip().upper()):
        return jsonify({"success": False, "error": f"Student with roll number '{roll_number}' already exists."}), 409

    if get_student_by_email(email.strip().lower()):
        return jsonify({"success": False, "error": f"Student with email '{email}' already exists."}), 409

    try:
        student_id = create_student(name, roll_number, course, semester, email)
        return jsonify({
            "success": True,
            "message": "Student created successfully.",
            "student_id": student_id
        }), 201
    except sqlite3.IntegrityError as e:
        return jsonify({"success": False, "error": f"Database integrity error: {str(e)}"}), 400
    except Exception as e:
        return jsonify({"success": False, "error": f"Server error: {str(e)}"}), 500

@api_bp.route("/students/<int:student_id>", methods=["GET"])
def get_student(student_id):
    """Retrieve details of a specific student."""
    student = get_student_by_id(student_id)
    if not student:
        return jsonify({"success": False, "error": f"Student with ID {student_id} not found."}), 404
    return jsonify({"success": True, "student": student}), 200

@api_bp.route("/students/<int:student_id>", methods=["PUT"])
def edit_student(student_id):
    """Update details of an existing student."""
    existing = get_student_by_id(student_id)
    if not existing:
        return jsonify({"success": False, "error": f"Student with ID {student_id} not found."}), 404

    data = request.get_json() or {}

    name = data.get("name")
    roll_number = data.get("roll_number")
    course = data.get("course")
    semester = data.get("semester")
    email = data.get("email")

    # Validation
    if not name or not str(name).strip():
        return jsonify({"success": False, "error": "Student name is required."}), 400

    if not roll_number or not str(roll_number).strip():
        return jsonify({"success": False, "error": "Roll number is required."}), 400

    if not course or not str(course).strip():
        return jsonify({"success": False, "error": "Course is required."}), 400

    if semester is None:
        return jsonify({"success": False, "error": "Semester is required."}), 400

    try:
        semester = int(semester)
        if semester < 1 or semester > 8:
            return jsonify({"success": False, "error": "Semester must be an integer between 1 and 8."}), 400
    except (ValueError, TypeError):
        return jsonify({"success": False, "error": "Semester must be a valid integer between 1 and 8."}), 400

    if not email or not str(email).strip():
        return jsonify({"success": False, "error": "Email is required."}), 400

    if not re.match(EMAIL_REGEX, email.strip()):
        return jsonify({"success": False, "error": "Invalid email format."}), 400

    # Check roll number uniqueness if changed
    roll_match = get_student_by_roll(roll_number.strip().upper())
    if roll_match and roll_match["student_id"] != student_id:
        return jsonify({"success": False, "error": f"Roll number '{roll_number}' is already taken."}), 409

    # Check email uniqueness if changed
    email_match = get_student_by_email(email.strip().lower())
    if email_match and email_match["student_id"] != student_id:
        return jsonify({"success": False, "error": f"Email '{email}' is already taken."}), 409

    try:
        update_student(student_id, name, roll_number, course, semester, email)
        updated = get_student_by_id(student_id)
        return jsonify({
            "success": True,
            "message": "Student updated successfully.",
            "student": updated
        }), 200
    except Exception as e:
        return jsonify({"success": False, "error": f"Failed to update student: {str(e)}"}), 500

@api_bp.route("/students/<int:student_id>", methods=["DELETE"])
def remove_student(student_id):
    """Delete a student and cascade delete associated tasks."""
    existing = get_student_by_id(student_id)
    if not existing:
        return jsonify({"success": False, "error": f"Student with ID {student_id} not found."}), 404

    try:
        delete_student(student_id)
        return jsonify({
            "success": True,
            "message": f"Student '{existing['name']}' and associated tasks deleted successfully."
        }), 200
    except Exception as e:
        return jsonify({"success": False, "error": f"Failed to delete student: {str(e)}"}), 500

# =======================================================
# MODULE 2: Task Management Endpoints
# =======================================================

@api_bp.route("/tasks", methods=["GET"])
def list_tasks():
    """Retrieve tasks with optional status and student_id filters."""
    status = request.args.get("status")
    student_id = request.args.get("student_id")

    if status and status not in ["Pending", "Completed"]:
        return jsonify({"success": False, "error": "Status must be 'Pending' or 'Completed'."}), 400

    student_id_int = None
    if student_id:
        try:
            student_id_int = int(student_id)
        except ValueError:
            return jsonify({"success": False, "error": "student_id filter must be an integer."}), 400

    tasks = get_all_tasks(status=status, student_id=student_id_int)
    return jsonify({"success": True, "count": len(tasks), "tasks": tasks}), 200

@api_bp.route("/tasks", methods=["POST"])
def add_task():
    """Add a new task linked to a student with validation."""
    data = request.get_json() or {}

    student_id = data.get("student_id")
    title = data.get("title")
    description = data.get("description", "")
    deadline = data.get("deadline")
    status = data.get("status", "Pending")

    # Validation
    if student_id is None:
        return jsonify({"success": False, "error": "student_id is required."}), 400

    try:
        student_id = int(student_id)
    except (ValueError, TypeError):
        return jsonify({"success": False, "error": "student_id must be a valid integer."}), 400

    student = get_student_by_id(student_id)
    if not student:
        return jsonify({"success": False, "error": f"Student with ID {student_id} does not exist."}), 404

    if not title or not str(title).strip():
        return jsonify({"success": False, "error": "Task title is required."}), 400

    if not deadline or not str(deadline).strip():
        return jsonify({"success": False, "error": "Task deadline is required."}), 400

    try:
        datetime.strptime(deadline.strip(), "%Y-%m-%d")
    except ValueError:
        return jsonify({"success": False, "error": "Deadline must be in YYYY-MM-DD format."}), 400

    if status not in ["Pending", "Completed"]:
        return jsonify({"success": False, "error": "Status must be 'Pending' or 'Completed'."}), 400

    try:
        task_id = create_task(student_id, title, description, deadline, status)
        return jsonify({
            "success": True,
            "message": "Task created successfully.",
            "task_id": task_id
        }), 201
    except Exception as e:
        return jsonify({"success": False, "error": f"Failed to create task: {str(e)}"}), 500

@api_bp.route("/tasks/<int:task_id>", methods=["GET"])
def get_task(task_id):
    """Retrieve details of a single task."""
    task = get_task_by_id(task_id)
    if not task:
        return jsonify({"success": False, "error": f"Task with ID {task_id} not found."}), 404
    return jsonify({"success": True, "task": task}), 200

@api_bp.route("/tasks/<int:task_id>", methods=["PUT"])
def edit_task(task_id):
    """Update task details."""
    existing = get_task_by_id(task_id)
    if not existing:
        return jsonify({"success": False, "error": f"Task with ID {task_id} not found."}), 404

    data = request.get_json() or {}
    title = data.get("title")
    description = data.get("description", existing["description"])
    deadline = data.get("deadline")
    status = data.get("status", existing["status"])

    if not title or not str(title).strip():
        return jsonify({"success": False, "error": "Task title is required."}), 400

    if not deadline or not str(deadline).strip():
        return jsonify({"success": False, "error": "Task deadline is required."}), 400

    try:
        datetime.strptime(deadline.strip(), "%Y-%m-%d")
    except ValueError:
        return jsonify({"success": False, "error": "Deadline must be in YYYY-MM-DD format."}), 400

    if status not in ["Pending", "Completed"]:
        return jsonify({"success": False, "error": "Status must be 'Pending' or 'Completed'."}), 400

    try:
        update_task(task_id, title, description, deadline, status)
        updated = get_task_by_id(task_id)
        return jsonify({
            "success": True,
            "message": "Task updated successfully.",
            "task": updated
        }), 200
    except Exception as e:
        return jsonify({"success": False, "error": f"Failed to update task: {str(e)}"}), 500

@api_bp.route("/tasks/<int:task_id>/complete", methods=["PATCH"])
def complete_task(task_id):
    """Mark a task as completed."""
    existing = get_task_by_id(task_id)
    if not existing:
        return jsonify({"success": False, "error": f"Task with ID {task_id} not found."}), 404

    try:
        update_task_status(task_id, "Completed")
        return jsonify({
            "success": True,
            "message": "Task marked as completed.",
            "task_id": task_id,
            "status": "Completed"
        }), 200
    except Exception as e:
        return jsonify({"success": False, "error": f"Failed to complete task: {str(e)}"}), 500

@api_bp.route("/tasks/<int:task_id>", methods=["DELETE"])
def remove_task(task_id):
    """Delete a task."""
    existing = get_task_by_id(task_id)
    if not existing:
        return jsonify({"success": False, "error": f"Task with ID {task_id} not found."}), 404

    try:
        delete_task(task_id)
        return jsonify({
            "success": True,
            "message": "Task deleted successfully."
        }), 200
    except Exception as e:
        return jsonify({"success": False, "error": f"Failed to delete task: {str(e)}"}), 500

# =======================================================
# MODULE 3: Performance Dashboard Statistics Endpoint
# =======================================================

@api_bp.route("/dashboard/stats", methods=["GET"])
def dashboard_stats():
    """Return aggregate performance statistics for the dashboard."""
    try:
        stats = get_dashboard_stats()
        return jsonify({
            "success": True,
            "stats": stats
        }), 200
    except Exception as e:
        return jsonify({"success": False, "error": f"Failed to compute statistics: {str(e)}"}), 500
