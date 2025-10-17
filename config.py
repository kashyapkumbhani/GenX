import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class Config:
    """Base configuration"""
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev-key-for-development-only')
    STATIC_FOLDER = 'static'
    TEMPLATES_FOLDER = 'templates'
    OUTPUT_DIR = os.path.join(os.path.dirname(__file__), 'output')
    TEMPLATE_DIR = os.path.join(os.path.dirname(__file__), 'template')
    
class DevelopmentConfig(Config):
    """Development configuration"""
    DEBUG = True
    
class ProductionConfig(Config):
    """Production configuration"""
    DEBUG = False

# Configuration dictionary
config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}