
const API_URL = "/api/dashboard/stats";
const token = localStorage.getItem("access_token");

let overviewChart = null;
let opportunityChart = null;

function formatCurrency(value) {
    return "₹" + Number(value || 0).toLocaleString("en-IN");
}

function showMessage(text, type = "danger") {
    const element = document.getElementById("reportMessage");
    element.className = `alert alert-${type}`;
    element.textContent = text;
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
        throw new Error("Session expired. Please log in again.");
    }

    if (!response.ok) {
        const error = await response.json().catch(() => ({}));
        throw new Error(error.detail || "Unable to load reports.");
    }

    return response.json();
}

async function initializeReports() {
    if (!token) {
        window.location.href = "/";
        return;
    }

    try {
        const user = await apiRequest("/api/auth/me");

        document.getElementById("userRole").textContent =
            `${user.username} | ${user.role}`;

        if (!["Admin", "Manager"].includes(user.role)) {
            throw new Error("Reports are available only to Admin and Manager.");
        }

        await loadReports();

    } catch (error) {
        showMessage(error.message);
    }
}

async function loadReports() {
    try {
        const data = await apiRequest(API_URL);

        // KPI values
        document.getElementById("totalCustomers").textContent =
            data.total_customers ?? 0;

        document.getElementById("totalLeads").textContent =
            data.total_leads ?? 0;

        document.getElementById("openOpportunities").textContent =
            data.open_opportunities ?? 0;

        document.getElementById("pipelineValue").textContent =
            formatCurrency(data.pipeline_value);

        document.getElementById("weightedPipeline").textContent =
            formatCurrency(data.weighted_pipeline);

        document.getElementById("wonOpportunities").textContent =
            data.won_opportunities ?? 0;

        document.getElementById("lostOpportunities").textContent =
            data.lost_opportunities ?? 0;

        document.getElementById("pendingFollowups").textContent =
            data.pending_followups ?? 0;

        // Pipeline table
        document.getElementById("tablePipeline").textContent =
            formatCurrency(data.pipeline_value);

        document.getElementById("tableWeighted").textContent =
            formatCurrency(data.weighted_pipeline);

        document.getElementById("tableOpen").textContent =
            data.open_opportunities ?? 0;

        document.getElementById("tableWon").textContent =
            data.won_opportunities ?? 0;

        document.getElementById("tableLost").textContent =
            data.lost_opportunities ?? 0;

        createCharts(data);

        document.getElementById("lastUpdated").textContent =
            "Last updated: " + new Date().toLocaleString("en-IN");

        document.getElementById("reportMessage").textContent = "";

    } catch (error) {
        showMessage(error.message);
    }
}

function createCharts(data) {
    if (overviewChart) overviewChart.destroy();
    if (opportunityChart) opportunityChart.destroy();

    if (typeof Chart === "undefined") {
        showMessage("Chart.js could not be loaded. Check your internet connection.");
        return;
    }

    const overviewCanvas = document.getElementById("overviewChart");
    const opportunityCanvas = document.getElementById("opportunityChart");

    overviewChart = new Chart(overviewCanvas, {
        type: "bar",
        data: {
            labels: [
                "Customers",
                "Leads",
                "Open Opportunities",
                "Pending Follow-Ups"
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
                legend: { display: false }
            }
        }
    });

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

document.getElementById("refreshBtn").addEventListener("click", loadReports);

document.getElementById("logoutBtn").addEventListener("click", () => {
    localStorage.clear();
    window.location.href = "/";
});

initializeReports();
