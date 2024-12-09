def register_blueprints(app):
    """Registers all the blueprints for the application."""
    from app.routes.auth_routes import auth_bp
    from app.routes.no_auth_routes import no_auth_bp
    from app.routes.ajax_routes import ajax_bp
    from app.routes.error_routes import error_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(no_auth_bp)
    app.register_blueprint(ajax_bp)
    app.register_blueprint(error_bp)