/**
 * Module 1: Student Management Frontend Logic
 */

let allStudents = [];
let pendingDeleteStudentId = null;

document.addEventListener("DOMContentLoaded", () => {
    loadStudents();
});

// Fetch and display all students
async function loadStudents() {
    const tbody = document.getElementById("studentsTableBody");
    const countBadge = document.getElementById("studentCountBadge");
    
    try {
        const res = await fetch("/api/students");
        const data = await res.json();

        if (!data.success) {
            tbody.innerHTML = `<tr><td colspan="7" class="text-center text-danger">Failed to load students: ${escapeHtml(data.error)}</td></tr>`;
            return;
        }

        allStudents = data.students || [];
        countBadge.textContent = `${allStudents.length} Student${allStudents.length === 1 ? '' : 's'}`;
        renderStudentsTable(allStudents);
    } catch (err) {
        tbody.innerHTML = `<tr><td colspan="7" class="text-center text-danger">Network error loading students.</td></tr>`;
        console.error(err);
    }
}

// Render student rows into the table
function renderStudentsTable(students) {
    const tbody = document.getElementById("studentsTableBody");
    
    if (students.length === 0) {
        tbody.innerHTML = `
            <tr>
                <td colspan="7" class="text-center" style="padding: 2.5rem 1rem; color: #64748b;">
                    <p style="font-size: 1.1rem; font-weight: 500;">No students found</p>
                    <p style="font-size: 0.85rem; margin-top: 0.35rem;">Click "+ Add Student" above to enroll your first student.</p>
                </td>
            </tr>
        `;
        return;
    }

    tbody.innerHTML = students.map(s => `
        <tr>
            <td><strong>#${s.student_id}</strong></td>
            <td><code style="background:#f1f5f9; padding:0.2rem 0.4rem; border-radius:4px; font-weight:600;">${escapeHtml(s.roll_number)}</code></td>
            <td><strong>${escapeHtml(s.name)}</strong></td>
            <td>${escapeHtml(s.course)}</td>
            <td>Semester ${s.semester}</td>
            <td><a href="mailto:${escapeHtml(s.email)}" style="color:#2563eb; text-decoration:none;">${escapeHtml(s.email)}</a></td>
            <td>
                <div class="actions-cell">
                    <button class="btn btn-secondary btn-sm" onclick="openEditStudentModal(${s.student_id})">✏️ Edit</button>
                    <button class="btn btn-danger btn-sm" onclick="openDeleteStudentModal(${s.student_id}, '${escapeHtml(s.name)}')">🗑️ Delete</button>
                </div>
            </td>
        </tr>
    `).join("");
}

// Filter students by search input
function filterStudentsTable() {
    const query = (document.getElementById("studentSearchInput").value || "").toLowerCase().trim();
    if (!query) {
        renderStudentsTable(allStudents);
        return;
    }

    const filtered = allStudents.filter(s => 
        s.name.toLowerCase().includes(query) ||
        s.roll_number.toLowerCase().includes(query) ||
        s.course.toLowerCase().includes(query) ||
        s.email.toLowerCase().includes(query)
    );
    renderStudentsTable(filtered);
}

// Open Add Student Modal
function openAddStudentModal() {
    document.getElementById("addStudentForm").reset();
    const err = document.getElementById("addStudentError");
    err.textContent = "";
    err.style.display = "none";
    openModal("addStudentModal");
}

// Handle Add Student Form Submit
async function handleAddStudent(e) {
    e.preventDefault();
    const err = document.getElementById("addStudentError");
    const submitBtn = document.getElementById("addStudentSubmitBtn");

    err.textContent = "";
    err.style.display = "none";

    const name = document.getElementById("addName").value.trim();
    const roll_number = document.getElementById("addRoll").value.trim();
    const course = document.getElementById("addCourse").value.trim();
    const semester = parseInt(document.getElementById("addSemester").value, 10);
    const email = document.getElementById("addEmail").value.trim();

    // Client-side validation
    if (!name) return showFormError(err, "Student name is required.");
    if (!roll_number) return showFormError(err, "Roll number is required.");
    if (!course) return showFormError(err, "Course is required.");
    if (isNaN(semester) || semester < 1 || semester > 8) return showFormError(err, "Semester must be between 1 and 8.");
    if (!email || !isValidEmail(email)) return showFormError(err, "Please provide a valid email address.");

    submitBtn.disabled = true;
    submitBtn.textContent = "Saving...";

    try {
        const res = await fetch("/api/students", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ name, roll_number, course, semester, email })
        });
        const data = await res.json();

        if (!res.ok || !data.success) {
            showFormError(err, data.error || "Failed to add student.");
            return;
        }

        closeModal("addStudentModal");
        showToast(`Student "${name}" added successfully!`, "success");
        loadStudents();
    } catch (error) {
        showFormError(err, "Network error occurred while saving student.");
        console.error(error);
    } finally {
        submitBtn.disabled = false;
        submitBtn.textContent = "Save Student";
    }
}

