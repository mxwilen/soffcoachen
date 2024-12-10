from flask import Flask
import secrets
import os

from config import Config
from app.extensions import db, migrate, mail, bcrypt, limiter, login_manager, csrf
from app.config_logging import configure_logging

def create_app():
    """Application factory function."""
    print("Initializing the Flask application...")

    # Create the app instance
    app = Flask(__name__, template_folder='templates/', static_folder='static/')

    # Load the configuration
    app.config.from_object(Config)

    # Log errors to the console
    import logging
    if not app.debug:
        handler = logging.StreamHandler()
        handler.setLevel(logging.ERROR)
        app.logger.addHandler(handler)

    # Generate a SECRET_KEY if not found in environment variables
    if 'SECRET_KEY' in os.environ:
        app.config['SECRET_KEY'] = os.environ['SECRET_KEY']
    else:
        print("No SECRET_KEY found. Generating new.")
        app.config['SECRET_KEY'] = secrets.token_hex()

    # Initialize logging
    configure_logging()

    # Initialize Flask extensions
    db.init_app(app)
    migrate.init_app(app, db)
    mail.init_app(app)
    bcrypt.init_app(app)
    limiter.init_app(app)
    csrf.init_app(app)
    login_manager.init_app(app)

    # Configure login manager
    login_manager.login_view = "no_auth.login"
    login_manager.login_message_category = "info"

    # Register blueprints
    # from app.config_blueprints import register_blueprints
    from app.routes import init_blueprints, register_blueprints
    register_blueprints(app)
    # init_blueprints(app)

    with app.app_context():
        from dummy_data import generate_dummy
        generate_dummy(app, db)

        # from .models import Team  # Import models inside app context
        # Query the teams and make them part of the app config
        # app.config['TEAMS'] = [team.name for team in Team.query.all()]
        # app.config['TAGS'] = ["transfers & truppbygge", "matcher", "kultur", "förening", "övrigt"]


    return app

