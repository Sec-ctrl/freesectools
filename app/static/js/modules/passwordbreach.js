function checkPasswordBreach() {
    const password = document.getElementById('password').value;
    const csrfToken = document.querySelector('meta[name="csrf-token"]').getAttribute('content');

    fetch('/check-password-breach', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': csrfToken // Include CSRF token
        },
        body: JSON.stringify({ password: password })
    })
    .then(response => response.json())
    .then(data => {
        const breachContainer = document.getElementById('breach-container');
        const breachInfo = document.getElementById('breach-info');
        const breachIcon = document.getElementById('breach-icon');
        const breachRecommendation = document.getElementById('breach-recommendation');

        if (data.error) {
            alert('Error: ' + data.error);
        } else {
            const breachCount = data.breach_count;
            breachContainer.style.display = 'block';

            if (breachCount > 0) {
                breachIcon.className = 'bi bi-exclamation-triangle-fill text-danger'; // Custom red icon
                breachInfo.innerText = `Your password was found in ${breachCount} data breach${breachCount > 1 ? 'es' : ''}.`;
                breachRecommendation.innerText = 'We recommend you change your password immediately for better security.';
            } else {
                breachIcon.className = 'bi bi-check-circle-fill text-success'; // Custom green icon
                breachInfo.innerText = 'Good news! Your password was not found in any breaches.';
                breachRecommendation.innerText = 'It\'s always good practice to use unique passwords for different sites.';
            }
        }
    })
    .catch(error => {
        alert('An error occurred: ' + error);
    });
}

document.addEventListener('DOMContentLoaded', function() {
    // Add event listener for the breach check button
    const breachButton = document.getElementById('check-breach-btn');
    if (breachButton) {
        breachButton.addEventListener('click', function() {
            checkPasswordBreach();
        });
    }
});