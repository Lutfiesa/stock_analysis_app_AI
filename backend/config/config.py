"""
Configuration Management for Stock Analysis App
Handles environment variables and application settings
"""
import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from .env file
BASE_DIR = Path(__file__).resolve().parent.parent.parent
load_dotenv(BASE_DIR / '.env')


class Config:
    """Application configuration"""
    
    # Environment
    APP_ENV = os.getenv('APP_ENV', 'development')
    DEBUG = os.getenv('DEBUG', 'true').lower() == 'true'
    
    # Server settings
    BACKEND_HOST = os.getenv('BACKEND_HOST', '127.0.0.1')
    BACKEND_PORT = int(os.getenv('BACKEND_PORT', '8000'))
    
    # API Keys
    SECTORS_API_KEY = os.getenv('SECTORS_API_KEY', '')
    TWELVEDATA_API_KEY = os.getenv('TWELVEDATA_API_KEY', '')
    ALPHAVANTAGE_API_KEY = os.getenv('ALPHAVANTAGE_API_KEY', '')
    
    # Database
    DATABASE_PATH = os.getenv('DATABASE_PATH', str(BASE_DIR / 'data' / 'stock_cache.db'))
    
    # Cache settings
    CACHE_EXPIRATION = int(os.getenv('CACHE_EXPIRATION', '3600'))
    ENABLE_CACHE = os.getenv('ENABLE_CACHE', 'true').lower() == 'true'
    
    # Rate limiting
    RATE_LIMIT_PER_MINUTE = int(os.getenv('RATE_LIMIT_PER_MINUTE', '60'))
    
    # Logging
    LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
    LOG_FILE = os.getenv('LOG_FILE', str(BASE_DIR / 'logs' / 'app.log'))
    LOG_API_REQUESTS = os.getenv('LOG_API_REQUESTS', 'true').lower() == 'true'
    
    # Security
    SECRET_KEY = os.getenv('SECRET_KEY', 'development-secret-key-change-in-production')
    CORS_ORIGINS = os.getenv('CORS_ORIGINS', 'http://localhost:5173,http://127.0.0.1:5173').split(',')
    
    # Optional settings
    MAX_HISTORICAL_DAYS = int(os.getenv('MAX_HISTORICAL_DAYS', '365'))
    
    @classmethod
    def validate(cls):
        """Validate required configuration"""
        missing = []
        
        if not cls.SECTORS_API_KEY and not cls.TWELVEDATA_API_KEY:
            missing.append('At least one API key (SECTORS_API_KEY or TWELVEDATA_API_KEY) is required')
        
        if missing:
            raise ValueError(f"Missing configuration: {', '.join(missing)}")
        
        return True
    
    @classmethod
    def get_api_base_urls(cls):
        """Get base URLs for all APIs"""
        return {
            'sectors': 'https://api.sectors.app/v1',
            'twelvedata': 'https://api.twelvedata.com',
            'alphavantage': 'https://www.alphavantage.co/query'
        }


# Create necessary directories
def ensure_directories():
    """Ensure required directories exist"""
    dirs = [
        BASE_DIR / 'data',
        BASE_DIR / 'logs',
    ]
    for directory in dirs:
        directory.mkdir(exist_ok=True, parents=True)


# Initialize on import
ensure_directories()

# Export config
config = Config()
