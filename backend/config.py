"""
Configuration for Equestrian Management System
Migrated from JSON files to MySQL database
All French terms translated to English
"""
import os

class Config:
    # Base directories
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))

    # MySQL Configuration for PythonAnywhere
    # REPLACE WITH YOUR ACTUAL CREDENTIALS
    MYSQL_USER = os.environ.get('MYSQL_USER', 'yourusername')
    MYSQL_PASSWORD = os.environ.get('MYSQL_PASSWORD', 'yourpassword')
    MYSQL_HOST = os.environ.get('MYSQL_HOST', 'yourusername.mysql.pythonanywhere-services.com')
    MYSQL_DB = os.environ.get('MYSQL_DB', 'yourusername$equestrian_db')

    # SQLAlchemy Configuration
    SQLALCHEMY_DATABASE_URI = f'mysql+pymysql://{MYSQL_USER}:{MYSQL_PASSWORD}@{MYSQL_HOST}/{MYSQL_DB}'
    SQLALCHEMY_POOL_RECYCLE = 280  # Critical for PythonAnywhere (5 min timeout)
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ENGINE_OPTIONS = {
        'pool_pre_ping': True,
        'pool_recycle': 280,
    }

    # Application Configuration
    SECRET_KEY = os.environ.get('SECRET_KEY', 'your-secret-key-change-in-production')
    DEBUG = os.environ.get('DEBUG', 'False').lower() == 'true'
    HOST = '0.0.0.0'
    PORT = 4004

    # CORS Configuration
    CORS_ORIGINS = ['*']  # Restrict in production

    @staticmethod
    def init_directories():
        """Create necessary directories (now mostly for static files)"""
        static_dir = os.path.join(Config.BASE_DIR, 'static')
        os.makedirs(static_dir, exist_ok=True)
        print(f"✅ Static directory created/verified: {static_dir}")
