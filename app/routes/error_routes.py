from flask import render_template, Blueprint
from flask_limiter.errors import RateLimitExceeded

error_bp = Blueprint('error', __name__)

def register_error_handlers(app):
    """Registers global error handlers for the Flask app."""
    
    @app.errorhandler(400)
    def bad_request(e):
        """Handles bad request (400) errors."""
        return render_template('error_pages/400.html'), 400

    @app.errorhandler(403)
    def forbidden(e):
        """Handles forbidden (403) errors."""
        return render_template('error_pages/403.html'), 403

    @app.errorhandler(404)
    def page_not_found(e):
        """Handles page not found (404) errors."""
        return render_template('error_pages/404.html'), 404

    @app.errorhandler(500)
    def internal_server_error(e):
        """Handles internal server error (500) errors."""
        return render_template('error_pages/500.html'), 500

    @app.errorhandler(RateLimitExceeded)
    def handle_rate_limit_exceeded(e):
        """Handles rate limit exceeded (429) errors."""
        return render_template("error_pages/429.html"), 429