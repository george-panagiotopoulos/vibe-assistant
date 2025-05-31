import os
import logging
from dotenv import load_dotenv
from pathlib import Path

logger = logging.getLogger(__name__)

class EnvironmentLoader:
    """Aggressive environment variable loader with multiple fallback strategies"""
    
    def __init__(self):
        self.loaded = False
        self.env_paths = []
        self.load_environment()
    
    def load_environment(self):
        """Load environment variables from multiple possible locations"""
        # Try multiple .env file locations
        possible_paths = [
            Path(__file__).parent.parent.parent / '.env',  # Root level
            Path(__file__).parent.parent / '.env',         # Backend level
            Path('.env'),                                   # Current directory
            Path('../.env'),                               # Parent directory
        ]
        
        for env_path in possible_paths:
            if env_path.exists():
                logger.info(f"Loading .env from: {env_path}")
                load_dotenv(env_path, override=True)
                self.env_paths.append(str(env_path))
                self.loaded = True
        
        # Force reload from the first found .env file
        if self.env_paths:
            load_dotenv(self.env_paths[0], override=True)
        
        # Log what we found
        self.log_environment_status()
    
    def log_environment_status(self):
        """Log the current environment variable status"""
        logger.info("=== ENVIRONMENT STATUS ===")
        logger.info(f"Loaded .env files: {self.env_paths}")
        
        # Check critical variables
        critical_vars = [
            'AWS_ACCESS_KEY_ID',
            'AWS_SECRET_ACCESS_KEY', 
            'AWS_DEFAULT_REGION',
            'AWS_BEDROCK_MODEL_ID',
            'GITHUB_TOKEN',
            'GITHUB_DEFAULT_REPO'
        ]
        
        for var in critical_vars:
            value = os.environ.get(var)
            if value:
                # Show first 10 chars for security
                display_value = value[:10] + '...' if len(value) > 10 else value
                logger.info(f"{var}: {display_value}")
            else:
                logger.warning(f"{var}: NOT SET")
    
    def force_reload(self):
        """Force reload environment variables"""
        self.load_environment()
    
    def get_env(self, key, default=None):
        """Get environment variable with fallback"""
        value = os.environ.get(key, default)
        if not value and not self.loaded:
            # Try reloading if we haven't loaded successfully
            self.force_reload()
            value = os.environ.get(key, default)
        return value
    
    def ensure_loaded(self):
        """Ensure environment is loaded, reload if necessary"""
        if not self.loaded or not os.environ.get('AWS_ACCESS_KEY_ID'):
            self.force_reload()

# Global instance
env_loader = EnvironmentLoader() 