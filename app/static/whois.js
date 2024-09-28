document.addEventListener('DOMContentLoaded', function() {
    const whoisButton = document.getElementById('whois-lookup-btn');
    if (whoisButton) {
        whoisButton.addEventListener('click', whois_search);
    }
});

function whois_search() {
    const whoisContainer = document.getElementById('whois-container');
    const domain = document.getElementById('domain').value;
    const csrfToken = document.querySelector('meta[name="csrf-token"]').getAttribute('content');

    fetch('/whois-search', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': csrfToken
        },
        body: JSON.stringify({ domain: domain })
    })
    .then(response => response.json())
    .then(data => {
        if (data.error) {
            alert('Error: ' + data.error);
        } else {
            // Display the WHOIS data
            document.getElementById('whois-info').innerText = JSON.stringify(data.whois_data, null, 2);
            document.getElementById('whois-container').style.display = 'block';
        }
    // Display the result after successful lookup
    whoisContainer.classList.remove('hidden');
    })
    
    .catch(error => {
        alert('An error occurred: ' + error);
    });
}

