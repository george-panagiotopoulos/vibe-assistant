import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Flask Configuration
SECRET_KEY = os.environ.get('FLASK_SECRET_KEY', 'vibe-assistant-secret-key-2024')
DEBUG = os.environ.get('FLASK_DEBUG', 'True').lower() == 'true'

# AWS Configuration
AWS_ACCESS_KEY_ID = os.environ.get('AWS_ACCESS_KEY_ID')
AWS_SECRET_ACCESS_KEY = os.environ.get('AWS_SECRET_ACCESS_KEY')
AWS_DEFAULT_REGION = os.environ.get('AWS_DEFAULT_REGION', 'us-east-1')
BEDROCK_MODEL_ID = os.environ.get('AWS_BEDROCK_MODEL_ID', 'anthropic.claude-3-5-sonnet-20240620-v1:0')

# GitHub Configuration
GITHUB_TOKEN = os.environ.get('GITHUB_TOKEN')
GITHUB_DEFAULT_REPO = os.environ.get('GITHUB_DEFAULT_REPO')

# Application Configuration
LOG_LEVEL = os.environ.get('LOG_LEVEL', 'INFO')
MAX_FILE_SIZE_KB = int(os.environ.get('MAX_FILE_SIZE_KB', '1000'))
DEFAULT_TASK_TYPE = os.environ.get('DEFAULT_TASK_TYPE', 'development')

class Config:
    """Flask configuration class"""
    
    # Flask settings
    SECRET_KEY = SECRET_KEY
    DEBUG = DEBUG
    
    # GitHub settings
    GITHUB_TOKEN = GITHUB_TOKEN
    
    # AWS Bedrock settings
    AWS_ACCESS_KEY_ID = AWS_ACCESS_KEY_ID
    AWS_SECRET_ACCESS_KEY = AWS_SECRET_ACCESS_KEY
    AWS_REGION = AWS_DEFAULT_REGION
    
    # Bedrock model settings
    BEDROCK_MODEL_ID = BEDROCK_MODEL_ID
    
    # Configuration file path
    CONFIG_FILE_PATH = os.environ.get('CONFIG_FILE_PATH', 'config/user_config.json')
    
    @classmethod
    def validate_config(cls):
        """Validate that required configuration is present"""
        required_vars = ['AWS_ACCESS_KEY_ID', 'AWS_SECRET_ACCESS_KEY']
        missing_vars = [var for var in required_vars if not getattr(cls, var)]
        
        if missing_vars:
            raise ValueError(f"Missing required environment variables: {', '.join(missing_vars)}")
        
        return True 