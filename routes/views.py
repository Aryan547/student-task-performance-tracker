from flask import Blueprint, render_template

views_bp = Blueprint("views", __name__)

@views_bp.route("/")
def index():
    """Render home portal page."""
    return render_template("index.html")

@views_bp.route("/students")
def students():
    """Render Student Management page."""
    return render_template("students.html")

@views_bp.route("/tasks")
def tasks():
    """Render Task Management page."""
    return render_template("tasks.html")

@views_bp.route("/dashboard")
def dashboard():
    """Render Performance Dashboard page."""
    return render_template("dashboard.html")
