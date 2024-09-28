# app.py
from imports import *  # Import everything from imports.py
import logging
from logging.handlers import RotatingFileHandler
from werkzeug.middleware.proxy_fix import ProxyFix


# Initialize Flask app
app = Flask(__name__)

if not app.debug:
    # Set up logging for production
    file_handler = RotatingFileHandler('error.log', maxBytes=10240, backupCount=10)
    file_handler.setLevel(logging.WARNING)
    formatter = logging.Formatter('%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]')
    file_handler.setFormatter(formatter)
    app.logger.addHandler(file_handler)




# Configurations
app.config['SERVER_NAME'] = None
app.config['SECRET_KEY'] = '@EvilMrPopEyesNeverFailesToSurrenderWhen@'
app.config['SESSION_COOKIE_SECURE'] = True  # Ensures cookies are only sent over HTTPS
app.config['SESSION_COOKIE_HTTPONLY'] = True  # Prevents JavaScript access to cookies
app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'  # Protects against CSRF in cross-origin requests
app.config['APP_ENV'] = 'production'
app.config['SQLALCHEMY_POOL_SIZE'] = 10
app.config['SQLALCHEMY_POOL_TIMEOUT'] = 30  # Adjust pool size and timeout based on your traffic
app.config['DEBUG'] = False  # This is already set

@app.after_request
def remove_server_header(response):
    response.headers['X-Powered-By'] = ''
    return response

# Initialize extensions
csrf = CSRFProtect(app)
ext = Sitemap(app=app)

# Allowed HTML tags for content sanitization
ALLOWED_TAGS = ['p', 'strong', 'em', 'ul', 'li', 'br']

# Flask-Limiter configuration (Rate limiting)
limiter = Limiter(
    key_func=get_remote_address,
    storage_uri='redis://localhost:6379/0',  # Using Redis for rate limiting
    app=app,
    on_breach=lambda limit: (jsonify({"error": "Too many requests, please try again later."}), 429)
)

# Flask-Login configuration (User authentication)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'auth.login'  # Redirect to login view if unauthorized

# User loader for Flask-Login
@login_manager.user_loader
def load_user(user_id):
    return User.get_user_by_id(user_id)


### Context Processors (Injecting values globally into templates) ###

@app.context_processor
def get_quote():
    """Inject a random tea tip into templates."""
    tip_of_the_table = random.choice(TeaTimeTips)
    return {'tip_of_the_table': tip_of_the_table}


app.wsgi_app = ProxyFix(app.wsgi_app, x_for=1)

@app.context_processor
def get_ip():
    """Inject the user's IP address into templates."""
    x_forwarded_for = request.headers.get('X-Forwarded-For', None)
    if x_forwarded_for:
        user_ip = x_forwarded_for.split(',')[0].strip()
    else:
        user_ip = request.remote_addr
    return {'ip': user_ip}



@app.context_processor
def inject_latest_cyber_news():
    """Inject the latest cybersecurity news into templates."""
    news_fetcher = CyberNewsFetcher()
    latest_news = news_fetcher.get_news()[:10]  # Get the latest 10 news items
    return {'latest_cyber_news': latest_news}


### Request Hooks ###

@app.before_request
def generate_nonce():
    """Generate a nonce for CSP headers."""
    g.csp_nonce = base64.b64encode(os.urandom(16)).decode('utf-8')


@app.after_request
def apply_security_headers(response):
    """Apply security headers to the response."""
    return add_security_headers(response)


### Utility Functions ###

def sanitize_html(content):
    """Sanitize HTML content to allow only certain tags."""
    return bleach.clean(content, tags=ALLOWED_TAGS, strip=True)


### Routes ###

# Dynamically generate sitemap.xml
@app.route('/sitemap.xml', methods=['GET'])
def sitemap():
    """Generate and return the sitemap.xml."""
    return ext.sitemap()


# Serve robots.txt
@app.route('/robots.txt')
def robots_txt():
    """Serve the robots.txt file."""
    return send_from_directory(app.root_path, 'robots.txt')


### Error Handlers ###

@app.errorhandler(500)
def internal_error(error):
    """Handle internal server errors."""
    return "An unexpected error occurred. Please try again later.", 500

@app.errorhandler(404)
def not_found_error(error):
    """Handle 404 Not Found errors."""
    return "The requested resource could not be found.", 404

@app.errorhandler(403)
def forbidden_error(error):
    """Handle 403 Forbidden errors."""
    return "You don't have permission to access this resource.", 403


### Blueprint Registration ###

# Register app blueprints
app.register_blueprint(home_bp)
app.register_blueprint(about_bp)
app.register_blueprint(passwordgen_bp)
app.register_blueprint(whois_bp)
app.register_blueprint(mac_lookup_bp)
app.register_blueprint(blogs_bp)
app.register_blueprint(auth_bp)
app.register_blueprint(hash_bp)
app.register_blueprint(header_checker_bp)
app.register_blueprint(dnslookup_bp)

# Initialize and register IP-related routes
init_ip_geolocation_routes(limiter)
app.register_blueprint(ip_geolocation_bp)

init_ip_blacklist_routes(limiter)
app.register_blueprint(ip_blacklist_bp)

init_databreach_routes(limiter)
app.register_blueprint(databreach_bp)


### Main Application Entry Point ###

if __name__ == '__main__':
    app.run()
