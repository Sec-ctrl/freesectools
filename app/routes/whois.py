# routes/whois.py

from flask import Blueprint, render_template, request, jsonify, abort
from modules.whois_lookup import WhoisLookup
from flask_wtf.csrf import validate_csrf
import re
import sqlite3


whois_bp = Blueprint("whois", __name__)


@whois_bp.route("/whois")
def whois():
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
        (3,),
    )
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

    # Close the database
    conn.close()
    return render_template(
        "/tools/whois.html", title="Whois Lookup Tool", blog_post=blog_post
    )


@whois_bp.route("/whois-search", methods=["POST"])
def whois_search():
    data = request.get_json()
    csrf_token = request.headers.get("X-CSRFToken")
    try:
        validate_csrf(csrf_token)
    except Exception as e:
        return jsonify({"error": "Invalid CSRF token" f"{e}"}), 400

    domain = data.get("domain", "").strip()
    if not domain:
        return jsonify({"error": "Domain is required"}), 400

    if not re.match(r"^[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$", domain):
        return jsonify({"error": "Invalid domain format"}), 400

    try:
        whois_lookup = WhoisLookup(domain)
        whois_data = whois_lookup.perform_lookup()
    except Exception as e:
        return jsonify({"error": str(e)}), 500

    if isinstance(whois_data, str) and "Error" in whois_data:
        return jsonify({"error": whois_data}), 500

    return jsonify({"whois_data": whois_data})
