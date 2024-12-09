import os
import secrets
from flask import Flask
from flask_mail import Mail
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager
from flask_migrate import Migrate
from flask_wtf.csrf import CSRFProtect
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
import logging

from .utils import get_database_uri


def create_app():
    """Application factory."""
    print("Initializing the Flask application...")
    
    app = Flask(__name__, template_folder='../templates/', static_folder='../static')

    app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'
    app.config['MAIL_SERVER'] = 'smtp.googlemail.com'
    app.config['MAIL_PORT'] = 587
    app.config['MAIL_USE_TLS'] = True
    
    # Configure the app
    # app.config.from_object("config.Config")

    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['SQLALCHEMY_DATABASE_URI'] = get_database_uri()


    if 'SECRET_KEY' in os.environ:
        app.config['SECRET_KEY'] = os.environ['SECRET_KEY']
    else:
        print("No SECRET_KEY found. Generating new.")
        app.config['SECRET_KEY'] = secrets.token_hex()

    # Initialize Flask extensions (but do not bind them to the app yet)
    db = SQLAlchemy()
    migrate = Migrate()
    csrf = CSRFProtect()
    mail = Mail()
    bcrypt = Bcrypt()
    limiter = Limiter(key_func=get_remote_address, default_limits=["200 per day", "50 per hour"])
    login_manager = LoginManager()

    # Logging configuration
    logging.basicConfig(
        filename="suspicious_activity.log",
        level=logging.WARNING,
        format="%(asctime)s - %(levelname)s - %(message)s",
    )

    tags = ["transfers & truppbygge", "matcher", "kultur", "förening", "övrigt"]

    # Initialize Flask extensions with the app
    db.init_app(app)
    migrate.init_app(app, db)
    csrf.init_app(app)
    mail.init_app(app)
    bcrypt.init_app(app)
    limiter.init_app(app)
    login_manager.init_app(app)
    login_manager.login_view = "auth.login"
    login_manager.login_message_category = "info"

    with app.app_context():
        # Import models to ensure they are registered with SQLAlchemy
        # from . import models  # Import models here

        # Import and register blueprints
        # from routes import auth_routes, no_auth_routes, ajax_routes, error_routes
        # app.register_blueprint(auth_routes.bp)
        # app.register_blueprint(no_auth_routes.bp)
        # app.register_blueprint(ajax_routes.bp)
        # app.register_blueprint(error_pages.bp)

        from soffcoachen.routes import init_blueprints
        # from routes import init_blueprints
        init_blueprints(app)

        # Generate dummy data
        from dummy_data import generate_dummy
        # generate_dummy(db)
        db.drop_all()
        db.session.commit()
        db.create_all()

        # from .models import Team
        # teams = [(team.name) for team in Team.query.all()]

    return app



#if __name__ == '__main__':
#   app.run()
