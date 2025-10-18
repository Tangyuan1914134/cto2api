import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    API_KEY = os.getenv('API_KEY', 'default-api-key-please-change')
    BASE_URL = os.getenv('BASE_URL', 'http://localhost:5000')
    TARGET_WEB_URL = os.getenv('TARGET_WEB_URL', 'https://example.com')
    PORT = int(os.getenv('PORT', 5000))
    DEBUG = os.getenv('DEBUG', 'False').lower() == 'true'
    
    @staticmethod
    def validate():
        if Config.API_KEY == 'default-api-key-please-change':
            print("Warning: Using default API key. Please set API_KEY in .env file")
        return True
