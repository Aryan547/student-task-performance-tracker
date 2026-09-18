# Sequence Diagrams: Student Task & Performance Tracker

This document presents interaction sequences between the User, Web Browser, Flask Application, and SQLite Database.

---

## 1. Student Creation Sequence

```mermaid
sequenceDiagram
    autonumber
    actor User as Academic Mentor
    participant Browser as Browser UI (students.js)
    participant Flask as Flask Server (routes/api.py)
    participant DB as SQLite DB (database.py)

    User->>Browser: Enters student details & clicks "Save Student"
    Browser->>Browser: Client-side validation (regex, range check)
    alt Validation fails
        Browser-->>User: Display error message in modal
    else Validation passes
        Browser->>Flask: POST /api/students {name, roll_number, course, semester, email}
        Flask->>DB: Check if roll_number or email exists
        DB-->>Flask: Query result
        alt Duplicate found
            Flask-->>Browser: 409 Conflict {"success": false, "error": "Already exists"}
            Browser-->>User: Display duplicate error alert
        else Unique record
            Flask->>DB: INSERT INTO students VALUES (...)
            DB-->>Flask: Return student_id
            Flask-->>Browser: 201 Created {"success": true, "student_id": id}
            Browser->>Browser: Close modal & trigger showToast("Saved!")
            Browser->>Flask: GET /api/students
            Flask->>DB: SELECT * FROM students ORDER BY name
            DB-->>Flask: Student records
            Flask-->>Browser: 200 OK {"students": [...]}
            Browser-->>User: Render updated student table
        end
    end
```

---

## 2. Task Assignment & Completion Sequence

```mermaid
sequenceDiagram
    autonumber
    actor User as User (Mentor / Student)
    participant Browser as Browser UI (tasks.js)
    participant Flask as Flask Server (routes/api.py)
    participant DB as SQLite DB (database.py)

    Note over User,DB: Task Creation Flow
    User->>Browser: Fills task form & clicks "Save Task"
    Browser->>Flask: POST /api/tasks {student_id, title, deadline, status: "Pending"}
    Flask->>DB: Verify student_id exists in students table
    DB-->>Flask: Verified
    Flask->>DB: INSERT INTO tasks VALUES (...)
    DB-->>Flask: Return task_id
    Flask-->>Browser: 201 Created {"success": true, "task_id": id}
    Browser-->>User: Display success toast & refresh tasks table

    Note over User,DB: Task Completion Flow
    User->>Browser: Clicks "✅ Done" button on task row
    Browser->>Flask: PATCH /api/tasks/:id/complete
    Flask->>DB: UPDATE tasks SET status = 'Completed' WHERE task_id = :id
    DB-->>Flask: Rows affected: 1
    Flask-->>Browser: 200 OK {"success": true, "status": "Completed"}
    Browser->>Browser: Update status badge to "Completed"
    Browser-->>User: Display celebration toast notification
```

---

## 3. Performance Dashboard Statistics Sequence

```mermaid
sequenceDiagram
    autonumber
    actor User as User
    participant Browser as Browser UI (dashboard.js)
    participant Flask as Flask Server (routes/api.py)
    participant DB as SQLite DB (database.py)
    participant Chart as Chart.js Engine

    User->>Browser: Navigates to /dashboard
    Browser->>Flask: GET /api/dashboard/stats
    Flask->>DB: SELECT COUNT(*) FROM students
    DB-->>Flask: total_students
    Flask->>DB: SELECT COUNT(*), SUM(Completed), SUM(Pending) FROM tasks
    DB-->>Flask: Task aggregates
    Flask->>DB: SELECT student_id, counts GROUP BY student_id
    DB-->>Flask: Student breakdown rows
    Flask->>Flask: Calculate completion_percentage = (completed / total) * 100
    Flask-->>Browser: 200 OK {"success": true, "stats": {...}}
    Browser->>Browser: Update Total Students, Total Tasks, Completed, Pending cards
    Browser->>Browser: Animate completion rate progress bar
    Browser->>Chart: new Chart(ctx, {type: 'doughnut', data: [completed, pending]})
    Chart-->>Browser: Render interactive doughnut chart
    Browser->>Browser: Render student performance breakdown table
    Browser-->>User: Display comprehensive performance dashboard
```
