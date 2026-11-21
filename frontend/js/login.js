
document.getElementById("loginForm").addEventListener("submit", async function(event) {

    event.preventDefault();

    const username = document.getElementById("username").value;
    const password = document.getElementById("password").value;
    const errorMessage = document.getElementById("errorMessage");

    errorMessage.textContent = "Checking credentials...";
    
    try {

        const response = await fetch("/api/auth/login", {
            method: "POST",

            headers: {
                "Content-Type": "application/json"
            },

            body: JSON.stringify({
                username: username,
                password: password
            })
        });

        const data = await response.json();

        if (!response.ok) {
            throw new Error(data.detail || "Login failed");
        }

        // Save authentication details
        localStorage.setItem("access_token", data.access_token);
        localStorage.setItem("username", data.username);
        localStorage.setItem("role", data.role);

        errorMessage.style.color = "green";
        errorMessage.textContent = "Login successful! Welcome " + data.role;

        console.log("Login successful:", data);

        window.location.href = "/dashboard";

    }

    catch (error) {

        errorMessage.style.color = "red";
        errorMessage.textContent = error.message;

        console.error(error);

    }

});
