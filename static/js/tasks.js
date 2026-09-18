/**
 * Module 2: Task Management Frontend Logic
 */

let allTasks = [];
let pendingDeleteTaskId = null;

document.addEventListener("DOMContentLoaded", () => {
    loadTasks();
});

// Load tasks from backend with status filter
async function loadTasks() {
    const tbody = document.getElementById("tasksTableBody");
    const countBadge = document.getElementById("taskCountBadge");
    const statusFilter = document.getElementById("statusFilter") ? document.getElementById("statusFilter").value : "";

    let url = "/api/tasks";
    if (statusFilter) {
        url += `?status=${encodeURIComponent(statusFilter)}`;
    }

    try {
        const res = await fetch(url);
        const data = await res.json();

        if (!data.success) {
            tbody.innerHTML = `<tr><td colspan="6" class="text-center text-danger">Failed to load tasks: ${escapeHtml(data.error)}</td></tr>`;
            return;
        }

        allTasks = data.tasks || [];
        countBadge.textContent = `${allTasks.length} Task${allTasks.length === 1 ? '' : 's'}`;
        renderTasksTable(allTasks);
    } catch (err) {
        tbody.innerHTML = `<tr><td colspan="6" class="text-center text-danger">Network error loading tasks.</td></tr>`;
        console.error(err);
    }
}

// Render tasks into table
function renderTasksTable(tasks) {
    const tbody = document.getElementById("tasksTableBody");

    if (tasks.length === 0) {
        tbody.innerHTML = `
            <tr>
                <td colspan="6" class="text-center" style="padding: 2.5rem 1rem; color: #64748b;">
                    <p style="font-size: 1.1rem; font-weight: 500;">No tasks found</p>
                    <p style="font-size: 0.85rem; margin-top: 0.35rem;">Click "+ Add Task" above to assign an academic assignment.</p>
                </td>
            </tr>
        `;
        return;
    }

    tbody.innerHTML = tasks.map(t => {
        const isCompleted = t.status === "Completed";
        const statusBadge = isCompleted
            ? `<span class="badge badge-completed">Completed</span>`
            : `<span class="badge badge-pending">Pending</span>`;

        const markDoneBtn = !isCompleted
            ? `<button class="btn btn-success btn-sm" onclick="markTaskCompleted(${t.task_id})">✅ Done</button>`
            : ``;

        return `
            <tr>
                <td><strong>#${t.task_id}</strong></td>
                <td>
                    <div style="font-weight: 600; color: #0f172a;">${escapeHtml(t.title)}</div>
                    ${t.description ? `<div style="font-size: 0.85rem; color: #64748b; margin-top: 0.2rem;">${escapeHtml(t.description)}</div>` : ''}
                </td>
                <td>
                    <div style="font-weight: 500;">${escapeHtml(t.student_name)}</div>
                    <code style="background:#f1f5f9; padding:0.1rem 0.35rem; border-radius:4px; font-size:0.8rem; color:#475569;">${escapeHtml(t.roll_number)}</code>
                </td>
                <td>
                    <span style="font-size: 0.9rem; font-family: monospace;">📅 ${escapeHtml(t.deadline)}</span>
                </td>
                <td>${statusBadge}</td>
                <td>
                    <div class="actions-cell">
                        ${markDoneBtn}
                        <button class="btn btn-secondary btn-sm" onclick="openEditTaskModal(${t.task_id})">✏️ Edit</button>
                        <button class="btn btn-danger btn-sm" onclick="openDeleteTaskModal(${t.task_id}, '${escapeHtml(t.title)}')">🗑️ Delete</button>
                    </div>
                </td>
            </tr>
        `;
    }).join("");
}

// Filter tasks in memory by search query
function filterTasksTable() {
    const query = (document.getElementById("taskSearchInput").value || "").toLowerCase().trim();
    if (!query) {
        renderTasksTable(allTasks);
        return;
    }

    const filtered = allTasks.filter(t => 
        t.title.toLowerCase().includes(query) ||
        (t.description && t.description.toLowerCase().includes(query)) ||
        t.student_name.toLowerCase().includes(query) ||
        t.roll_number.toLowerCase().includes(query) ||
        t.deadline.toLowerCase().includes(query) ||
        t.status.toLowerCase().includes(query)
    );
    renderTasksTable(filtered);
}

// Open Add Task Modal & populate students dropdown
async function openAddTaskModal() {
    document.getElementById("addTaskForm").reset();
    const err = document.getElementById("addTaskError");
    err.textContent = "";
    err.style.display = "none";

    // Set default deadline to today + 7 days
    const today = new Date();
    today.setDate(today.getDate() + 7);
    const defaultDeadline = today.toISOString().split("T")[0];
    document.getElementById("addTaskDeadline").value = defaultDeadline;

    // Populate students dropdown
    const select = document.getElementById("addStudentSelect");
    select.innerHTML = `<option value="">Loading students...</option>`;

    try {
        const res = await fetch("/api/students");
        const data = await res.json();
        
        if (!data.success || !data.students || data.students.length === 0) {
            select.innerHTML = `<option value="">-- No students registered. Please add a student first! --</option>`;
            showToast("Please register at least one student before creating tasks.", "warning");
        } else {
            select.innerHTML = `<option value="">-- Select Enrolled Student --</option>` + 
                data.students.map(s => `<option value="${s.student_id}">${escapeHtml(s.name)} (${escapeHtml(s.roll_number)} - ${escapeHtml(s.course)})</option>`).join("");
        }
    } catch (e) {
        select.innerHTML = `<option value="">Error loading students</option>`;
        console.error(e);
    }

    openModal("addTaskModal");
}

