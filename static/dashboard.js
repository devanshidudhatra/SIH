document.addEventListener("DOMContentLoaded", function () {
    const dashboardContent = document.getElementById("dashboard-content");
    dashboardContent.innerHTML = `
        <p>Welcome to the Cyber Triage Tool Dashboard. Here you can view ongoing investigations, alerts, and more.</p>
        <p><strong>Latest Alerts:</strong></p>
        <ul>
            <li>Suspicious activity detected on 192.168.1.1</li>
            <li>Unauthorized access attempt blocked</li>
        </ul>
    `;
});
