import importlib
import pkgutil
import os

from flask import Blueprint


def init_blueprints(app):
    package_dir = os.path.dirname(__file__)
    for _, module_name, _ in pkgutil.iter_modules([package_dir]):
        module = importlib.import_module(f'{__name__}.{module_name}')
        for attribute_name in dir(module):
            attribute = getattr(module, attribute_name)
            if isinstance(attribute, Blueprint):
                app.register_blueprint(attribute)