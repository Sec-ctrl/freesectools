from flask import Blueprint, render_template, request, jsonify
from modules.mac_checker import MACAddressLookup
from flask_wtf.csrf import validate_csrf

mac_lookup_bp = Blueprint('mac_lookup', __name__)

# Define a route for the MAC address lookup page
@mac_lookup_bp.route('/mac-identifier')
def mac_identifier():
    return render_template('/tools/mac_identifier.html', title="Mac Identifier Tool")

# Define a route to handle the lookup
@mac_lookup_bp.route('/lookup-mac-address', methods=['POST'])
def lookup_mac_address():
    
    csrf_token = request.headers.get('X-CSRFToken')
    try:
        validate_csrf(csrf_token)
    except:
        return jsonify({'error': 'Invalid CSRF token'}), 400
    
    data = request.get_json()
    mac_address = data.get('mac_address', '').strip()

    if not mac_address:
        return jsonify({'error': 'MAC address is required'}), 400

    # Initialize the MACAddressLookup
    mac_lookup = MACAddressLookup()
    result = mac_lookup.lookup(mac_address)

    return jsonify({'result': result})
