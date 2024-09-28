from flask import Blueprint, render_template, request, jsonify
from modules.ip_blacklist_checker import IPBlacklistChecker

ip_blacklist_bp = Blueprint('ip_blacklist', __name__)

def init_ip_blacklist_routes(limiter):
    # Define a route to handle the IP blacklist lookup
    @limiter.limit("5 per minute")  # Limit to 5 requests per minute
    @ip_blacklist_bp.route('/lookup-ip-blacklist', methods=['POST'])
    def lookup_ip_blacklist():
        try:
            data = request.get_json()

            # Validate that data is received and is in JSON format
            if not data or not isinstance(data, dict):
                return jsonify({'error': 'Invalid JSON format'}), 400

            # Extract and validate the IP address
            ip_address = data.get('ip_address', '').strip()

            if not ip_address:
                return jsonify({'error': 'IP address is required'}), 400

            # Initialize the IPBlacklistChecker
            blacklist_checker = IPBlacklistChecker()
            result = blacklist_checker.is_blacklisted(ip_address)

            return jsonify(result)

        except Exception as e:
            # Catch any unexpected errors and return a JSON error response
            return jsonify({'error': 'An error occurred: ' + str(e)}), 500

    # Define a route for the IP Blacklist Checker page
    @ip_blacklist_bp.route('/ip-blacklist')
    def ip_blacklist():
        return render_template('/tools/ip_blacklist.html', title='IP Blacklist Tool')
