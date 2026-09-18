"""Utility script to seed realistic sample data into tracker.db for local demo."""
from app import create_app
from database import create_student, create_task, get_all_students

def seed():
    app = create_app("development")
    with app.app_context():
        existing = get_all_students()
        if not existing:
            s1 = create_student("Aarav Sharma", "21BCE1001", "B.Tech CSE", 6, "aarav.sharma@example.com")
            s2 = create_student("Diya Patel", "21BCE1045", "B.Tech IT", 6, "diya.patel@example.com")
            s3 = create_student("Rohan Verma", "21BCE1120", "B.Tech CSE", 6, "rohan.verma@example.com")

            create_task(s1, "Operating Systems Lab 4", "Implement CPU scheduling algorithms (Round Robin & FCFS)", "2026-10-05", "Completed")
            create_task(s1, "Database Design Milestone", "Submit normalized ER diagram and schema definitions", "2026-10-12", "Completed")
            create_task(s1, "Cloud Computing Assignment", "Deploy Flask app using SQLite persistence", "2026-10-25", "Pending")
            create_task(s2, "Web Development Portfolio", "Build responsive dashboard using HTML, CSS and Chart.js", "2026-10-15", "Completed")
            create_task(s3, "Algorithm Analysis Homework", "Solve dynamic programming recurrence relations", "2026-10-18", "Pending")
            print("Successfully seeded 3 students and 5 tasks into tracker.db!")
        else:
            print("Database already populated, skipping seed.")

if __name__ == "__main__":
    seed()
