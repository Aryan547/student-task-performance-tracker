/**
 * Module 3: Performance Dashboard Frontend Logic
 */

let taskChartInstance = null;

document.addEventListener("DOMContentLoaded", () => {
    loadDashboard();
});

// Fetch aggregate performance statistics from /api/dashboard/stats
async function loadDashboard() {
    try {
        const res = await fetch("/api/dashboard/stats");
        const data = await res.json();

        if (!data.success) {
            showToast(data.error || "Failed to load dashboard metrics", "error");
            return;
        }

        const stats = data.stats;
        renderMetrics(stats);
        renderChart(stats.completed_tasks, stats.pending_tasks);
        renderStudentBreakdown(stats.student_performance || []);
    } catch (err) {
        showToast("Network error loading dashboard statistics.", "error");
        console.error(err);
    }
}

// Render metric cards and completion progress
function renderMetrics(stats) {
    document.getElementById("statTotalStudents").textContent = stats.total_students || 0;
    document.getElementById("statTotalTasks").textContent = stats.total_tasks || 0;
    document.getElementById("statCompletedTasks").textContent = stats.completed_tasks || 0;
    document.getElementById("statPendingTasks").textContent = stats.pending_tasks || 0;

    const percentage = stats.completion_percentage !== undefined ? stats.completion_percentage : 0;
    document.getElementById("completionPercentNumber").textContent = percentage;
    document.getElementById("completionProgressBar").style.width = `${Math.min(100, Math.max(0, percentage))}%`;
    document.getElementById("progressSummaryText").textContent = 
        `${stats.completed_tasks || 0} of ${stats.total_tasks || 0} tasks completed`;
}

// Render Chart.js task status chart
function renderChart(completed, pending) {
    const canvas = document.getElementById("taskStatusChart");
    const fallback = document.getElementById("chartFallbackMessage");

    if (!canvas) return;

    // Check if there are no tasks
    if (completed === 0 && pending === 0) {
        canvas.classList.add("hidden");
        fallback.classList.remove("hidden");
        if (taskChartInstance) {
            taskChartInstance.destroy();
            taskChartInstance = null;
        }
        return;
    }

    canvas.classList.remove("hidden");
    fallback.classList.add("hidden");

    if (typeof Chart === "undefined") {
        fallback.textContent = "Chart library could not be loaded. Please check internet connection.";
        fallback.classList.remove("hidden");
        canvas.classList.add("hidden");
        return;
    }

    const ctx = canvas.getContext("2d");

    if (taskChartInstance) {
        taskChartInstance.destroy();
    }

    taskChartInstance = new Chart(ctx, {
        type: "doughnut",
        data: {
            labels: ["Completed Tasks", "Pending Tasks"],
            datasets: [{
                data: [completed, pending],
                backgroundColor: ["#10b981", "#f59e0b"],
                hoverBackgroundColor: ["#059669", "#d97706"],
                borderWidth: 2,
                borderColor: "#ffffff"
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    position: "bottom",
                    labels: {
                        boxWidth: 14,
                        padding: 18,
                        font: {
                            family: "'Inter', sans-serif",
                            size: 12
                        }
                    }
                },
                tooltip: {
                    callbacks: {
                        label: function(context) {
                            const total = completed + pending;
                            const value = context.parsed;
                            const pct = total > 0 ? Math.round((value / total) * 100) : 0;
                            return ` ${context.label}: ${value} (${pct}%)`;
                        }
                    }
                }
            },
            cutout: "68%"
        }
    });
}

// Render student breakdown table
function renderStudentBreakdown(students) {
    const tbody = document.getElementById("studentPerformanceBody");
    if (!tbody) return;

    if (students.length === 0) {
        tbody.innerHTML = `
            <tr>
                <td colspan="7" class="text-center" style="padding: 1.5rem; color: #64748b;">
                    No student performance data available. Enrol students and assign tasks to view breakdown.
                </td>
            </tr>
        `;
        return;
    }

    tbody.innerHTML = students.map(s => {
        const rate = s.completion_rate !== undefined ? s.completion_rate : 0;
        let rateColor = "#64748b";
        if (rate >= 80) rateColor = "#10b981";
        else if (rate >= 50) rateColor = "#2563eb";
        else if (rate > 0) rateColor = "#f59e0b";

        return `
            <tr>
                <td><strong>${escapeHtml(s.name)}</strong></td>
                <td><code style="background:#f1f5f9; padding:0.15rem 0.4rem; border-radius:4px; font-weight:600;">${escapeHtml(s.roll_number)}</code></td>
                <td>${escapeHtml(s.course)}</td>
                <td><strong>${s.total_assigned}</strong></td>
                <td><span style="color:#047857; font-weight:600;">${s.total_completed}</span></td>
                <td><span style="color:#b45309; font-weight:600;">${s.total_pending}</span></td>
                <td>
                    <div style="display:flex; align-items:center; gap:0.5rem;">
                        <div style="flex:1; max-width:80px; height:8px; background:#e2e8f0; border-radius:999px; overflow:hidden;">
                            <div style="width:${rate}%; height:100%; background:${rateColor}; border-radius:999px;"></div>
                        </div>
                        <span style="font-weight:600; font-size:0.85rem; color:${rateColor};">${rate}%</span>
                    </div>
                </td>
            </tr>
        `;
    }).join("");
}
