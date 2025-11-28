"""
Main Flask application
Refactored to use MySQL with SQLAlchemy
All French terms translated to English
"""
from flask import Flask
from flask_cors import CORS
from config import Config
from models import db

# Import blueprints (will be created below)
from routes.pages import pages_bp
from routes.riders import riders_bp
from routes.horses import horses_bp
from routes.recurring_lessons import recurring_lessons_bp
from routes.availability import availability_bp
from routes.schedule import schedule_bp
from routes.stats import stats_bp

def create_app():
    """Create and configure the Flask application"""
    app = Flask(__name__)
    app.config.from_object(Config)

    # Initialize extensions
    db.init_app(app)
    CORS(app, origins=Config.CORS_ORIGINS)

    # Create tables
    with app.app_context():
        db.create_all()
        print("✅ Database tables created/verified")

    # Initialize directories for static files
    Config.init_directories()

    # Register blueprints
    app.register_blueprint(pages_bp)
    app.register_blueprint(riders_bp, url_prefix='/api')
    app.register_blueprint(horses_bp, url_prefix='/api')
    app.register_blueprint(recurring_lessons_bp, url_prefix='/api')
    app.register_blueprint(availability_bp, url_prefix='/api')
    app.register_blueprint(schedule_bp, url_prefix='/api')
    app.register_blueprint(stats_bp, url_prefix='/api')

    print("✅ Application created successfully")
    return app

# Create app instance for WSGI servers (Gunicorn, PythonAnywhere)
app = create_app()

if __name__ == '__main__':
    app.run(
        debug=Config.DEBUG,
        host=Config.HOST,
        port=Config.PORT
    )
