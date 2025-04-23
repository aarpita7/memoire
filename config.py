import os

class Config:
    # Database configuration
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'sqlite:///journal.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Security configuration
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'your-secret-key-here'
    
    # Session configuration
    PERMANENT_SESSION_LIFETIME = 1800  # 30 minutes 