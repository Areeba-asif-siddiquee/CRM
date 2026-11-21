
const token = localStorage.getItem("access_token");

if (!token) {
    window.location.href = "/";
}

let overviewChart = null;
let opportunityChart = null;


// 1. Verify logged-in user
async function initializeDashboard() {
    try {
        const response = await fetch("/api/auth/me", {
            headers: {
                "Authorization": "Bearer " + token
            }
        });

        if (!response.ok) {
            throw new Error("Session expired");
        }

        const user = await response.json();

        document.getElementById("welcomeUser").textContent =
            "Welcome, " + user.username;

        document.getElementById("userRole").textContent =
            user.role;

        showModules(user.role);
        await loadDashboardStats();

    } catch (error) {
        console.error(error);
        localStorage.clear();
        window.location.href = "/";
    }
}


// 2. Role-based module navigation
function showModules(role) {

    const modules = {

        Admin: [
            ["Customers", "/customers"],
            ["Leads", "/leads"],
            ["Opportunities", "/opportunities"],
            ["Follow-Ups", "/followups"],
            ["Activities", "/activities"],
            ["User Management", "/users"],
            ["Audit Log", "/audit"],
            ["Reports", "/reports"]
        ],

        Manager: [
            ["Customers", "/customers"],
            ["Leads", "/leads"],
            ["Opportunities", "/opportunities"],
            ["Follow-Ups", "/followups"],
            ["Activities", "/activities"],
            ["Reports", "/reports"]
        ],

        SalesExecutive: [
            ["My Customers", "/customers"],
            ["My Leads", "/leads"],
            ["My Opportunities", "/opportunities"],
            ["My Follow-Ups", "/followups"],
            ["My Activities", "/activities"]
        ]
    };

    const grid = document.getElementById("modulesGrid");
    grid.innerHTML = "";

    (modules[role] || []).forEach(([name, url]) => {

        grid.innerHTML += `
            <div class="col-md-4 col-lg-3">
                <a href="${url}" class="module-link">
                    <div class="dashboard-card module-card">
                        <h6>${name}</h6>
                        <small>Open module →</small>
                    </div>
                </a>
            </div>
        `;
    });
}


// 3. Load live dashboard statistics
async function loadDashboardStats() {

    const response = await fetch("/api/dashboard/stats", {
        headers: {
            "Authorization": "Bearer " + token
        }
    });

    if (!response.ok) {
        throw new Error("Unable to load dashboard statistics");
    }

    const data = await response.json();

    document.getElementById("totalCustomers").textContent =
        data.total_customers ?? 0;

    document.getElementById("totalLeads").textContent =
        data.total_leads ?? 0;

    document.getElementById("openOpportunities").textContent =
        data.open_opportunities ?? 0;

    document.getElementById("pipelineValue").textContent =
        "₹" + Number(data.pipeline_value || 0).toLocaleString("en-IN");

    document.getElementById("wonOpportunities").textContent =
        data.won_opportunities ?? 0;

    document.getElementById("lostOpportunities").textContent =
        data.lost_opportunities ?? 0;

    document.getElementById("pendingFollowups").textContent =
        data.pending_followups ?? 0;

    createCharts(data);
}


// 4. Create dashboard charts
function createCharts(data) {

    if (overviewChart) overviewChart.destroy();
    if (opportunityChart) opportunityChart.destroy();

    if (typeof Chart === "undefined") {
        console.error("Chart.js is not loaded.");
        return;
    }

    const overviewCanvas =
        document.getElementById("overviewChart");

    const opportunityCanvas =
        document.getElementById("opportunityChart");


    // Overview bar chart
    if (overviewCanvas) {

        overviewChart = new Chart(overviewCanvas, {

            type: "bar",

            data: {
                labels: [
                    "Customers",
                    "Leads",
                    "Open Opportunities",
                    "Follow-ups"
                ],

                datasets: [{
                    label: "Total Records",

                    data: [
                        data.total_customers || 0,
                        data.total_leads || 0,
                        data.open_opportunities || 0,
                        data.pending_followups || 0
                    ],

                    backgroundColor: [
                        "#76624D",
                        "#A48C70",
                        "#C1A98D",
                        "#DED5C8"
                    ],

                    borderRadius: 6
                }]
            },

            options: {
                responsive: true,

                plugins: {
                    legend: {
                        display: false
                    }
                }
            }
        });
    }


    // Opportunity distribution chart
    if (opportunityCanvas) {

        opportunityChart = new Chart(opportunityCanvas, {

            type: "doughnut",

            data: {
                labels: ["Open", "Won", "Lost"],

                datasets: [{
                    data: [
                        data.open_opportunities || 0,
                        data.won_opportunities || 0,
                        data.lost_opportunities || 0
                    ],

                    backgroundColor: [
                        "#76624D",
                        "#A48C70",
                        "#DED5C8"
                    ],

                    borderWidth: 1
                }]
            },

            options: {
                responsive: true
            }
        });
    }
}


// 5. Logout
document.getElementById("logoutBtn").addEventListener("click", () => {

    localStorage.removeItem("access_token");
    localStorage.removeItem("username");
    localStorage.removeItem("role");

    window.location.href = "/";
});


// 6. Start dashboard
initializeDashboard();
