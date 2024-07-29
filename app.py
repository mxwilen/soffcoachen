import os
import secrets
from flask import Flask
from flask_mail import Mail
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager
from flask_migrate import Migrate
from flask_wtf.csrf import CSRFProtect
from azureproject.get_conn import get_conn

from routes import init_blueprints

app = Flask(__name__, template_folder='templates', static_folder='static')

app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'
app.config['MAIL_SERVER'] = 'smtp.googlemail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True

# WEBSITE_HOSTNAME exists only in production environment
if not 'WEBSITE_HOSTNAME' in os.environ:
   # local development, where we'll use environment variables
   print("Loading config.development and environment variables from .env file.")
   app.config.from_object('azureproject.development')
else:
   # production
   print("Loading config.production.")
   app.config.from_object('azureproject.production')

with app.app_context():
    app.config.update(
        SQLALCHEMY_TRACK_MODIFICATIONS=False,
        SQLALCHEMY_DATABASE_URI=get_conn(),
    )


if 'SECRET_KEY' in os.environ:
    app.config['SECRET_KEY'] = os.environ['SECRET_KEY']
else:
    print("No SECRET_KEY found. Generating new!!!")
    app.config['SECRET_KEY'] = secrets.token_hex()


# Initialize the database connection
db = SQLAlchemy(app)

# Enable Flask-Migrate commands "flask db init/migrate/upgrade" to work
migrate = Migrate(app, db)

# CSRF-token creation/usage
csrf = CSRFProtect(app)
csrf.init_app(app)

# For reseting mails with code.
mail = Mail(app)

# For encrypting passwords.
bcrypt = Bcrypt(app)

# Handling of logged in user.
login_manager = LoginManager(app)
login_manager.login_view = 'login'
login_manager.login_message_category = 'info'


tags = [
        'transfers & truppbygge',
        'matcher',
        'kultur',
        'förening',
        'övrigt'
    ]


# The import must be done after db initialization due to circular import issue.
with app.app_context():
    from dummy_data import generate_dummy
    # generate_dummy()
    
    from models import Team
    teams = [(team.name) for team in Team.query.all()]

init_blueprints(app)



if __name__ == '__main__':
   app.run()
