
const API_URL = "/api/leads/";
const token = localStorage.getItem("access_token");

let leads = [];
let currentRole = "";

const table = document.getElementById("leadTable");
const form = document.getElementById("leadForm");
const message = document.getElementById("message");
const modal = new bootstrap.Modal(document.getElementById("leadModal"));

function headers() {
    return {
        "Content-Type": "application/json",
        "Authorization": "Bearer " + token
    };
}

async function apiRequest(url, options = {}) {
    const response = await fetch(url, {
        ...options,
        headers: { ...headers(), ...(options.headers || {}) }
    });

    if (response.status === 401) {
        localStorage.clear();
        window.location.href = "/";
        throw new Error("Session expired");
    }

    if (!response.ok) {
        const error = await response.json().catch(() => ({}));
        throw new Error(error.detail || "Request failed");
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

async function initializePage() {
    if (!token) {
        window.location.href = "/";
        return;
    }

    try {
        const user = await apiRequest("/api/auth/me");
        currentRole = user.role;
        document.getElementById("userRole").textContent =
            `${user.username} | ${user.role}`;

        await loadLeads();
    } catch (error) {
        showMessage(error.message, "danger");
    }
}

async function loadLeads() {
    try {
        const result = await apiRequest(API_URL);
        leads = Array.isArray(result) ? result : (result.leads || []);
        displayLeads(leads);
    } catch (error) {
        table.innerHTML = `<tr><td colspan="8">${escapeHTML(error.message)}</td></tr>`;
    }
}

function displayLeads(records) {
    if (!records.length) {
        table.innerHTML = `<tr><td colspan="8" class="text-center">No leads found.</td></tr>`;
        return;
    }

    table.innerHTML = records.map(lead => {
        const id = lead._id || lead.id;

        return `
        <tr>
            <td>${escapeHTML(lead.lead_name)}</td>
            <td>${escapeHTML(lead.company_name || "-")}</td>
            <td>${escapeHTML(lead.email || "-")}</td>
            <td>${escapeHTML(lead.phone || "-")}</td>
            <td>${escapeHTML(lead.source || "-")}</td>
            <td>${escapeHTML(lead.status || "New")}</td>
            <td>₹${Number(lead.expected_value || 0).toLocaleString("en-IN")}</td>
            <td>
                <button class="btn btn-sm btn-outline-secondary me-1"
                    onclick="editLead('${id}')">Edit</button>
                ${lead.status !== "Lost" && lead.status !== "Converted" ? `
                <button class="btn btn-sm btn-outline-danger"
                    onclick="markLeadLost('${id}')">Mark Lost</button>` : ""}
            </td>
        </tr>`;
    }).join("");
}

function prepareAddLead() {
    form.reset();
    document.getElementById("leadId").value = "";
    document.getElementById("modalTitle").textContent = "Add Lead";
    document.getElementById("expectedValue").value = 0;
}

function getLeadData() {
    return {
        lead_name: document.getElementById("leadName").value.trim(),
        email: document.getElementById("email").value.trim() || null,
        phone: document.getElementById("phone").value.trim() || null,
        company_name: document.getElementById("companyName").value.trim(),
        source: document.getElementById("source").value,
        status: document.getElementById("status").value,
        expected_value: Number(document.getElementById("expectedValue").value || 0),
        notes: document.getElementById("notes").value.trim()
    };
}

async function editLead(id) {
    try {
        const lead = await apiRequest(`${API_URL}${id}`);

        document.getElementById("leadId").value = id;
        document.getElementById("leadName").value = lead.lead_name || "";
        document.getElementById("email").value = lead.email || "";
        document.getElementById("phone").value = lead.phone || "";
        document.getElementById("companyName").value = lead.company_name || "";
        document.getElementById("source").value = lead.source || "Other";
        document.getElementById("status").value = lead.status || "New";
        document.getElementById("expectedValue").value = lead.expected_value || 0;
        document.getElementById("notes").value = lead.notes || "";

        document.getElementById("modalTitle").textContent = "Edit Lead";
        modal.show();
    } catch (error) {
        showMessage(error.message, "danger");
    }
}

form.addEventListener("submit", async event => {
    event.preventDefault();

    const id = document.getElementById("leadId").value;
    const data = getLeadData();

    try {
        await apiRequest(id ? `${API_URL}${id}` : API_URL, {
            method: id ? "PUT" : "POST",
            body: JSON.stringify(data)
        });

        modal.hide();
        form.reset();
        await loadLeads();
        showMessage(id ? "Lead updated successfully." : "Lead added successfully.");
    } catch (error) {
        showMessage(error.message, "danger");
    }
});

async function markLeadLost(id) {
    if (!confirm("Are you sure you want to mark this lead as lost?")) return;

    try {
        await apiRequest(`${API_URL}${id}`, { method: "DELETE" });
        await loadLeads();
        showMessage("Lead marked as lost.");
    } catch (error) {
        showMessage(error.message, "danger");
    }
}

document.getElementById("searchLead").addEventListener("input", function () {
    const term = this.value.toLowerCase();

    displayLeads(leads.filter(lead =>
        [lead.lead_name, lead.email, lead.company_name, lead.phone]
            .some(value => String(value || "").toLowerCase().includes(term))
    ));
});

document.getElementById("logoutBtn").addEventListener("click", () => {
    localStorage.clear();
    window.location.href = "/";
});

initializePage();
