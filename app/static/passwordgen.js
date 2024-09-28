// Show a notification alert with a message
function showNotification(message, type = 'info') {
    const notificationAlert = document.getElementById('notification-alert');
    const notificationMessage = document.getElementById('notification-message');

    notificationMessage.innerText = message;
    notificationAlert.className = `alert alert-${type} alert-dismissible fade show`;

    // Auto-hide the notification after 3 seconds
    setTimeout(() => {
        closeNotification();
    }, 3000);
}

// Close the notification
function closeNotification() {
    const notificationAlert = document.getElementById('notification-alert');
    notificationAlert.classList.remove('show');
}

// Update the password length display dynamically
function updateLengthValue(value) {
    document.getElementById('length-value').innerText = value;
}

// Validate form inputs and generate the password if valid
function validateAndGeneratePassword() {
    // Retrieve form values
    const length = parseInt(document.getElementById('password-length').value, 10);
    const includeUppercase = document.getElementById('include-uppercase').checked;
    const includeLowercase = document.getElementById('include-lowercase').checked;
    const includeDigits = document.getElementById('include-digits').checked;
    const includeSymbols = document.getElementById('include-symbols').checked;
    const customChars = document.getElementById('custom-chars').value;

    // Validate password length
    if (isNaN(length) || length < 4 || length > 64) {
        showNotification('Password length must be between 4 and 64.');
        return;
    }

    // Validate that at least one character type is selected or custom characters are provided
    if (!includeUppercase && !includeLowercase && !includeDigits && !includeSymbols && customChars.trim() === "") {
        showNotification('Select at least one character type or provide custom characters.');
        return;
    }

    // Validate custom characters length
    if (customChars.length > 50) {
        showNotification('Custom characters input is too long (maximum 50 characters).');
        return;
    }

    // If validation passes, generate the password
    generatePassword();
}

// Send AJAX request to generate the password dynamically
function generatePassword() {

    // Get the CSRF token from the meta tag in HTML
    const csrfToken = document.querySelector('meta[name="csrf-token"]').getAttribute('content');

    // Collect form data
    const formData = {
        length: document.getElementById('password-length').value,
        include_uppercase: document.getElementById('include-uppercase').checked,
        include_lowercase: document.getElementById('include-lowercase').checked,
        include_digits: document.getElementById('include-digits').checked,
        include_symbols: document.getElementById('include-symbols').checked,
        exclude_similar: document.getElementById('exclude-similar').checked,
        exclude_ambiguous: document.getElementById('exclude-ambiguous').checked,
        exclude_quotes: document.getElementById('exclude-quotes').checked,
        custom_chars: document.getElementById('custom-chars').value
    };

    // Send AJAX request to the Flask backend
    fetch('/generate-password', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': csrfToken // Include CSRF token in request header
        },
        body: JSON.stringify(formData)
    })
    .then(response => {
        if (!response.ok) {
            throw new Error('Failed to generate password. Please check your input.');
        }
        return response.json();
    })
    .then(data => {
        if (data.error) {
            showNotification(data.error);
        } else {
            // Show the password and copy button
            document.getElementById('generated-password').innerText = data.password;
            document.getElementById('password-container').style.display = 'block';
            
            // Update the password strength indicator
            updatePasswordStrength(data.password);
        }
    })
    .catch(error => {
        console.error('Error:', error);
        showNotification('An error occurred while generating the password. Please try again.');
    });
}

// Update the password strength indicator based on the password's complexity
function updatePasswordStrength(password) {
    const strengthBar = document.getElementById('strength-bar');
    const strengthText = document.getElementById('strength-text');
    const strengthContainer = document.querySelector('.password-strength-container');
    let strength = 0;

    // Calculate password strength
    if (password.length >= 12) strength += 1;
    if (/[A-Z]/.test(password)) strength += 1;
    if (/[a-z]/.test(password)) strength += 1;
    if (/\d/.test(password)) strength += 1;
    if (/[^A-Za-z0-9]/.test(password)) strength += 1;

    // Update the strength bar and text
    const strengthPercent = (strength / 5) * 100;
    strengthBar.style.width = strengthPercent + '%';

    // Determine the strength level and color
    let strengthLevel;
    let barClass;
    if (strength <= 1) {
        strengthLevel = 'Very Weak';
        barClass = 'bg-danger';
    } else if (strength === 2) {
        strengthLevel = 'Weak';
        barClass = 'bg-warning';
    } else if (strength === 3) {
        strengthLevel = 'Moderate';
        barClass = 'bg-info';
    } else if (strength === 4) {
        strengthLevel = 'Strong';
        barClass = 'bg-primary';
    } else {
        strengthLevel = 'Very Strong';
        barClass = 'bg-success';
    }

    // Update bar class
    strengthBar.className = 'progress-bar ' + barClass;

    // Show the strength container
    strengthContainer.style.display = 'block';
    strengthText.innerText = strengthLevel;
}

// Copy the generated password to the clipboard
function copyPassword() {
    const password = document.getElementById('generated-password').innerText;
    navigator.clipboard.writeText(password).then(() => {
        showNotification('Password copied!', 'success');
    }).catch(err => {
        console.error('Could not copy text: ', err);
        showNotification('Failed to copy password.', 'danger');
    });
}

document.addEventListener('DOMContentLoaded', function() {
    // Event listener for range input
    const passwordLengthInput = document.getElementById('password-length');
    if (passwordLengthInput) {
        passwordLengthInput.addEventListener('input', function() {
            updateLengthValue(this.value);
        });
    }

    // Event listener for generate button
    const generateButton = document.getElementById('generate-button');
    if (generateButton) {
        generateButton.addEventListener('click', function() {
            validateAndGeneratePassword();
        });
    }

    // Event listener for copy password
    const copyButton = document.getElementById('copy-button');
    if (copyButton) {
        copyButton.addEventListener('click', function() {
            copyPassword();
        });
    }
});

document.addEventListener('DOMContentLoaded', function() {
    // Event listener for copy password
    const copyButton = document.getElementById('copy-button');
    if (copyButton) {
        copyButton.addEventListener('click', function() {
            copyPassword();
        });
    }
});