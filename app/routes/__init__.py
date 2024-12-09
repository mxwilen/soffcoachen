import os
import pkgutil
import importlib
from flask import Blueprint


def init_blueprints(app):
    """Dynamically import and register all Blueprints in the routes/ folder."""
    package_dir = os.path.dirname(__file__)  # Get the directory of the 'routes/' folder
    for _, module_name, _ in pkgutil.iter_modules([package_dir]):
        # Dynamically import the module
        module = importlib.import_module(f'{__name__}.{module_name}')
        
        # Iterate through all attributes in the module
        for attribute_name in dir(module):
            # Ignore private attributes (__name__, __file__, etc.)
            if attribute_name.startswith('__'):
                continue
            
            # Get the attribute from the module
            attribute = getattr(module, attribute_name)
            
            # Check if the attribute is a Blueprint
            if isinstance(attribute, Blueprint):
                app.register_blueprint(attribute)


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
