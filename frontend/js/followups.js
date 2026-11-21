
const API_URL = "/api/followups/";
const token = localStorage.getItem("access_token");

let followups = [];

const table = document.getElementById("followupTable");
const form = document.getElementById("followupForm");
const message = document.getElementById("message");
const modal = new bootstrap.Modal(document.getElementById("followupModal"));

function getHeaders() {
    return {
        "Content-Type": "application/json",
        "Authorization": "Bearer " + token
    };
}

async function apiRequest(url, options = {}) {
    const response = await fetch(url, {
        ...options,
        headers: { ...getHeaders(), ...(options.headers || {}) }
    });

    if (response.status === 401) {
        localStorage.clear();
        window.location.href = "/";
        throw new Error("Session expired. Please log in again.");
    }

    if (!response.ok) {
        const error = await response.json().catch(() => ({}));
        throw new Error(error.detail || "Request failed.");
    }

    if (response.status === 204) return null;
    return response.json();
}

function escapeHTML(value) {
    return String(value ?? "").replace(/[&<>"']/g, char => ({
        "&": "&amp;",
        "<": "&lt;",
        ">": "&gt;",
        '"': "&quot;",
        "'": "&#39;"
    })[char]);
}

function showMessage(text, type = "success") {
    message.className = `alert alert-${type} mt-3`;
    message.textContent = text;

    setTimeout(() => {
        message.textContent = "";
        message.className = "mt-3";
    }, 4000);
}

function toLocalDateTime(value) {
    if (!value) return "";

    const date = new Date(value);
    if (Number.isNaN(date.getTime())) return String(value).slice(0, 16);

    const offset = date.getTimezoneOffset();
    const local = new Date(date.getTime() - offset * 60000);
    return local.toISOString().slice(0, 16);
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

        await loadFollowups();
    } catch (error) {
        showMessage(error.message, "danger");
    }
}

async function loadFollowups() {
    try {
        const result = await apiRequest(API_URL);
        followups = Array.isArray(result)
            ? result
            : (result.followups || []);

        displayFollowups(followups);
    } catch (error) {
        table.innerHTML =
            `<tr><td colspan="7">${escapeHTML(error.message)}</td></tr>`;
    }
}

function displayFollowups(records) {
    if (!records.length) {
        table.innerHTML =
            `<tr><td colspan="7" class="text-center">No follow-ups found.</td></tr>`;
        return;
    }

    table.innerHTML = records.map(item => {
        const id = item._id || item.id;
        const date = item.followup_date || "";

        return `
        <tr>
            <td>${escapeHTML(item.subject)}</td>
            <td>${escapeHTML(item.customer_id)}</td>
            <td>${escapeHTML(String(date).replace("T", " ").slice(0, 16))}</td>
            <td>${escapeHTML(item.followup_type)}</td>
            <td>${escapeHTML(item.status || "Planned")}</td>
            <td>${escapeHTML(item.remarks || "-")}</td>
            <td>
                <button class="btn btn-sm btn-outline-secondary me-1"
                    onclick="editFollowup('${id}')">Edit</button>
                ${item.status === "Planned" ? `
                <button class="btn btn-sm btn-outline-success"
                    onclick="completeFollowup('${id}')">Complete</button>
                ` : ""}
            </td>
        </tr>`;
    }).join("");
}

function prepareAddFollowup() {
    form.reset();
    document.getElementById("followupId").value = "";
    document.getElementById("modalTitle").textContent = "Add Follow-Up";
    document.getElementById("status").value = "Planned";
}

function getFollowupData() {
    const dateValue = document.getElementById("followupDate").value;

    return {
        customer_id: document.getElementById("customerId").value.trim(),
        subject: document.getElementById("subject").value.trim(),
        followup_date: dateValue ? new Date(dateValue).toISOString() : "",
        followup_type: document.getElementById("followupType").value,
        status: document.getElementById("status").value,
        remarks: document.getElementById("remarks").value.trim()
    };
}

async function editFollowup(id) {
    try {
        const item = await apiRequest(`${API_URL}${id}`);

        document.getElementById("followupId").value = id;
        document.getElementById("customerId").value = item.customer_id || "";
        document.getElementById("subject").value = item.subject || "";
        document.getElementById("followupDate").value =
            toLocalDateTime(item.followup_date);
        document.getElementById("followupType").value =
            item.followup_type || "Call";
        document.getElementById("status").value =
            item.status || "Planned";
        document.getElementById("remarks").value = item.remarks || "";

        document.getElementById("modalTitle").textContent = "Edit Follow-Up";
        modal.show();
    } catch (error) {
        showMessage(error.message, "danger");
    }
}

form.addEventListener("submit", async event => {
    event.preventDefault();

    const id = document.getElementById("followupId").value;
    const data = getFollowupData();

    try {
        await apiRequest(id ? `${API_URL}${id}` : API_URL, {
            method: id ? "PUT" : "POST",
            body: JSON.stringify(data)
        });

        modal.hide();
        form.reset();
        await loadFollowups();

        showMessage(id
            ? "Follow-up updated successfully."
            : "Follow-up created successfully."
        );
    } catch (error) {
        showMessage(error.message, "danger");
    }
});

async function completeFollowup(id) {
    if (!confirm("Mark this follow-up as completed?")) return;

    try {
        await apiRequest(`${API_URL}${id}`, {
            method: "PUT",
            body: JSON.stringify({ status: "Completed" })
        });

        await loadFollowups();
        showMessage("Follow-up completed successfully.");
    } catch (error) {
        showMessage(error.message, "danger");
    }
}

document.getElementById("searchFollowup").addEventListener("input", function () {
    const term = this.value.toLowerCase();

    displayFollowups(followups.filter(item =>
        [
            item.subject,
            item.customer_id,
            item.followup_type,
            item.status,
            item.remarks
        ].some(value =>
            String(value || "").toLowerCase().includes(term)
        )
    ));
});

document.getElementById("logoutBtn").addEventListener("click", () => {
    localStorage.clear();
    window.location.href = "/";
});

initializePage();
