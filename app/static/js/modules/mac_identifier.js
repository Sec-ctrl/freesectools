function lookupMacAddress() {
    const macAddress = document.getElementById('mac_address').value;
    const csrfToken = document.querySelector('meta[name="csrf-token"]').getAttribute('content');

    fetch('/lookup-mac-address', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': csrfToken
        },
        body: JSON.stringify({ mac_address: macAddress })
    })
    .then(response => response.json())  // Parse response as JSON
    .then(data => {
        const macLookupResult = document.getElementById('mac-lookup-result');
        const manufacturerInfo = document.getElementById('manufacturer-info');
        const unicastMulticastInfo = document.getElementById('unicast-multicast-info');
        const localUniversalInfo = document.getElementById('local-universal-info');

        // Check for any error in the response
        if (data.error) {
            alert('Error: ' + data.error);
            macLookupResult.style.display = 'none';  // Hide the result section if there's an error
        } else {
            const result = data.result;

            // Display the results in the result section
            manufacturerInfo.innerHTML = `<strong>Manufacturer:</strong> ${result.manufacturer || 'Not Available'}`;
            unicastMulticastInfo.innerHTML = `<strong>Address Type:</strong> ${result.unicast_multicast || 'Not Available'}`;
            localUniversalInfo.innerHTML = `<strong>Administration Type:</strong> ${result.local_universal || 'Not Available'}`;

            macLookupResult.style.display = 'block';  // Show the result section
        }
    })
    .catch(error => {
        alert('An error occurred: ' + error);
        document.getElementById('mac-lookup-result').style.display = 'none';  // Hide the result section if an error occurs
    });
}

document.addEventListener('DOMContentLoaded', function() {
    const lookupButton = document.getElementById('lookup-button');
    if (lookupButton) {
        lookupButton.addEventListener('click', function() {
            lookupMacAddress();
        });
    }
});
