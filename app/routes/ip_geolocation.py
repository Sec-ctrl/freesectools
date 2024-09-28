from flask import Blueprint, render_template, request, jsonify
from modules.ip2geo import IPGeolocationLookup
from flask_wtf.csrf import validate_csrf

ip_geolocation_bp = Blueprint('ip_geolocation', __name__)

def init_ip_geolocation_routes(limiter):
    # Define a route to handle the IP geolocation lookup
    @ip_geolocation_bp.route('/lookup-ip-geolocation', methods=['POST'])
    @limiter.limit("5 per minute")  # Limit to 5 requests per minute
    def lookup_ip_geolocation():
        csrf_token = request.headers.get('X-CSRFToken')
        try:
            validate_csrf(csrf_token)
        except:
            return jsonify({'error': 'Invalid CSRF token'}), 400
        data = request.get_json()
        ip_address = data.get('ip_address', '').strip()

        if not ip_address:
            return jsonify({'error': 'IP address is required'}), 400

        # Initialize the IPGeolocationLookup
        geo_lookup = IPGeolocationLookup()
        result = geo_lookup.lookup(ip_address)
        print(result)

        return jsonify(result)

    # Define a route for the IP Geolocation page
    @ip_geolocation_bp.route('/ip-geolocation')
    def ip_geolocation():
        return render_template('/tools/ip_geolocation.html', title='IP Geolocation Tool')
