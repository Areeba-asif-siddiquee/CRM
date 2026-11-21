
const API_URL = "/api/opportunities/";
const token = localStorage.getItem("access_token");

let opportunities = [];

const table = document.getElementById("opportunityTable");
const form = document.getElementById("opportunityForm");
const message = document.getElementById("message");
const modal = new bootstrap.Modal(
    document.getElementById("opportunityModal")
);

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

async function initializePage() {
    if (!token) {
        window.location.href = "/";
        return;
    }

    try {
        const user = await apiRequest("/api/auth/me");

        document.getElementById("userRole").textContent =
            `${user.username} | ${user.role}`;

        await loadOpportunities();

    } catch (error) {
        showMessage(error.message, "danger");
    }
}

async function loadOpportunities() {
    try {
        const result = await apiRequest(API_URL);

        opportunities = Array.isArray(result)
            ? result
            : (result.opportunities || []);

        displayOpportunities(opportunities);

    } catch (error) {
        table.innerHTML = `
            <tr><td colspan="8">${escapeHTML(error.message)}</td></tr>`;
    }
}

function displayOpportunities(records) {
    if (!records.length) {
        table.innerHTML = `
            <tr><td colspan="8" class="text-center">No opportunities found.</td></tr>`;
        return;
    }

    table.innerHTML = records.map(item => {
        const id = item._id || item.id;

        return `
        <tr>
            <td>${escapeHTML(item.opportunity_name)}</td>
            <td>${escapeHTML(item.customer_id)}</td>
            <td>₹${Number(item.amount || 0).toLocaleString("en-IN")}</td>
            <td>${escapeHTML(item.stage)}</td>
            <td>${Number(item.probability || 0)}%</td>
            <td>₹${Number(item.weighted_value || 0).toLocaleString("en-IN")}</td>
            <td>${escapeHTML(item.expected_close_date || "-")}</td>
            <td>
                <button class="btn btn-sm btn-outline-secondary me-1"
                    onclick="editOpportunity('${id}')">Edit</button>

                ${item.stage !== "Won" && item.stage !== "Lost" ? `
                <button class="btn btn-sm btn-outline-danger"
                    onclick="markOpportunityLost('${id}')">Mark Lost</button>
                ` : ""}
            </td>
        </tr>`;
    }).join("");
}

function prepareAddOpportunity() {
    form.reset();

    document.getElementById("opportunityId").value = "";
    document.getElementById("modalTitle").textContent = "Add Opportunity";
    document.getElementById("probability").value = 50;
}

function getOpportunityData() {
    return {
        opportunity_name: document.getElementById("opportunityName").value.trim(),
        customer_id: document.getElementById("customerId").value.trim(),
        amount: Number(document.getElementById("amount").value),
        stage: document.getElementById("stage").value,
        probability: Number(document.getElementById("probability").value),
        expected_close_date: document.getElementById("expectedCloseDate").value,
        notes: document.getElementById("notes").value.trim()
    };
}

async function editOpportunity(id) {
    try {
        const item = await apiRequest(`${API_URL}${id}`);

        document.getElementById("opportunityId").value = id;
        document.getElementById("opportunityName").value = item.opportunity_name || "";
        document.getElementById("customerId").value = item.customer_id || "";
        document.getElementById("amount").value = item.amount || "";
        document.getElementById("stage").value = item.stage || "Qualification";
        document.getElementById("probability").value = item.probability ?? 50;
        document.getElementById("expectedCloseDate").value =
            String(item.expected_close_date || "").slice(0, 10);
        document.getElementById("notes").value = item.notes || "";

        document.getElementById("modalTitle").textContent = "Edit Opportunity";
        modal.show();

    } catch (error) {
        showMessage(error.message, "danger");
    }
}

form.addEventListener("submit", async event => {
    event.preventDefault();

    const id = document.getElementById("opportunityId").value;
    const data = getOpportunityData();

    if (!data.customer_id) {
        showMessage("Customer ID is required.", "danger");
        return;
    }

    if (data.amount <= 0) {
        showMessage("Amount must be greater than zero.", "danger");
        return;
    }

    if (data.probability < 0 || data.probability > 100) {
        showMessage("Probability must be between 0 and 100.", "danger");
        return;
    }

    try {
        await apiRequest(id ? `${API_URL}${id}` : API_URL, {
            method: id ? "PUT" : "POST",
            body: JSON.stringify(data)
        });

        modal.hide();
        form.reset();

        await loadOpportunities();

        showMessage(
            id ? "Opportunity updated successfully." :
                 "Opportunity added successfully."
        );

    } catch (error) {
        showMessage(error.message, "danger");
    }
});

async function markOpportunityLost(id) {
    if (!confirm("Are you sure you want to mark this opportunity as lost?")) {
        return;
    }

    try {
        await apiRequest(`${API_URL}${id}`, {
            method: "DELETE"
        });

        await loadOpportunities();
        showMessage("Opportunity marked as lost.");

    } catch (error) {
        showMessage(error.message, "danger");
    }
}

document.getElementById("searchOpportunity").addEventListener("input", function () {
    const term = this.value.toLowerCase();

    displayOpportunities(opportunities.filter(item =>
        [
            item.opportunity_name,
            item.stage,
            item.customer_id
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
