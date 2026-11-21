
const API_URL = "/api/customers/";
const token = localStorage.getItem("access_token");

let customers = [];
let currentRole = "";

const table = document.getElementById("customerTable");
const searchInput = document.getElementById("searchCustomer");
const form = document.getElementById("customerForm");
const message = document.getElementById("message");

const modalElement = document.getElementById("customerModal");
const customerModal = new bootstrap.Modal(modalElement);

function authHeaders() {
    return {
        "Content-Type": "application/json",
        "Authorization": `Bearer ${token}`
    };
}

async function apiRequest(url, options = {}) {
    const response = await fetch(url, {
        ...options,
        headers: {
            ...authHeaders(),
            ...(options.headers || {})
        }
    });

    if (response.status === 401) {
        localStorage.clear();
        window.location.href = "/";
        throw new Error("Session expired. Please log in again.");
    }

    if (!response.ok) {
        const error = await response.json().catch(() => ({}));
        throw new Error(error.detail || "Something went wrong.");
    }

    if (response.status === 204) return null;
    return response.json();
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

        // Sales executives cannot deactivate customers.
        if (currentRole === "SalesExecutive") {
            document.querySelector('[data-bs-target="#customerModal"]').style.display = "inline-block";
        }

        await loadCustomers();
    } catch (error) {
        showMessage(error.message, "danger");
    }
}

async function loadCustomers() {
    try {
        const result = await apiRequest(API_URL);
        customers = Array.isArray(result) ? result : (result.customers || []);
        displayCustomers(customers);
    } catch (error) {
        table.innerHTML = `<tr><td colspan="6" class="text-danger">${escapeHTML(error.message)}</td></tr>`;
    }
}

function displayCustomers(records) {
    if (!records.length) {
        table.innerHTML = `
            <tr>
                <td colspan="6" class="text-center text-muted">
                    No customers found.
                </td>
            </tr>`;
        return;
    }

    table.innerHTML = records.map(customer => {
        const id = customer._id || customer.id;

        return `
            <tr>
                <td>${escapeHTML(customer.customer_name || "")}</td>
                <td>${escapeHTML(customer.company_name || "-")}</td>
                <td>${escapeHTML(customer.email || "")}</td>
                <td>${escapeHTML(customer.phone || "")}</td>
                <td>
                    <span class="badge ${customer.status === "Active" ? "bg-success" : "bg-secondary"}">
                        ${escapeHTML(customer.status || "Active")}
                    </span>
                </td>
                <td>
                    <button class="btn btn-sm btn-outline-secondary me-1"
                        onclick="editCustomer('${id}')">Edit</button>

                    ${currentRole !== "SalesExecutive" && customer.status !== "Inactive" ? `
                    <button class="btn btn-sm btn-outline-danger"
                        onclick="deactivateCustomer('${id}')">Deactivate</button>
                    ` : ""}
                </td>
            </tr>`;
    }).join("");
}

function escapeHTML(value) {
    return String(value).replace(/[&<>"']/g, character => ({
        "&": "&amp;",
        "<": "&lt;",
        ">": "&gt;",
        '"': "&quot;",
        "'": "&#39;"
    })[character]);
}

function showMessage(text, type = "success") {
    message.className = `mt-3 alert alert-${type}`;
    message.textContent = text;

    setTimeout(() => {
        message.textContent = "";
        message.className = "mt-3";
    }, 4000);
}

function prepareAddCustomer() {
    form.reset();
    document.getElementById("customerId").value = "";
    document.getElementById("modalTitle").textContent = "Add Customer";
}

async function editCustomer(id) {
    try {
        const customer = await apiRequest(`${API_URL}${id}`);

        document.getElementById("customerId").value = id;
        document.getElementById("customerName").value = customer.customer_name || "";
        document.getElementById("email").value = customer.email || "";
        document.getElementById("phone").value = customer.phone || "";
        document.getElementById("companyName").value = customer.company_name || "";
        document.getElementById("address").value = customer.address || "";
        document.getElementById("city").value = customer.city || "";
        document.getElementById("state").value = customer.state || "";

        document.getElementById("modalTitle").textContent = "Edit Customer";
        customerModal.show();
    } catch (error) {
        showMessage(error.message, "danger");
    }
}

form.addEventListener("submit", async function (event) {
    event.preventDefault();

    const id = document.getElementById("customerId").value;

    const customerData = {
        customer_name: document.getElementById("customerName").value.trim(),
        email: document.getElementById("email").value.trim(),
        phone: document.getElementById("phone").value.trim(),
        company_name: document.getElementById("companyName").value.trim(),
        address: document.getElementById("address").value.trim(),
        city: document.getElementById("city").value.trim(),
        state: document.getElementById("state").value.trim()
    };

    try {
        if (id) {
            await apiRequest(`${API_URL}${id}`, {
                method: "PUT",
                body: JSON.stringify(customerData)
            });
            showMessage("Customer updated successfully.");
        } else {
            await apiRequest(API_URL, {
                method: "POST",
                body: JSON.stringify(customerData)
            });
            showMessage("Customer added successfully.");
        }

        customerModal.hide();
        form.reset();
        await loadCustomers();

    } catch (error) {
        showMessage(error.message, "danger");
    }
});

async function deactivateCustomer(id) {
    if (!confirm("Are you sure you want to deactivate this customer?")) {
        return;
    }

    try {
        await apiRequest(`${API_URL}${id}`, {
            method: "DELETE"
        });

        showMessage("Customer deactivated successfully.");
        await loadCustomers();

    } catch (error) {
        showMessage(error.message, "danger");
    }
}

searchInput.addEventListener("input", function () {
    const term = this.value.toLowerCase();

    const filtered = customers.filter(customer =>
        [
            customer.customer_name,
            customer.email,
            customer.phone,
            customer.company_name
        ].some(value => String(value || "").toLowerCase().includes(term))
    );

    displayCustomers(filtered);
});

document.getElementById("logoutBtn").addEventListener("click", function () {
    localStorage.clear();
    window.location.href = "/";
});

initializePage();
