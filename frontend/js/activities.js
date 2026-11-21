
const API_URL = "/api/activities/";
const token = localStorage.getItem("access_token");

let activities = [];

const table = document.getElementById("activityTable");
const form = document.getElementById("activityForm");
const message = document.getElementById("message");
const modal = new bootstrap.Modal(document.getElementById("activityModal"));

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
        "&": "&amp;", "<": "&lt;", ">": "&gt;",
        '"': "&quot;", "'": "&#39;"
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

    const local = new Date(date.getTime() - date.getTimezoneOffset() * 60000);
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

        await loadActivities();
    } catch (error) {
        showMessage(error.message, "danger");
    }
}

async function loadActivities() {
    try {
        const result = await apiRequest(API_URL);

        activities = Array.isArray(result)
            ? result
            : (result.activities || []);

        displayActivities(activities);
    } catch (error) {
        table.innerHTML =
            `<tr><td colspan="8">${escapeHTML(error.message)}</td></tr>`;
    }
}

function displayActivities(records) {
    if (!records.length) {
        table.innerHTML =
            `<tr><td colspan="8" class="text-center">No activities found.</td></tr>`;
        return;
    }

    table.innerHTML = records.map(item => {
        const id = item._id || item.id;

        return `
        <tr>
            <td>${escapeHTML(item.subject)}</td>
            <td>${escapeHTML(item.activity_type)}</td>
            <td>${escapeHTML(String(item.activity_date || "").replace("T", " ").slice(0, 16))}</td>
            <td>${escapeHTML(item.customer_id || "-")}</td>
            <td>${escapeHTML(item.lead_id || "-")}</td>
            <td>${escapeHTML(item.status || "Planned")}</td>
            <td>${escapeHTML(item.description || "-")}</td>
            <td>
                <button class="btn btn-sm btn-outline-secondary"
                    onclick="editActivity('${id}')">Edit</button>
            </td>
        </tr>`;
    }).join("");
}

function prepareAddActivity() {
    form.reset();
    document.getElementById("activityId").value = "";
    document.getElementById("modalTitle").textContent = "Add Activity";
    document.getElementById("status").value = "Planned";
}

function getActivityData() {
    const dateValue = document.getElementById("activityDate").value;

    return {
        subject: document.getElementById("subject").value.trim(),
        activity_type: document.getElementById("activityType").value,
        activity_date: dateValue ? new Date(dateValue).toISOString() : "",
        customer_id: document.getElementById("customerId").value.trim() || null,
        lead_id: document.getElementById("leadId").value.trim() || null,
        status: document.getElementById("status").value,
        description: document.getElementById("description").value.trim()
    };
}

function editActivity(id) {
    const item = activities.find(activity =>
        String(activity._id || activity.id) === String(id)
    );

    if (!item) {
        showMessage("Activity not found. Refresh and try again.", "danger");
        return;
    }

    document.getElementById("activityId").value = id;
    document.getElementById("subject").value = item.subject || "";
    document.getElementById("activityType").value =
        item.activity_type || "Call";
    document.getElementById("activityDate").value =
        toLocalDateTime(item.activity_date);
    document.getElementById("customerId").value =
        item.customer_id || "";
    document.getElementById("leadId").value =
        item.lead_id || "";
    document.getElementById("status").value =
        item.status || "Planned";
    document.getElementById("description").value =
        item.description || "";

    document.getElementById("modalTitle").textContent = "Edit Activity";
    modal.show();
}

form.addEventListener("submit", async event => {
    event.preventDefault();

    const id = document.getElementById("activityId").value;
    const data = getActivityData();

    if (!data.customer_id && !data.lead_id) {
        showMessage("Enter either a Customer ID or a Lead ID.", "danger");
        return;
    }

    try {
        await apiRequest(id ? `${API_URL}${id}` : API_URL, {
            method: id ? "PUT" : "POST",
            body: JSON.stringify(data)
        });

        modal.hide();
        form.reset();
        await loadActivities();

        showMessage(id
            ? "Activity updated successfully."
            : "Activity created successfully."
        );
    } catch (error) {
        showMessage(error.message, "danger");
    }
});

document.getElementById("searchActivity").addEventListener("input", function () {
    const term = this.value.toLowerCase();

    displayActivities(activities.filter(item =>
        [
            item.subject,
            item.activity_type,
            item.description,
            item.status,
            item.customer_id,
            item.lead_id
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
