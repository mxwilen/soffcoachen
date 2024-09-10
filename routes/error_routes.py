from flask import render_template
from app import app

@app.errorhandler(400)
def bad_request(e):
    # Handles CSRF errors aswell.
    return render_template('error_pages/400.html'), 400

@app.errorhandler(403)
def forbidden(e):
    return render_template('error_pages/403.html'), 403

@app.errorhandler(404)
def page_not_found(e):
    return render_template('error_pages/404.html'), 404

@app.errorhandler(500)
def internal_server_error(e):
    return render_template('error_pages/500.html'), 500