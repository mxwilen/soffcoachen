from flask import render_template, Blueprint, current_app as app
from flask_limiter.errors import RateLimitExceeded

error_bp = Blueprint('error', __name__)

@error_bp.errorhandler(400)
def bad_request(e):
    # Handles CSRF errors aswell.
    return render_template('error_pages/400.html'), 400

@error_bp.errorhandler(403)
def forbidden(e):
    return render_template('error_pages/403.html'), 403

@error_bp.errorhandler(404)
def page_not_found(e):
    print("error 404")
    return render_template('error_pages/404.html'), 404

@error_bp.errorhandler(500)
def internal_server_error(e):
    return render_template('error_pages/500.html'), 500

@error_bp.errorhandler(RateLimitExceeded)
def handle_rate_limit_exceeded(e):
    return render_template("error_pages/429.html"), 429
