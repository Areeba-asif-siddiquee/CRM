
const API_URL = "/api/users/";
const token = localStorage.getItem("access_token");

let allUsers = [];
let userModal;

document.addEventListener("DOMContentLoaded", async () => {
    if (!token) {
        window.location.href = "/";
        return;
    }

    userModal = new bootstrap.Modal(document.getElementById("userModal"));

    document.getElementById("userForm").addEventListener("submit", saveUser);
    document.getElementById("searchUser").addEventListener("input", filterUsers);
    document.getElementById("logoutBtn").addEventListener("click", logout);

    await checkAdmin();
});

async function apiRequest(url, options = {}) {
    const response = await fetch(url, {
        ...options,
        headers: {
            "Content-Type": "application/json",
            "Authorization": `Bearer ${token}`,
            ...(options.headers || {})
        }
    });

    if (response.status === 401) {
        logout();
        throw new Error("Session expired. Please log in again.");
    }

    const data = await response.json().catch(() => ({}));

    if (!response.ok) {
        throw new Error(data.detail || "Something went wrong.");
    }

    return data;
}

async function checkAdmin() {
    try {
        const user = await apiRequest("/api/auth/me");

        if (user.role !== "Admin") {
            alert("Only Admin users can access User Management.");
            window.location.href = "/dashboard";
            return;
        }

        document.getElementById("adminName").textContent =
            user.username + " (Admin)";

        await loadUsers();

    } catch (error) {
        showMessage(error.message, "danger");
    }
}

async function loadUsers() {
    try {
        allUsers = await apiRequest(API_URL);
        renderUsers(allUsers);
    } catch (error) {
        showMessage(error.message, "danger");
    }
}

function renderUsers(users) {
    const tbody = document.getElementById("usersTableBody");

    if (!users.length) {
        tbody.innerHTML = `
            <tr>
                <td colspan="6" class="text-center text-muted">
                    No users found.
                </td>
            </tr>`;
        return;
    }

    tbody.innerHTML = users.map((user, index) => {
        const id = escapeHTML(user._id || "");
        const username = escapeHTML(user.username || "");
        const fullName = escapeHTML(user.full_name || "-");
        const role = escapeHTML(user.role || "-");
        const active = user.is_active !== false;

        return `
            <tr>
                <td>${index + 1}</td>
                <td>${username}</td>
                <td>${fullName}</td>
                <td>${role}</td>
                <td>
                    <span class="badge ${active ? "status-active" : "status-inactive"}">
                        ${active ? "Active" : "Inactive"}
                    </span>
                </td>
                <td>
                    <button class="btn btn-sm btn-outline-secondary me-1"
                        onclick="editUser('${id}')">
                        Edit
                    </button>

                    ${active ? `
                        <button class="btn btn-sm btn-outline-danger"
                            onclick="deactivateUser('${id}')">
                            Deactivate
                        </button>` : ""}
                </td>
            </tr>`;
    }).join("");
}

function filterUsers() {
    const search = document.getElementById("searchUser").value.toLowerCase();

    const filtered = allUsers.filter(user =>
        (user.username || "").toLowerCase().includes(search) ||
        (user.full_name || "").toLowerCase().includes(search)
    );

    renderUsers(filtered);
}

function openAddModal() {
    document.getElementById("userForm").reset();
    document.getElementById("userId").value = "";
    document.getElementById("username").disabled = false;
    document.getElementById("passwordGroup").classList.remove("d-none");
    document.getElementById("password").required = true;
    document.getElementById("statusGroup").classList.add("d-none");
    document.getElementById("modalTitle").textContent = "Add New User";
    document.getElementById("formError").textContent = "";
}

function editUser(id) {
    const user = allUsers.find(item => item._id === id);

    if (!user) return;

    document.getElementById("userForm").reset();
    document.getElementById("userId").value = id;
    document.getElementById("username").value = user.username || "";
    document.getElementById("username").disabled = true;
    document.getElementById("fullName").value = user.full_name || "";
    document.getElementById("userRole").value = user.role || "SalesExecutive";

    document.getElementById("passwordGroup").classList.add("d-none");
    document.getElementById("password").required = false;

    document.getElementById("statusGroup").classList.remove("d-none");
    document.getElementById("userStatus").value =
        user.is_active === false ? "false" : "true";

    document.getElementById("modalTitle").textContent = "Edit User";
    document.getElementById("formError").textContent = "";

    userModal.show();
}

async function saveUser(event) {
    event.preventDefault();

    const id = document.getElementById("userId").value;
    const formError = document.getElementById("formError");

    const payload = {
        full_name: document.getElementById("fullName").value.trim(),
        role: document.getElementById("userRole").value
    };

    if (!id) {
        payload.username = document.getElementById("username").value.trim();
        payload.password = document.getElementById("password").value;
    } else {
        payload.is_active =
            document.getElementById("userStatus").value === "true";
    }

    try {
        if (id) {
            await apiRequest(`${API_URL}${id}`, {
                method: "PUT",
                body: JSON.stringify(payload)
            });
        } else {
            await apiRequest(API_URL, {
                method: "POST",
                body: JSON.stringify(payload)
            });
        }

        userModal.hide();
        showMessage(id ? "User updated successfully." : "User created successfully.", "success");
        await loadUsers();

    } catch (error) {
        formError.textContent = error.message;
    }
}

async function deactivateUser(id) {
    const user = allUsers.find(item => item._id === id);

    if (!user) return;

    if (!confirm(`Deactivate user "${user.username}"?`)) return;

    try {
        await apiRequest(`${API_URL}${id}`, {
            method: "DELETE"
        });

        showMessage("User deactivated successfully.", "success");
        await loadUsers();

    } catch (error) {
        showMessage(error.message, "danger");
    }
}

function showMessage(message, type) {
    const box = document.getElementById("messageBox");
    box.textContent = message;
    box.className = `alert alert-${type}`;
    box.classList.remove("d-none");

    setTimeout(() => box.classList.add("d-none"), 4000);
}

function escapeHTML(value) {
    return String(value).replace(/[&<>"']/g, char => ({
        "&": "&amp;",
        "<": "&lt;",
        ">": "&gt;",
        '"': "&quot;",
        "'": "&#39;"
    })[char]);
}

function logout() {
    localStorage.clear();
    window.location.href = "/";
}
