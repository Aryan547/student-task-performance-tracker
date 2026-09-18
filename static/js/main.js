/**
 * Main Shared Utilities for Student Task & Performance Tracker
 */

// Toast notification manager
function showToast(message, type = "info", duration = 3500) {
    const container = document.getElementById("toast-container");
    if (!container) return;

    const toast = document.createElement("div");
    toast.className = `toast toast-${type}`;
    
    let icon = "ℹ️";
    if (type === "success") icon = "✅";
    if (type === "error") icon = "❌";
    if (type === "warning") icon = "⚠️";

    toast.innerHTML = `
        <div style="display:flex; align-items:center; gap:0.5rem;">
            <span>${icon}</span>
            <span>${escapeHtml(message)}</span>
        </div>
        <button style="background:none; border:none; cursor:pointer; color:#94a3b8; font-size:1.1rem; line-height:1;" onclick="this.parentElement.remove()">&times;</button>
    `;

    container.appendChild(toast);

    setTimeout(() => {
        if (toast.parentElement) {
            toast.style.transition = "opacity 0.3s ease, transform 0.3s ease";
            toast.style.opacity = "0";
            toast.style.transform = "translateX(100%)";
            setTimeout(() => toast.remove(), 300);
        }
    }, duration);
}

// Modal management
function openModal(modalId) {
    const modal = document.getElementById(modalId);
    if (modal) {
        modal.classList.add("active");
    }
}

function closeModal(modalId) {
    const modal = document.getElementById(modalId);
    if (modal) {
        modal.classList.remove("active");
        // Clear error box if present
        const err = modal.querySelector(".form-error");
        if (err) {
            err.textContent = "";
            err.style.display = "none";
        }
    }
}

// Close modals when clicking on the backdrop
window.addEventListener("click", function(event) {
    if (event.target.classList.contains("modal")) {
        event.target.classList.remove("active");
        const err = event.target.querySelector(".form-error");
        if (err) {
            err.textContent = "";
            err.style.display = "none";
        }
    }
});

// Close modal on Escape key
window.addEventListener("keydown", function(event) {
    if (event.key === "Escape") {
        document.querySelectorAll(".modal.active").forEach(modal => {
            modal.classList.remove("active");
        });
    }
});

// HTML escaping helper for XSS prevention
function escapeHtml(text) {
    if (!text) return "";
    return String(text)
        .replace(/&/g, "&amp;")
        .replace(/</g, "&lt;")
        .replace(/>/g, "&gt;")
        .replace(/"/g, "&quot;")
        .replace(/'/g, "&#039;");
}
