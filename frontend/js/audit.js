

const API_URL = "/api/audit/";
const token = localStorage.getItem("access_token");

let auditRecords = [];

const table = document.getElementById("auditTable");
const message = document.getElementById("message");

function escapeHTML(value) {
    return String(value ?? "").replace(/[&<>"']/g, char => ({
        "&": "&amp;",
        "<": "&lt;",
        ">": "&gt;",
        '"': "&quot;",
        "'": "&#39;"
    })[char]);
}

function showMessage(text, type = "danger") {
    message.className = `alert alert-${type} mt-3`;
    message.textContent = text;
}

async function apiRequest(url) {
    const response = await fetch(url, {
        headers: {
            "Authorization": "Bearer " + token
        }
    });

    if (response.status === 401) {
        localStorage.clear();
        window.location.href = "/";
        throw new Error("Session expired.");
    }

    if (!response.ok) {
        const error = await response.json().catch(() => ({}));
        throw new Error(error.detail || "Unable to load audit records.");
    }

    return response.json();
}

async function initializePage() {
    if (!token) {
        window.location.href = "/";
        return;
    }

    try {
        const user = await apiRequest("/api/auth/me");

        document.getElementById("userRole").textContent =
            `${user.username} | ${user.role}`;

        if (user.role !== "Admin") {
            throw new Error("Only Admin users can view audit logs.");
        }

        await loadAuditRecords();

    } catch (error) {
        table.innerHTML = `
            <tr><td colspan="5">${escapeHTML(error.message)}</td></tr>`;
    }
}

async function loadAuditRecords() {
    try {
        const result = await apiRequest(API_URL);

        auditRecords = Array.isArray(result)
            ? result
            : (result.audit_logs || result.records || []);

        displayAuditRecords(auditRecords);

    } catch (error) {
        showMessage(error.message);
    }
}

function displayAuditRecords(records) {
    if (!records.length) {
        table.innerHTML = `
            <tr><td colspan="5" class="text-center">
                No audit records found.
            </td></tr>`;
        return;
    }

    table.innerHTML = records.map(record => {
        const date = record.created_date
            ? new Date(record.created_date).toLocaleString("en-IN")
            : "-";

        return `
        <tr>
            <td>${escapeHTML(record.username)}</td>
            <td>${escapeHTML(record.action)}</td>
            <td>${escapeHTML(record.entity_name)}</td>
            <td>${escapeHTML(record.record_id || "-")}</td>
            <td>${escapeHTML(date)}</td>
        </tr>`;
    }).join("");
}

document.getElementById("searchAudit").addEventListener("input", function () {
    const term = this.value.toLowerCase();

    const filtered = auditRecords.filter(record =>
        [
            record.username,
            record.action,
            record.entity_name,
            record.record_id
        ].some(value =>
            String(value || "").toLowerCase().includes(term)
        )
    );

    displayAuditRecords(filtered);
});

document.getElementById("logoutBtn").addEventListener("click", () => {
    localStorage.clear();
    window.location.href = "/";
});

initializePage();
