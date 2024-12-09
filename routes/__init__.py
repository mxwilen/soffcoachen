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

