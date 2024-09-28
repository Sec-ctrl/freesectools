from flask import Flask, request, jsonify, Blueprint, render_template
import json
import hashlib

header_checker_bp = Blueprint('header_checker', __name__)

@header_checker_bp.route('/fingerprint', methods=['GET'])
def fingerprint():
    return render_template('/tools/header_checker.html')

@header_checker_bp.route('/analyze_fingerprint', methods=['POST'])
def analyze_fingerprint():
    try:
        # Log the request data to help debug
        print("Raw request data:", request.data)
        
        # Attempt to parse JSON data from the request
        data = request.get_json(force=True)  # Force parsing as JSON
        
        # Log the parsed JSON data
        print("Parsed JSON data:", data)

        if not data:
            return jsonify({'error': 'Invalid JSON data'}), 400
        
        # Create a unique hash of the fingerprint data
        fingerprint_hash = hashlib.sha256(json.dumps(data, sort_keys=True).encode()).hexdigest()
        
        # Get detailed analysis and risk level
        analysis_result = calculate_risk_level(data)
        
        # Create the result to include risk level, detailed analysis, and fingerprint hash
        result = {
            'fingerprint_hash': fingerprint_hash,
            'risk_level': analysis_result['risk_level'],
            'risk_score': analysis_result['risk_score'],
            'detailed_analysis': analysis_result['detailed_analysis']
        }
        return jsonify(result)
    except Exception as e:
        # Log the exception and return the error message to help with debugging
        print("Error during JSON parsing:", str(e))
        return jsonify({'error': str(e)}), 400

def calculate_risk_level(fingerprint_data):
    # Define the baseline common values for each attribute
    common_values = {
        'userAgent': ['Mozilla/5.0', 'Windows NT', 'Macintosh', 'Linux'],
        'platform': ['Win32', 'MacIntel', 'Linux x86_64'],
        'screenResolution': ['1920x1080', '1366x768'],
        'colorDepth': [24, 32],
        'timezone': ['UTC', 'GMT'],
        'language': ['en-US', 'en-GB'],
        'hardwareConcurrency': [4, 8],
        'deviceMemory': [4, 8],
        'plugins': [],
        'mimeTypes': [],
        'canvasFingerprint': [],
        'webglFingerprint': [],
        'audioFingerprint': [],
        'fonts': [],
        'touchSupport': [True, False],
        'pointerSupport': [True, False],
        'connectionType': [],
        'maxTouchPoints': [0, 1, 5],
        'javaEnabled': [False],
        'cookieEnabled': [True, False],
    }
    
    detailed_analysis = []
    risk_score = 0
    
    # Analyze each attribute
    for key, value in fingerprint_data.items():
        # Create a base detail dictionary
        attribute_detail = {
            'attribute': key,
            'value': value,
            'unique': False,
            'description': '',
            'recommendation': ''
        }

        # Handle 'N/A' values gracefully
        if value == 'N/A':
            attribute_detail['description'] = (
                "The value is not available. This may or may not affect your fingerprint's uniqueness."
            )
            attribute_detail['unique'] = False

        # Determine if the attribute is a known common value
        elif key in common_values:
            if isinstance(value, list):
                # Check if the list of values contains common values
                uniqueness = all(item not in common_values[key] for item in value)
                # Join list elements into a single string for explanation if needed
                display_value = ', '.join(map(str, value))  # Convert all elements to strings
            else:
                # Handle other types like int, float, str
                uniqueness = value not in common_values[key]
                display_value = str(value)  # Convert to string for consistent handling

            # If the attribute value is unique
            if uniqueness:
                attribute_detail['unique'] = True
                # Truncate the explanation for very long values
                if isinstance(display_value, str) and len(display_value) > 30:
                    truncated_value = display_value[:30] + '...'
                else:
                    truncated_value = display_value
                attribute_detail['description'] = (
                    "The value is uncommon and may make your browser more identifiable."
                )
                risk_score += 1  # Increment risk score for unique attributes
                # Add a recommendation
                attribute_detail['recommendation'] = get_recommendation_for_attribute(key)
            else:
                attribute_detail['description'] = (
                    "The value is common and doesn't significantly affect your fingerprint."
                )
        
        # If the attribute's uniqueness cannot be determined specifically
        else:
            attribute_detail['description'] = (
                "The uniqueness of this attribute could not be determined specifically."
            )

        # Append the detailed analysis
        detailed_analysis.append(attribute_detail)

    # Determine the overall risk level
    if risk_score > 10:
        risk_level = 'High'
    elif risk_score > 5:
        risk_level = 'Medium'
    else:
        risk_level = 'Low'

    return {
        'risk_level': risk_level,
        'risk_score': risk_score,
        'detailed_analysis': detailed_analysis
    }

def get_recommendation_for_attribute(attribute):
    recommendations = {
        'userAgent': "Use privacy-focused browser extensions (e.g., User-Agent Switcher) to modify the user agent string or use a browser that randomizes the user agent, such as Tor Browser.",
        'platform': "Use virtual machines (VMs) or privacy-focused browsers that can spoof or hide platform information.",
        'screenResolution': "Use a standard screen resolution or a privacy tool that spoofs screen resolution. Resizing your browser window to common dimensions can also help.",
        'colorDepth': "Use browser extensions that can modify or obscure the color depth information.",
        'timezone': "Use a VPN or privacy tools that spoof your timezone to a more common one (e.g., UTC).",
        'language': "Set your browser language to a more common language (e.g., 'en-US'). Use privacy tools that randomize or hide language settings.",
        'hardwareConcurrency': "Use a privacy-focused browser or extensions that spoof the number of logical processors.",
        'deviceMemory': "Use privacy-focused browsers that obfuscate or limit the exposure of device memory information.",
        'plugins': "Disable unnecessary plugins or use a privacy-focused browser that restricts plugin exposure. Consider using browser extensions that spoof plugin information.",
        'mimeTypes': "Use privacy-focused browsers or extensions that limit or spoof MIME types.",
        'canvasFingerprint': "Use privacy-focused browsers like Brave or Tor that block or obfuscate canvas fingerprinting. Install browser extensions like CanvasBlocker.",
        'webglFingerprint': "Use browsers or extensions that block or spoof WebGL information (e.g., Canvas Defender).",
        'audioFingerprint': "Use privacy tools or browser settings to block or obfuscate the AudioContext API. Consider using browsers like Tor that provide built-in protection.",
        'fonts': "Use browser extensions that limit the fonts accessible to websites. Avoid installing custom fonts that make your system more unique.",
        'touchSupport': "Use browser extensions that can spoof touch support information if you're concerned about its uniqueness.",
        'pointerSupport': "Use privacy-focused browsers that can obfuscate or limit pointer support information.",
        'connectionType': "Use privacy tools that spoof or block network connection type information.",
        'maxTouchPoints': "Use privacy-focused browsers or extensions to spoof the number of touch points if it's unique.",
        'javaEnabled': "Disable Java in your browser if it's not required for your use case to enhance privacy.",
        'cookieEnabled': "Use browser extensions that manage cookies and enhance privacy, such as automatic cookie deletion."
    }
    return recommendations.get(attribute, "")