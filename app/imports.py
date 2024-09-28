from flask import Flask, send_from_directory, jsonify, request
from routes.home import home_bp
from routes.about import about_bp
from routes.passwordgen import passwordgen_bp
from routes.whois import whois_bp
from routes.databreach import databreach_bp
from routes.mac_lookup import mac_lookup_bp
from routes.ip_geolocation import ip_geolocation_bp, init_ip_geolocation_routes  # Import init_ip_geolocation_routes
from routes.ip_blacklist import ip_blacklist_bp, init_ip_blacklist_routes
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from modules.outsiders.hackernews import CyberNewsFetcher
from flask_wtf import CSRFProtect
from routes.blogs import blogs_bp
from routes.auth import auth_bp  # Import the auth blueprint
from models import User  # Import your User model
from flask_login import LoginManager
from flask_sitemap import Sitemap
from routes.header_checker import header_checker_bp
from routes.dnslookup import dnslookup_bp
from routes.hashtool import hash_bp
from routes.databreach import init_databreach_routes
import random
import bleach
from flask import render_template_string
import secrets
import base64
from flask import g
import os
from security_headers import add_security_headers
from security_headers import add_security_headers
from routes.home import TeaTimeTips