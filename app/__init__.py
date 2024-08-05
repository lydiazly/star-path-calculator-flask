# app/__init__.py
from flask import Flask
from flask_cors import CORS

def create_app():
    app = Flask(__name__, template_folder='templates', static_folder='static')
    # Initialize CORS with the app, enable CORS for all routes
    CORS(app)

    with app.app_context():
        from . import views  # noqa
        # views.init_limiter(app)  # Initialize the limiter with the app context
    
    return app