// Open Edit Student Modal
async function openEditStudentModal(studentId) {
    const err = document.getElementById("editStudentError");
    err.textContent = "";
    err.style.display = "none";

    try {
        const res = await fetch(`/api/students/${studentId}`);
        const data = await res.json();

        if (!res.ok || !data.success) {
            showToast(data.error || "Could not retrieve student details", "error");
            return;
        }

        const s = data.student;
        document.getElementById("editStudentId").value = s.student_id;
        document.getElementById("editName").value = s.name;
        document.getElementById("editRoll").value = s.roll_number;
        document.getElementById("editCourse").value = s.course;
        document.getElementById("editSemester").value = s.semester;
        document.getElementById("editEmail").value = s.email;

        openModal("editStudentModal");
    } catch (error) {
        showToast("Error loading student profile", "error");
        console.error(error);
    }
}

// Handle Edit Student Form Submit
async function handleEditStudent(e) {
    e.preventDefault();
    const err = document.getElementById("editStudentError");
    const submitBtn = document.getElementById("editStudentSubmitBtn");

    const studentId = document.getElementById("editStudentId").value;
    const name = document.getElementById("editName").value.trim();
    const roll_number = document.getElementById("editRoll").value.trim();
    const course = document.getElementById("editCourse").value.trim();
    const semester = parseInt(document.getElementById("editSemester").value, 10);
    const email = document.getElementById("editEmail").value.trim();

    if (!name) return showFormError(err, "Student name is required.");
    if (!roll_number) return showFormError(err, "Roll number is required.");
    if (!course) return showFormError(err, "Course is required.");
    if (isNaN(semester) || semester < 1 || semester > 8) return showFormError(err, "Semester must be between 1 and 8.");
    if (!email || !isValidEmail(email)) return showFormError(err, "Please provide a valid email address.");

    submitBtn.disabled = true;
    submitBtn.textContent = "Updating...";

    try {
        const res = await fetch(`/api/students/${studentId}`, {
            method: "PUT",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ name, roll_number, course, semester, email })
        });
        const data = await res.json();

        if (!res.ok || !data.success) {
            showFormError(err, data.error || "Failed to update student.");
            return;
        }

        closeModal("editStudentModal");
        showToast(`Student "${name}" updated successfully!`, "success");
        loadStudents();
    } catch (error) {
        showFormError(err, "Network error occurred while updating student.");
        console.error(error);
    } finally {
        submitBtn.disabled = false;
        submitBtn.textContent = "Update Student";
    }
}

// Open Delete Confirmation Modal
function openDeleteStudentModal(studentId, studentName) {
    pendingDeleteStudentId = studentId;
    document.getElementById("deleteStudentName").textContent = studentName;
    
    const confirmBtn = document.getElementById("confirmDeleteStudentBtn");
    confirmBtn.onclick = handleConfirmDeleteStudent;

    openModal("deleteStudentModal");
}

// Handle Confirmed Student Deletion
async function handleConfirmDeleteStudent() {
    if (!pendingDeleteStudentId) return;

    try {
        const res = await fetch(`/api/students/${pendingDeleteStudentId}`, {
            method: "DELETE"
        });
        const data = await res.json();

        if (!res.ok || !data.success) {
            showToast(data.error || "Failed to delete student", "error");
            return;
        }

        closeModal("deleteStudentModal");
        showToast("Student deleted successfully.", "success");
        loadStudents();
    } catch (error) {
        showToast("Network error occurred while deleting student.", "error");
        console.error(error);
    } finally {
        pendingDeleteStudentId = null;
    }
}

function showFormError(element, message) {
    element.textContent = message;
    element.style.display = "block";
}

function isValidEmail(email) {
    return /^[\w\.-]+@[\w\.-]+\.\w+$/.test(email);
}
