# app/__init__.py
from flask import Flask

def create_app():
    app = Flask(__name__, template_folder='templates', static_folder='static')

    with app.app_context():
        from . import views
        views.init_limiter(app)  # Initialize the limiter with the app context
    
    return app