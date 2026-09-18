# Class Diagram: Student Task & Performance Tracker

This document presents the class structure, domain entities, and data models of the application.

```mermaid
classDiagram
    class Student {
        +int student_id
        +string name
        +string roll_number
        +string course
        +int semester
        +string email
        +datetime created_at
        +to_dict() dict
    }

    class Task {
        +int task_id
        +int student_id
        +string title
        +string description
        +string deadline
        +string status
        +datetime created_at
        +is_completed() bool
        +mark_completed() void
    }

    class DashboardStats {
        +int total_students
        +int total_tasks
        +int completed_tasks
        +int pending_tasks
        +float completion_percentage
        +list student_performance
        +calculate_percentage() float
    }

    class DatabaseManager {
        +get_db() Connection
        +close_db() void
        +init_db() void
        +get_all_students() list
        +get_student_by_id(int id) dict
        +create_student(name, roll, course, sem, email) int
        +update_student(id, name, roll, course, sem, email) int
        +delete_student(int id) int
        +get_all_tasks(status, student_id) list
        +get_task_by_id(int id) dict
        +create_task(student_id, title, desc, deadline, status) int
        +update_task(id, title, desc, deadline, status) int
        +update_task_status(id, status) int
        +delete_task(int id) int
        +get_dashboard_stats() dict
    }

    class StudentAPI {
        +list_students() JSON
        +add_student() JSON
        +get_student(int id) JSON
        +edit_student(int id) JSON
        +remove_student(int id) JSON
    }

    class TaskAPI {
        +list_tasks(status, student_id) JSON
        +add_task() JSON
        +get_task(int id) JSON
        +edit_task(int id) JSON
        +complete_task(int id) JSON
        +remove_task(int id) JSON
    }

    class DashboardAPI {
        +dashboard_stats() JSON
    }

    Student "1" --> "0..*" Task : has assigned
    DatabaseManager ..> Student : manages persistence
    DatabaseManager ..> Task : manages persistence
    DatabaseManager ..> DashboardStats : computes
    StudentAPI --> DatabaseManager : uses
    TaskAPI --> DatabaseManager : uses
    DashboardAPI --> DatabaseManager : uses
```

---

## Class Descriptions

### 1. `Student`
Encapsulates an enrolled student profile.
- **Attributes**:
  - `student_id`: Primary identifier (auto-incremented integer).
  - `name`: Full student name.
  - `roll_number`: Unique institutional roll identifier.
  - `course`: Enrolled academic branch/program.
  - `semester`: Current academic semester (1 to 8).
  - `email`: Institutional or personal email address (unique).

### 2. `Task`
Represents an academic deliverable or assignment.
- **Attributes**:
  - `task_id`: Primary identifier.
  - `student_id`: Foreign key referencing the enrolled `Student`.
  - `title`: Short task name.
  - `description`: Detailed task instructions.
  - `deadline`: Submission target date (`YYYY-MM-DD`).
  - `status`: Lifecycle state (`Pending` or `Completed`).

### 3. `DashboardStats`
Represents aggregate calculations for performance reporting.
- **Attributes**:
  - `total_students`: Total active students.
  - `total_tasks`: Total created assignments.
  - `completed_tasks`: Assignments with status `Completed`.
  - `pending_tasks`: Assignments with status `Pending`.
  - `completion_percentage`: `(completed / total) * 100`.
  - `student_performance`: List of student-level task completion statistics.

### 4. `DatabaseManager`
Data access layer wrapping SQLite interactions with parameterized queries and transaction control.
