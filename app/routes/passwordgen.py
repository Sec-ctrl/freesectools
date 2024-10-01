from flask import Blueprint, render_template, request, jsonify
from flask_wtf.csrf import validate_csrf
from modules.password_generator import PasswordGenerator
import re


passwordgen_bp = Blueprint("passwordgen", __name__)


@passwordgen_bp.route("/passwordgen")
def password_tool():
    return render_template("/tools/passwordgen.html", title="Password Generator")


@passwordgen_bp.route("/generate-password", methods=["POST"])
def generate_password():
    # Get the form data from the AJAX request
    data = request.get_json()

    csrf_token = request.headers.get("X-CSRFToken")
    try:
        validate_csrf(csrf_token)
    except Exception as e:
        return jsonify({"error": "Invalid CSRF token" f":{e}"}), 400

    # Extract and validate form data
    try:
        length = int(data.get("length", 12))
        if not 4 <= length <= 64:
            return jsonify({"error": "Invalid password length"}), 400

        # Sanitize and validate custom characters
        custom_chars = data.get("custom_chars", "")
        if len(custom_chars) > 50 or not re.match(r"^[\w\W]*$", custom_chars):
            return jsonify({"error": "Invalid custom characters"}), 400

        # Extract and validate boolean options
        include_uppercase = bool(data.get("include_uppercase", False))
        include_lowercase = bool(data.get("include_lowercase", False))
        include_digits = bool(data.get("include_digits", False))
        include_symbols = bool(data.get("include_symbols", False))
        exclude_similar = bool(data.get("exclude_similar", False))
        exclude_ambiguous = bool(data.get("exclude_ambiguous", False))
        exclude_quotes = bool(data.get("exclude_quotes", False))

    except ValueError as e:
        return jsonify({"error": "Invalid input data" f"{e}"}), 400

    # Initialize the password generator
    password_generator = PasswordGenerator(
        length=length,
        include_uppercase=include_uppercase,
        include_lowercase=include_lowercase,
        include_digits=include_digits,
        include_symbols=include_symbols,
        exclude_similar=exclude_similar,
        exclude_ambiguous=exclude_ambiguous,
        exclude_quotes=exclude_quotes,
        custom_chars=custom_chars,
    )

    # Generate the password
    try:
        generated_password = password_generator.generate()
    except Exception as e:
        return jsonify({"error": "Error generating password" f":{e}"}), 500

    # Return the password as JSON
    return jsonify({"password": generated_password})
