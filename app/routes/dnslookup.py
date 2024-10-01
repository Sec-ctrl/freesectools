from flask import Blueprint, render_template, request, jsonify, abort
from modules.dns_lookup import DNSLookup  # You'll need to create this module
from flask_wtf.csrf import validate_csrf
import sqlite3
import re


dnslookup_bp = Blueprint("dnslookup", __name__)


@dnslookup_bp.route("/dns-lookup")
def dns_lookup():
    try:
        # Connect to the SQLite database
        conn = sqlite3.connect("blogs_advanced.db")
        cursor = conn.cursor()

        # Fetch the specific blog post by ID using a parameterized query
        cursor.execute(
            """
            SELECT posts.id, posts.title, posts.content, posts.image, posts.date, authors.name, categories.name
            FROM posts
            JOIN authors ON posts.author_id = authors.id
            JOIN categories ON posts.category_id = categories.id
            WHERE posts.id = ?
        """,
            (2,),
        )  # Use a valid post ID that exists in your database

        row = cursor.fetchone()

        # If the blog post does not exist, return a 404 error
        if row is None:
            abort(404)

        # Convert row to a dictionary
        blog_post = {
            "id": row[0],
            "title": row[1],
            "content": row[2],
            "image": row[3],
            "date": row[4],
            "author": row[5],
            "category": row[6],
        }

    except sqlite3.Error as e:
        print(f"Database error: {e}")
        abort(500)
    finally:
        # Close the database connection
        conn.close()

    # Render the template and pass the blog_post
    return render_template(
        "/tools/dnslookup.html", title="DNS Lookup Tool", blog_post=blog_post
    )


@dnslookup_bp.route("/dns-lookup", methods=["POST"])
def dns_lookup_search():
    data = request.get_json()
    csrf_token = request.headers.get("X-CSRFToken")

    # Validate CSRF token
    try:
        validate_csrf(csrf_token)
    except Exception as e:
        return jsonify({"error": "Invalid CSRF token" f"and {e}"}), 400

    # Extract and validate the domain
    domain = data.get("domain", "").strip()
    if not domain:
        return jsonify({"error": "Domain is required"}), 400

    # Basic domain format validation
    if not re.match(r"^[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$", domain):
        return jsonify({"error": "Invalid domain format"}), 400

    # Perform DNS lookup using the DNSLookup class
    dns_lookup = DNSLookup(domain)
    dns_data = dns_lookup.perform_lookup()

    if isinstance(dns_data, str) and "Error" in dns_data:
        return jsonify({"error": dns_data}), 500

    # Return the DNS data and SSL certificate as JSON
    return jsonify({"dns_data": dns_data})
