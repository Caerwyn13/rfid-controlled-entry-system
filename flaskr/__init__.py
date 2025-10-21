# Define the __all__ variable
__all__ = ["db", "plotting"]

# Import the submodules
from . import db
from . import plotting


"""
FLASK CODE
"""
import os
from flask import Flask

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

    # Simple test page
    @app.route('/hello')
    def hello():
        return 'Hello!'
    
    from . import db
    db.init_app(app)
    
    return app
