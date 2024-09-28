from flask import Blueprint, render_template, request, jsonify
import hashlib
from flask_wtf.csrf import validate_csrf
from werkzeug.utils import secure_filename
import os
import time
from datetime import datetime

# Blueprint setup
hash_bp = Blueprint('hash', __name__)

# Set allowed file extensions and max file size (10 MB)
ALLOWED_EXTENSIONS = {'txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif', 'exe', 'bin', 'dll', 'py', 'sh', 'bat', 'zip', 'tar', 'gz', '7z', 'docx', 'xlsx', 'pptx', 'log', 'conf', 'cfg', 'csv'}
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10 MB

# In-memory rate limiting: store timestamps of requests by IP address
rate_limit_storage = {}

# Helper function to check allowed file extensions
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# Simple rate limiting function: allows 5 requests per minute
def is_rate_limited(ip_address):
    current_time = time.time()
    request_timestamps = rate_limit_storage.get(ip_address, [])
    
    # Filter timestamps older than 60 seconds
    request_timestamps = [ts for ts in request_timestamps if current_time - ts < 60]
    
    if len(request_timestamps) >= 5:
        return True
    
    # Update the storage with the current timestamp
    request_timestamps.append(current_time)
    rate_limit_storage[ip_address] = request_timestamps
    return False

# Hashing route
@hash_bp.route('/hash')
def hash():
    return render_template('/tools/hash.html', title="File Hashing Tool")

@hash_bp.route('/hash-file', methods=['POST'])
def hash_file():
    try:
        csrf_token = request.headers.get('X-CSRFToken')
        client_ip = request.remote_addr

        # Rate limiting
        if is_rate_limited(client_ip):
            return jsonify({'error': 'Rate limit exceeded. Please wait before making more requests.'}), 429

        # Validate CSRF token
        validate_csrf(csrf_token)

        # Check if a file was uploaded
        if 'file' not in request.files:
            return jsonify({'error': 'No file uploaded'}), 400

        file = request.files['file']
        filename = secure_filename(file.filename)

        # Validate file extension
        if not allowed_file(filename):
            return jsonify({'error': 'Invalid file type. Allowed types: ' + ', '.join(ALLOWED_EXTENSIONS)}), 400

        # Validate file size
        file.seek(0, os.SEEK_END)  # Move to the end of the file
        file_size = file.tell()  # Get file size
        file.seek(0)  # Reset file pointer to beginning
        if file_size > MAX_FILE_SIZE:
            return jsonify({'error': f'File size exceeds limit of {MAX_FILE_SIZE // 1024 // 1024} MB'}), 400

        # Get the selected algorithm from the form
        algorithm = request.form.get('algorithm', 'md5')

        # Ensure the selected algorithm is valid and add more options
        supported_algorithms = {'md5': hashlib.md5, 'sha1': hashlib.sha1, 'sha256': hashlib.sha256, 'sha512': hashlib.sha512, 'sha3_256': hashlib.sha3_256}
        if algorithm not in supported_algorithms:
            return jsonify({'error': 'Invalid hashing algorithm. Supported: MD5, SHA-1, SHA-256, SHA-512, SHA3-256'}), 400

        # Read file content
        file_content = file.read()

        # Hash the file using the selected algorithm
        hash_func = supported_algorithms[algorithm]()
        hash_func.update(file_content)
        hash_value = hash_func.hexdigest()

        # Get basic file metadata
        metadata = {
            'filename': filename,
            'size': file_size,
            'timestamp': datetime.utcnow().isoformat(),
        }

        # Return the generated hash and file metadata as JSON
        return jsonify({
            'hash': hash_value,
            'algorithm': algorithm,
            'metadata': metadata
        })

    except Exception as e:
        # Catch any unhandled errors and ensure a JSON response is returned
        return jsonify({'error': 'An unexpected error occurred: ' + str(e)}), 500
