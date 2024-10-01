from flask import Blueprint, render_template, request, jsonify
from modules.password_used import DataBreachChecker


databreach_bp = Blueprint("databreach", __name__)


@databreach_bp.route("/password-breach")
def password_breach():
    return render_template("/tools/password_breach.html", title="Password Breach Tool")


def init_databreach_routes(limiter):
    @limiter.limit("10 per minute")
    @databreach_bp.route("/check-password-breach", methods=["POST"])
    def check_password_breach():
        data = request.get_json()
        password = data.get("password", "").strip()

        if not password:
            return jsonify({"error": "Password is required"}), 400

        # Initialize the DataBreachChecker
        checker = DataBreachChecker()
        try:
            breach_count = checker.check_password_breach(password)
            return jsonify({"breach_count": breach_count})
        except Exception as e:
            return jsonify({"error": str(e)}), 500
