// Add an event listener for DOMContentLoaded to ensure the DOM is fully loaded before attaching listeners
document.addEventListener('DOMContentLoaded', function() {
    // Add event listener for the "Lookup IP Geolocation" button
    const lookupButton = document.getElementById('lookup-ip-button');
    if (lookupButton) {
        lookupButton.addEventListener('click', function(event) {
            event.preventDefault(); // Prevent the default form submission behavior
            lookupIPGeolocation();  // Call the lookup function
        });
    }
});

function lookupIPGeolocation() {
    const ipAddress = document.getElementById('ip_address').value.trim();
    const csrfToken = document.querySelector('meta[name="csrf-token"]').getAttribute('content');
    
    // Clear previous error messages and results
    document.getElementById('ip-error').style.display = 'none';
    document.getElementById('error-message').style.display = 'none';
    document.getElementById('geolocation-result').style.display = 'none';
    document.getElementById('loading').style.display = 'none';
    
    // Basic IP address validation
    if (!validateIPAddress(ipAddress)) {
        showError('Invalid IP address format.');
        return;
    }

    // Show loading indicator
    document.getElementById('feedback').style.display = 'block';
    document.getElementById('loading').style.display = 'inline-block';

    fetch('/lookup-ip-geolocation', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': csrfToken // Include CSRF token in request header
        },
        body: JSON.stringify({ ip_address: ipAddress })
    })
    .then(response => {
        // Hide loading indicator
        document.getElementById('loading').style.display = 'none';

        if (!response.ok) {
            throw new Error(`Error ${response.status}: ${response.statusText}`);
        }
        return response.json();
    })
    .then(data => {
        if (data.error) {
            showError(data.error);
        } else {
            showGeolocationResult(data);
        }
    })
    .catch(error => {
        showError('An error occurred: ' + error.message);
    });
}

function validateIPAddress(ip) {
    const ipPattern = /^(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)$/;
    return ipPattern.test(ip);
}

function showError(message) {
    const errorMessage = document.getElementById('error-message');
    errorMessage.textContent = message;
    errorMessage.style.display = 'block';
}

function showGeolocationResult(data) {
    // Display the geolocation information
    const geolocationInfo = document.getElementById('geolocation-info');
    geolocationInfo.innerHTML = '';

    for (const [key, value] of Object.entries(data)) {
        const li = document.createElement('li');
        li.innerText = `${key}: ${value}`;
        geolocationInfo.appendChild(li);
    }

    document.getElementById('geolocation-result').style.display = 'block';

    // Show the map if latitude and longitude are present
    if (data.Latitude && data.Longitude) {
        showMap(data.Latitude, data.Longitude);
    }
}

function showMap(lat, lon) {
    const mapContainer = document.getElementById('map');
    mapContainer.innerHTML = ''; // Clear the map container

    const map = L.map(mapContainer).setView([lat, lon], 13);
    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
        maxZoom: 19,
    }).addTo(map);

    L.marker([lat, lon]).addTo(map)
        .bindPopup('Location found')
        .openPopup();
}
