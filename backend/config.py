"""
Application Configuration
"""
import os

class Config:
    """Base configuration"""

    # Flask
    SECRET_KEY = os.environ.get('SECRET_KEY', 'dev-secret-key-change-in-production')
    DEBUG = os.environ.get('DEBUG', 'False').lower() == 'true'

    # Database (MySQL on PythonAnywhere)
    MYSQL_USER = os.environ.get('MYSQL_USER', 'your_username')
    MYSQL_PASSWORD = os.environ.get('MYSQL_PASSWORD', 'your_password')
    MYSQL_HOST = os.environ.get('MYSQL_HOST', 'your_username.mysql.pythonanywhere-services.com')
    MYSQL_DB = os.environ.get('MYSQL_DB', 'your_username$equestrian_db')

    SQLALCHEMY_DATABASE_URI = f'mysql+pymysql://{MYSQL_USER}:{MYSQL_PASSWORD}@{MYSQL_HOST}/{MYSQL_DB}'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ENGINE_OPTIONS = {
        'pool_recycle': 280,
        'pool_pre_ping': True,
    }

    # CORS
    # TODO: Change this to your actual frontend domain(s) in production
    # Example: ['https://yourusername.github.io', 'https://yourdomain.com']
    CORS_ORIGINS = os.environ.get('CORS_ORIGINS', '*').split(',')
