// Bootstrap validation
(function () {
    'use strict'
    var forms = document.querySelectorAll('.needs-validation')
    Array.prototype.slice.call(forms).forEach(function (form) {
        form.addEventListener('input', function () {
            form.classList.add('was-validated');
        }, false)
    })
})()

// Attach event listener to DNS lookup button
document.addEventListener('DOMContentLoaded', function() {
    const dnsSearchButton = document.getElementById('dns-search-btn');
    dnsSearchButton.addEventListener('click', dns_search);
});


// Main function for DNS search
function dns_search() {
    const domainInput = document.getElementById('domain');
    const domain = domainInput.value.trim();
    const form = document.getElementById('dnsLookup');

    if (!form.checkValidity()) {
        form.classList.add('was-validated');
        return;
    }

    // Show loading spinner and hide other elements
    showLoading();
    hideResults();
    hideError();

    const csrfToken = document.querySelector('meta[name="csrf-token"]').getAttribute('content');

    fetch('/dns-lookup', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': csrfToken
        },
        body: JSON.stringify({ domain: domain })
    })
    .then(response => response.json())
    .then(data => {
        hideLoading();

        if (data.error) {
            displayError(data.error);
        } else {
            displayResults(data.dns_data, domain);
        }
    })
    .catch(error => {
        hideLoading();
        displayError('An error occurred: ' + error);
    });
}

// Function to display an error message
function displayError(message) {
    document.getElementById('error-info').innerText = message;
    document.getElementById('error-container').style.display = 'block';
    hideResults(); // Hide the DNS results if there is an error
}

// Function to display DNS results
function displayResults(dnsData, domain) {
    // Hide error container if visible
    hideError();

    // Update the summary and security recommendations
    document.getElementById('dns-summary').innerText = `DNS lookup for ${domain} completed successfully. Below are the detailed results and security analysis.`;

    // Populate DNS records with data
    document.getElementById('a-record').innerText = formatRecord(dnsData.A);
    document.getElementById('aaaa-record').innerText = formatRecord(dnsData.AAAA);
    document.getElementById('mx-record').innerText = formatRecord(dnsData.MX);
    document.getElementById('ns-record').innerText = formatRecord(dnsData.NS);
    document.getElementById('txt-record').innerText = formatRecord(dnsData.TXT);

    // Handle SSL certificate data
    document.getElementById('ssl-cert').innerText = formatSSLCertificate(dnsData['SSL Certificate']);

    // DNSSEC info
    document.getElementById('dnssec-info').innerText = formatRecord(dnsData.DNSSEC);

    // Generate security recommendations
    generateRecommendations(dnsData);

    // Show the DNS results container
    document.getElementById('dns-container').style.display = 'block';
}

// Utility functions for showing and hiding elements
function showLoading() {
    document.getElementById('loading-spinner').style.display = 'block';
}

function hideLoading() {
    document.getElementById('loading-spinner').style.display = 'none';
}

function hideError() {
    document.getElementById('error-container').style.display = 'none';
}

function hideResults() {
    document.getElementById('dns-container').style.display = 'none';
}

// Function to format record data
function formatRecord(recordData) {
    if (Array.isArray(recordData) && recordData.length > 0) {
        return recordData.join('\n');
    } else if (typeof recordData === 'string') {
        return recordData;
    } else {
        return 'No record found.';
    }
}

// Function to format SSL certificate data
function formatSSLCertificate(certData) {
    if (typeof certData === 'object' && certData !== null) {
        let formattedCert = `
Subject: ${certData.subject}
Issuer: ${certData.issuer}
Valid From: ${certData.valid_from}
Valid To: ${certData.valid_to}
Serial Number: ${certData.serial_number}
Version: ${certData.version}
`;
        return formattedCert.trim();
    } else if (typeof certData === 'string') {
        return certData;
    } else {
        return 'SSL certificate information unavailable.';
    }
}

// Function to generate security recommendations based on DNS data
function generateRecommendations(dnsData) {
    const recommendations = [];
    const recList = document.getElementById('security-recommendations');
    recList.innerHTML = ''; // Clear previous recommendations

    // SSL Certificate checks
    if (typeof dnsData['SSL Certificate'] === 'object' && dnsData['SSL Certificate'] !== null) {
        recommendations.push({
            level: 'success',
            message: '✅ SSL certificate detected. Your domain uses HTTPS, which helps secure user data and communication.'
        });
    } else {
        recommendations.push({
            level: 'danger',
            message: '❌ No SSL certificate detected or SSL issue found. Enable HTTPS to secure your website and protect user data.'
        });
    }

    // DNSSEC checks
    if (!dnsData.DNSSEC || dnsData.DNSSEC.length === 0) {
        recommendations.push({
            level: 'warning',
            message: '⚠️ DNSSEC is not enabled. Enabling DNSSEC helps prevent DNS spoofing and man-in-the-middle attacks.'
        });
    } else {
        recommendations.push({
            level: 'success',
            message: '✅ DNSSEC is enabled. This adds an additional layer of security to your domain.'
        });
    }

    // Zone Transfer check
    if (dnsData['Zone Transfer'] && dnsData['Zone Transfer'].some(z => z.includes('Zone transfer succeeded'))) {
        recommendations.push({
            level: 'danger',
            message: '❌ Zone transfer is allowed. This exposes your DNS zone data to attackers. Restrict zone transfers to authorized servers.'
        });
    } else {
        recommendations.push({
            level: 'success',
            message: '✅ Zone transfers are properly restricted.'
        });
    }

    // Display recommendations
    recommendations.forEach(rec => {
        const alertDiv = document.createElement('div');
        alertDiv.className = `alert alert-${rec.level}`;
        alertDiv.role = 'alert';
        alertDiv.innerText = rec.message;
        recList.appendChild(alertDiv);
    });
}
