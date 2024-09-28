// Function to generate hash of the uploaded file
function hash_file() {
    const fileInput = document.getElementById('file');
    const algorithm = document.getElementById('algorithm').value;

    // Check if file is uploaded
    if (fileInput.files.length === 0) {
        alert('Please upload a file.');
        return;
    }

    const file = fileInput.files[0];

    // Validate file extension based on the backend allowed extensions
    const allowedExtensions = ['txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif', 'exe', 'bin', 'dll', 'py', 'sh', 'bat', 'zip', 'tar', 'gz', '7z', 'docx', 'xlsx', 'pptx', 'log', 'conf', 'cfg', 'csv'];

    const fileExtension = file.name.split('.').pop().toLowerCase();

    if (!allowedExtensions.includes(fileExtension)) {
        alert('Unsupported file type. Please upload a valid file with one of the following extensions: ' + allowedExtensions.join(', '));
        return;
    }

    // Check file size (optional limit, e.g., 10MB)
    const maxSizeInMB = 10; // Set max size (10MB)
    if (file.size > maxSizeInMB * 1024 * 1024) {
        alert(`File size exceeds ${maxSizeInMB}MB. Please upload a smaller file.`);
        return;
    }

    // CSRF token extraction
    const csrfToken = document.querySelector('meta[name="csrf-token"]').getAttribute('content');

    // Prepare form data
    const formData = new FormData();
    formData.append('file', file);
    formData.append('algorithm', algorithm);

    // Show loading state if necessary
    document.getElementById('loading-spinner').style.display = 'block';

    // Fetch API call to server for file hashing
    fetch('/hash-file', {
        method: 'POST',
        headers: {
            'X-CSRFToken': csrfToken
        },
        body: formData
    })
    .then(response => response.json())
    .then(data => {
        // Hide loading spinner
        document.getElementById('loading-spinner').style.display = 'none';

        if (data.error) {
            alert('Error: ' + data.error);
        } else {
            // Display the results
            document.getElementById('file-name').innerText = data.metadata.filename;
            document.getElementById('file-size').innerText = formatBytes(data.metadata.size);
            document.getElementById('hash-algorithm').innerText = data.algorithm.toUpperCase();
            document.getElementById('hash-info').value = data.hash;
            document.getElementById('timestamp').innerText = new Date(data.metadata.timestamp).toLocaleString();

            // Show the hash container with results
            document.getElementById('hash-container').style.display = 'block';
        }
    })
    .catch(error => {
        // Hide loading spinner
        document.getElementById('loading-spinner').style.display = 'none';
        console.error('An error occurred:', error);
        alert('An error occurred. Please try again.');
    });
}

// Function to format bytes to human-readable form (e.g., KB, MB)
function formatBytes(bytes, decimals = 2) {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const dm = decimals < 0 ? 0 : decimals;
    const sizes = ['Bytes', 'KB', 'MB', 'GB', 'TB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(dm)) + ' ' + sizes[i];
}

// Function to copy hash to clipboard
function copyToClipboard(element) {
    const input = document.querySelector(element);
    input.select();
    input.setSelectionRange(0, 99999); // For mobile devices

    try {
        document.execCommand('copy');
        alert('Hash copied to clipboard!');
    } catch (err) {
        console.error('Failed to copy:', err);
        alert('Failed to copy hash.');
    }
}

// Event listeners setup after DOM loads
document.addEventListener('DOMContentLoaded', () => {
    document.getElementById('generate-hash-btn').addEventListener('click', hash_file);
    document.getElementById('copy-hash-btn').addEventListener('click', () => copyToClipboard('#hash-info'));
});
