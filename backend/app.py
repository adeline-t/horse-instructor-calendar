"""
Equestrian Management System - Flask Application
API-only backend (static files served separately)
"""
from flask import Flask
from flask_cors import CORS
from config import Config
from models import db
from dotenv import load_dotenv

# Load environment variables (optional for local dev)
load_dotenv()

def create_app(config_class=Config):
    """Application factory"""
    app = Flask(__name__)
    app.config.from_object(config_class)

    # Initialize extensions
    db.init_app(app)
    CORS(app, origins=config_class.CORS_ORIGINS)

    # Import blueprints
    from routes.riders import riders_bp
    from routes.horses import horses_bp
    from routes.recurring_lessons import recurring_lessons_bp
    from routes.availability import availability_bp
    from routes.schedule import schedule_bp
    from routes.stats import stats_bp

    # Register blueprints (all under /api prefix)
    app.register_blueprint(riders_bp, url_prefix='/api')
    app.register_blueprint(horses_bp, url_prefix='/api')
    app.register_blueprint(recurring_lessons_bp, url_prefix='/api')
    app.register_blueprint(availability_bp, url_prefix='/api')
    app.register_blueprint(schedule_bp, url_prefix='/api')
    app.register_blueprint(stats_bp, url_prefix='/api')

    # Health check endpoint
    @app.route('/health')
    def health():
        return {'status': 'healthy'}, 200

    # Create tables on startup
    with app.app_context():
        db.create_all()
        print("Database tables created successfully")

    return app


if __name__ == '__main__':
    app = create_app()
    app.run(debug=Config.DEBUG)
