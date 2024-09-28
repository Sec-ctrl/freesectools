
document.addEventListener('DOMContentLoaded', function() {
    // Get the elements
    const ipAddress = document.getElementById('ip-address');
    const toggleIcon = document.getElementById('toggle-ip');

    // Function to toggle blur and icon
    toggleIcon.addEventListener('click', function() {
        // Toggle blur on the IP address
        ipAddress.classList.toggle('blurred');

        // Toggle the icon between eye and eye-slash
        if (ipAddress.classList.contains('blurred')) {
            // Eye-slash icon (IP is blurred)
            toggleIcon.innerHTML = `
                <path d="M572.52 241.4C518.4 135.4 407.3 64 288 64 168.7 64 57.6 135.4 3.48 241.4c-4.65 9.3-4.65 20.5 0 29.8C57.6 376.6 168.7 448 288 448c119.3 0 230.4-71.4 284.52-177.4 4.65-9.3 4.65-20.5 0-29.8zM288 384c-79.4 0-144-64.6-144-144s64.6-144 144-144 144 64.6 144 144-64.6 144-144 144zm0-224c-44.2 0-80 35.8-80 80s35.8 80 80 80 80-35.8 80-80-35.8-80-80-80z"/>
            `;
        } else {
            // Eye icon (IP is visible)
            toggleIcon.innerHTML = `
                <path d="M288 144c78.6 0 143.1 65.2 152.6 144-9.5 78.8-74 144-152.6 144-78.6 0-143.1-65.2-152.6-144 9.5-78.8 74-144 152.6-144zm0-64c-146.4 0-272.6 99.6-288 231.9-1.3 11.8-1.3 23.7 0 35.5C15.4 364.4 141.6 464 288 464s272.6-99.6 288-231.9c1.3-11.8 1.3-23.7 0-35.5C560.6 179.6 434.4 80 288 80zm0 368c-99.6 0-184-84.4-184-184s84.4-184 184-184 184 84.4 184 184-84.4 184-184 184zm0-64c-66.3 0-120-53.7-120-120s53.7-120 120-120 120 53.7 120 120-53.7 120-120 120z"/>
            `;
        }
    });
});

