# Project Statement: Student Task & Performance Tracker

**Course / Context**: VITyarthi Academic Project  
**Domain**: Academic Workflow & Student Performance Tracking  
**Author**: Academic Development Team  

---

## 1. Problem Statement

In academic environments, managing student assignments, course deliverables, and project milestones across multiple semesters and courses is often fragmented. Faculty, project mentors, and students typically resort to ad-hoc communication channels, spreadsheets, or physical notebooks. This lack of centralized management leads to:

- Missed assignment deadlines and submission confusion.
- Inability to quickly identify struggling students or overdue tasks.
- Lack of real-time visibility into overall student performance and completion rates.
- Disorganized records that are difficult to update, audit, or report.

The **Student Task & Performance Tracker** addresses this problem by delivering a lightweight, centralized web application to register students, assign and track tasks with deadlines, and monitor real-time completion analytics on a visual performance dashboard.

---

## 2. Project Scope

### In-Scope:
- **Student Profile Management**: Full CRUD (Create, Read, Update, Delete) operations for student academic records, including name, roll number, course, semester, and email with strict validation and cascade deletion.
- **Academic Task Management**: Creation, viewing, deadline tracking, status toggling (Pending to Completed), filtering, and deletion of academic tasks linked directly to enrolled students.
- **Visual Performance Dashboard**: Aggregate statistical tracking (total students, total tasks, completed tasks, pending tasks, completion percentage) along with an interactive Chart.js donut chart and student-by-student progress breakdown.
- **Lightweight Architecture**: Fully self-contained local SQLite database with parameterized SQL queries, Flask backend routing, and vanilla HTML5/CSS3/JavaScript frontend.
- **Automated Verification**: Pytest automated test suite covering all CRUD operations, invalid input constraints, and statistical computations.

### Out-of-Scope:
- Complex third-party authentication systems (OAuth/SSO) or external user directory sync.
- Heavyweight multi-service architectures (microservices, Docker, Kubernetes, cloud DBMS).
- File upload storage for large attachments.

---

## 3. Target Users

1. **Academic Mentors / Faculty**:
   - Register and maintain student directories for assigned batches.
   - Assign course tasks, homework, and lab deliverables with specified deadlines.
   - Monitor completion metrics and identify students requiring academic intervention.

2. **Students**:
   - Check pending deliverables and imminent deadlines.
   - Update assignment progress and mark completed deliverables.
   - Track personal completion percentages.

3. **Academic Administrators**:
   - Gain bird’s-eye visibility into class-wide assignment completion health.

---

## 4. High-Level Features

| Module | High-Level Feature | Description |
| :--- | :--- | :--- |
| **Module 1: Student Management** | Student Enrollment | Form-based student registration with unique roll number and email checks. |
| | Directory Viewing | Paginated/searchable table displaying enrolled students and course info. |
| | Profile Modification | Edit student information while preserving unique constraints. |
| | Student Removal | Delete student profile with automatic cascading deletion of assigned tasks. |
| **Module 2: Task Management** | Task Assignment | Create deliverables linked to existing students with due dates. |
| | Task Filtering | Filter task views by Pending or Completed status with search support. |
| | Status Toggling | One-click completion marking (`Pending` &rarr; `Completed`). |
| | Task Modification & Removal | Edit assignment details or remove outdated tasks. |
| **Module 3: Performance Dashboard** | Key Metrics Summary | Display Total Students, Total Tasks, Completed, and Pending counts. |
| | Completion Percentage | Compute accurate overall task completion percentage gauge. |
| | Chart.js Visual Analytics | Render an interactive doughnut chart showing Pending vs Completed distribution. |
| | Student Breakdown | Tabular summary of task allocation and individual completion rates. |
