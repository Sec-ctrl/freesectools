function lookupIPBlacklist() {
    const ipAddress = document.getElementById('ip_address').value.trim(); // Trim spaces to avoid empty strings
    const csrfToken = document.querySelector('meta[name="csrf-token"]').getAttribute('content');

    // Validate IP address format before making the request
    if (!ipAddress) {
        alert('Please enter a valid IP address.');
        return;
    }

    // Perform the API request to check the IP blacklist status
    fetch('/lookup-ip-blacklist', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': csrfToken // Include CSRF token in request header
        },
        body: JSON.stringify({ ip_address: ipAddress })
    })
    .then(response => {
        return response.json().then(data => {
            if (response.status === 400) {
                alert('Error: ' + data.error); // Handle 400 errors
            } else if (response.status === 500) {
                alert('Server Error: ' + data.error); // Handle 500 errors
            } else if (data.error) {
                alert('Error: ' + data.error);
            } else {
                const blacklistInfo = document.getElementById('blacklist-info');
                blacklistInfo.innerHTML = '';

                for (const [provider, status] of Object.entries(data)) {
                    const li = document.createElement('li');
                    li.innerText = `${provider}: ${status}`;
                    blacklistInfo.appendChild(li);
                }

                document.getElementById('blacklist-result').style.display = 'block';
            }
        });
    })
    .catch(error => {
        alert('An error occurred: ' + error);
        console.error('Fetch error:', error);
    });
}

document.addEventListener('DOMContentLoaded', function() {
    const checkButton = document.getElementById('check_button');
    if (checkButton) {
        checkButton.addEventListener('click', lookupIPBlacklist);
    }
});