// Handle Add Task Submission
async function handleAddTask(e) {
    e.preventDefault();
    const err = document.getElementById("addTaskError");
    const submitBtn = document.getElementById("addTaskSubmitBtn");

    err.textContent = "";
    err.style.display = "none";

    const student_id = document.getElementById("addStudentSelect").value;
    const title = document.getElementById("addTaskTitle").value.trim();
    const description = document.getElementById("addTaskDesc").value.trim();
    const deadline = document.getElementById("addTaskDeadline").value;
    const status = document.getElementById("addTaskStatus").value;

    if (!student_id) return showFormError(err, "Please select an assigned student.");
    if (!title) return showFormError(err, "Task title is required.");
    if (!deadline) return showFormError(err, "Deadline date is required.");

    submitBtn.disabled = true;
    submitBtn.textContent = "Saving...";

    try {
        const res = await fetch("/api/tasks", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ student_id: parseInt(student_id, 10), title, description, deadline, status })
        });
        const data = await res.json();

        if (!res.ok || !data.success) {
            showFormError(err, data.error || "Failed to create task.");
            return;
        }

        closeModal("addTaskModal");
        showToast("Task assigned successfully!", "success");
        loadTasks();
    } catch (error) {
        showFormError(err, "Network error occurred while creating task.");
        console.error(error);
    } finally {
        submitBtn.disabled = false;
        submitBtn.textContent = "Save Task";
    }
}

// Open Edit Task Modal
async function openEditTaskModal(taskId) {
    const err = document.getElementById("editTaskError");
    err.textContent = "";
    err.style.display = "none";

    try {
        const res = await fetch(`/api/tasks/${taskId}`);
        const data = await res.json();

        if (!res.ok || !data.success) {
            showToast(data.error || "Could not retrieve task details", "error");
            return;
        }

        const t = data.task;
        document.getElementById("editTaskId").value = t.task_id;
        document.getElementById("editTaskStudentName").value = `${t.student_name} (${t.roll_number})`;
        document.getElementById("editTaskTitle").value = t.title;
        document.getElementById("editTaskDesc").value = t.description || "";
        document.getElementById("editTaskDeadline").value = t.deadline;
        document.getElementById("editTaskStatus").value = t.status;

        openModal("editTaskModal");
    } catch (error) {
        showToast("Error loading task information", "error");
        console.error(error);
    }
}

// Handle Edit Task Submission
async function handleEditTask(e) {
    e.preventDefault();
    const err = document.getElementById("editTaskError");
    const submitBtn = document.getElementById("editTaskSubmitBtn");

    const taskId = document.getElementById("editTaskId").value;
    const title = document.getElementById("editTaskTitle").value.trim();
    const description = document.getElementById("editTaskDesc").value.trim();
    const deadline = document.getElementById("editTaskDeadline").value;
    const status = document.getElementById("editTaskStatus").value;

    if (!title) return showFormError(err, "Task title is required.");
    if (!deadline) return showFormError(err, "Deadline date is required.");

    submitBtn.disabled = true;
    submitBtn.textContent = "Updating...";

    try {
        const res = await fetch(`/api/tasks/${taskId}`, {
            method: "PUT",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ title, description, deadline, status })
        });
        const data = await res.json();

        if (!res.ok || !data.success) {
            showFormError(err, data.error || "Failed to update task.");
            return;
        }

        closeModal("editTaskModal");
        showToast("Task updated successfully!", "success");
        loadTasks();
    } catch (error) {
        showFormError(err, "Network error occurred while updating task.");
        console.error(error);
    } finally {
        submitBtn.disabled = false;
        submitBtn.textContent = "Update Task";
    }
}

// Mark Task as Completed
async function markTaskCompleted(taskId) {
    try {
        const res = await fetch(`/api/tasks/${taskId}/complete`, {
            method: "PATCH"
        });
        const data = await res.json();

        if (!res.ok || !data.success) {
            showToast(data.error || "Failed to mark task complete", "error");
            return;
        }

        showToast("Task marked as Completed! 🎉", "success");
        loadTasks();
    } catch (err) {
        showToast("Network error marking task complete.", "error");
        console.error(err);
    }
}

// Open Delete Task Confirmation Modal
function openDeleteTaskModal(taskId, title) {
    pendingDeleteTaskId = taskId;
    document.getElementById("deleteTaskTitle").textContent = `"${title}"`;

    const confirmBtn = document.getElementById("confirmDeleteTaskBtn");
    confirmBtn.onclick = handleConfirmDeleteTask;

    openModal("deleteTaskModal");
}

// Handle Confirmed Task Deletion
async function handleConfirmDeleteTask() {
    if (!pendingDeleteTaskId) return;

    try {
        const res = await fetch(`/api/tasks/${pendingDeleteTaskId}`, {
            method: "DELETE"
        });
        const data = await res.json();

        if (!res.ok || !data.success) {
            showToast(data.error || "Failed to delete task", "error");
            return;
        }

        closeModal("deleteTaskModal");
        showToast("Task deleted successfully.", "success");
        loadTasks();
    } catch (error) {
        showToast("Network error occurred while deleting task.", "error");
        console.error(error);
    } finally {
        pendingDeleteTaskId = null;
    }
}

function showFormError(element, message) {
    element.textContent = message;
    element.style.display = "block";
}
