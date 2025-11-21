# Define the __all__ variable
__all__ = ["auth", "db", "plotting", "querying", "app"]

# Import the submodules
from . import auth
from . import db
from . import plotting
from . import querying
from . import user

"""
FLASK CODE
"""
import os
from flask import Flask
# from flask_cors import CORS       # Not available on VM

def create_app(test_conf=None):
    # Create and configure the app
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(
        SECRET_KEY='290125',
        DATABASE=os.path.join(app.instance_path, 'flaskr.sqlite')
    )

    if test_conf is None:
        # Load instance conf when not testing
        app.config.from_pyfile('config.py', silent=True)
    else:
        app.config.from_pyfile(test_conf)

    # Ensure instance folder exists
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass
    
    db.init_app(app)
    app.register_blueprint(auth.bp)
    app.register_blueprint(user.bp)

    #CORS(app)   # Enable CORS
    return app
