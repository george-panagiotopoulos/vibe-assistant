import json
import os
import logging
from typing import Dict, Any, List

logger = logging.getLogger(__name__)

class ConfigService:
    """Service for managing application configuration"""
    
    def __init__(self, config_file='config/user_config.json'):
        self.config_file = config_file
        self.ensure_config_file_exists()
    
    def ensure_config_file_exists(self):
        """Ensure the config file and directory exist"""
        try:
            # Create config directory if it doesn't exist
            config_dir = os.path.dirname(self.config_file)
            if config_dir and not os.path.exists(config_dir):
                os.makedirs(config_dir)
            
            # Create default config file if it doesn't exist
            if not os.path.exists(self.config_file):
                self._create_default_config()
                
        except Exception as e:
            logger.error(f"Error ensuring config file exists: {str(e)}")
    
    def _create_default_config(self):
        """Create a default configuration file"""
        default_config = {
            "github": {
                "token": "",
                "default_repo": ""
            },
            "aws": {
                "access_key_id": "",
                "secret_access_key": "",
                "region": "us-east-1",
                "bedrock_model_id": "anthropic.claude-sonnet-4-20250514-v1:0"
            },
            "non_functional_requirements": {
                "development": [
                    "Use TypeScript for type safety and better developer experience",
                    "Implement proper error handling with try-catch blocks and user feedback",
                    "Follow REST API conventions for endpoints and HTTP status codes",
                    "Include unit tests with at least 80% code coverage",
                    "Use responsive design principles for mobile compatibility",
                    "Implement proper input validation and sanitization",
                    "Follow security best practices (authentication, authorization, data protection)",
                    "Use meaningful variable and function names with clear documentation",
                    "Implement logging for debugging and monitoring purposes",
                    "Consider performance implications and optimize for speed"
                ],
                "refactoring": [
                    "Maintain existing functionality while improving code structure",
                    "Eliminate code duplication through proper abstraction",
                    "Improve variable and function naming for better readability",
                    "Extract complex logic into separate, testable functions",
                    "Optimize performance bottlenecks identified through profiling",
                    "Update and maintain comprehensive test coverage",
                    "Improve error handling and edge case management",
                    "Enhance documentation and inline comments",
                    "Follow consistent coding style and conventions",
                    "Consider backward compatibility when making changes"
                ],
                "testing": [
                    "Write comprehensive unit tests covering all functions and methods",
                    "Include integration tests for API endpoints and database interactions",
                    "Test edge cases, boundary conditions, and error scenarios",
                    "Use meaningful test descriptions that explain what is being tested",
                    "Implement mocking for external dependencies and services",
                    "Ensure tests are independent and can run in any order",
                    "Include performance tests for critical application paths",
                    "Test user interface components and user interactions",
                    "Validate data integrity and consistency in tests",
                    "Use code coverage tools to identify untested code paths"
                ]
            },
            "system_prompt": {
                "development": "You are an expert software developer with deep knowledge of modern web technologies, best practices, and design patterns. Focus on creating clean, maintainable, and scalable solutions.",
                "refactoring": "You are an expert code reviewer and software architect specializing in improving existing codebases. Focus on enhancing structure, performance, and maintainability while preserving functionality.",
                "testing": "You are an expert QA engineer and test automation specialist. Focus on comprehensive testing strategies, edge cases, and ensuring software quality and reliability."
            },
            "preferences": {
                "default_task_type": "development",
                "auto_enhance_prompts": True,
                "include_file_context": True,
                "max_file_size_kb": 1000,
                "auto_enhance": False,
                "include_file_content": True,
                "max_file_size": 100,
                "editor_theme": "light"
            }
        }
        
        try:
            with open(self.config_file, 'w') as f:
                json.dump(default_config, f, indent=2)
            logger.info(f"Created default configuration file: {self.config_file}")
        except Exception as e:
            logger.error(f"Error creating default config: {str(e)}")
    
    def get_config(self) -> Dict[str, Any]:
        """Get the current configuration"""
        try:
            with open(self.config_file, 'r') as f:
                config = json.load(f)
            return config
        except FileNotFoundError:
            logger.warning("Config file not found, creating default")
            self._create_default_config()
            return self.get_config()
        except json.JSONDecodeError as e:
            logger.error(f"Error parsing config file: {str(e)}")
            raise Exception("Configuration file is corrupted")
        except Exception as e:
            logger.error(f"Error reading config: {str(e)}")
            raise Exception(f"Failed to read configuration: {str(e)}")
    
    def update_config(self, updates: Dict[str, Any]) -> Dict[str, Any]:
        """Update configuration with new values, preserving existing credentials"""
        try:
            config = self.get_config()
            
            # Preserve existing credentials if they exist and new ones are empty
            if 'aws' in updates and 'aws' in config:
                aws_updates = updates['aws']
                existing_aws = config['aws']
                
                # Preserve existing credentials if new ones are empty
                if not aws_updates.get('access_key_id') and existing_aws.get('access_key_id'):
                    aws_updates['access_key_id'] = existing_aws['access_key_id']
                if not aws_updates.get('secret_access_key') and existing_aws.get('secret_access_key'):
                    aws_updates['secret_access_key'] = existing_aws['secret_access_key']
            
            if 'github' in updates and 'github' in config:
                github_updates = updates['github']
                existing_github = config['github']
                
                # Preserve existing token if new one is empty
                if not github_updates.get('token') and existing_github.get('token'):
                    github_updates['token'] = existing_github['token']
                if not github_updates.get('default_repo') and existing_github.get('default_repo'):
                    github_updates['default_repo'] = existing_github['default_repo']
            
            # Deep merge the updates
            config = self._deep_merge(config, updates)
            
            # Save updated config
            with open(self.config_file, 'w') as f:
                json.dump(config, f, indent=2)
            
            logger.info("Configuration updated successfully")
            return config
            
        except Exception as e:
            logger.error(f"Error updating config: {str(e)}")
            raise Exception(f"Failed to update configuration: {str(e)}")
    
    def _deep_merge(self, base: Dict, updates: Dict) -> Dict:
        """Deep merge two dictionaries"""
        result = base.copy()
        
        for key, value in updates.items():
            if key in result and isinstance(result[key], dict) and isinstance(value, dict):
                result[key] = self._deep_merge(result[key], value)
            else:
                result[key] = value
        
        return result
    
    def get_requirements(self, task_type: str = None) -> Dict[str, List[str]]:
        """Get non-functional requirements"""
        try:
            config = self.get_config()
            requirements = config.get('non_functional_requirements', {})
            
            if task_type:
                return {task_type: requirements.get(task_type, [])}
            
            return requirements
            
        except Exception as e:
            logger.error(f"Error getting requirements: {str(e)}")
            return {}
    
    def update_requirements(self, task_type: str, requirements: List[str]) -> Dict[str, List[str]]:
        """Update requirements for a specific task type"""
        try:
            config = self.get_config()
            
            if 'non_functional_requirements' not in config:
                config['non_functional_requirements'] = {}
            
            config['non_functional_requirements'][task_type] = requirements
            
            # Save updated config
            with open(self.config_file, 'w') as f:
                json.dump(config, f, indent=2)
            
            logger.info(f"Requirements updated for task type: {task_type}")
            return config['non_functional_requirements']
            
        except Exception as e:
            logger.error(f"Error updating requirements: {str(e)}")
            raise Exception(f"Failed to update requirements: {str(e)}")
    
    def get_system_prompt(self, task_type: str = 'development') -> str:
        """Get system prompt for a specific task type"""
        try:
            config = self.get_config()
            system_prompts = config.get('system_prompt', {})
            return system_prompts.get(task_type, "")
        except Exception as e:
            logger.error(f"Error getting system prompt: {str(e)}")
            return ""
    
    def update_system_prompt(self, task_type: str, prompt: str) -> None:
        """Update system prompt for a specific task type"""
        try:
            config = self.get_config()
            
            if 'system_prompt' not in config:
                config['system_prompt'] = {}
            
            config['system_prompt'][task_type] = prompt
            
            # Save updated config
            with open(self.config_file, 'w') as f:
                json.dump(config, f, indent=2)
            
            logger.info(f"System prompt updated for task type: {task_type}")
            
        except Exception as e:
            logger.error(f"Error updating system prompt: {str(e)}")
            raise Exception(f"Failed to update system prompt: {str(e)}")
    
    def get_github_config(self) -> Dict[str, str]:
        """Get GitHub configuration"""
        try:
            config = self.get_config()
            return config.get('github', {})
        except Exception as e:
            logger.error(f"Error getting GitHub config: {str(e)}")
            return {}
    
    def get_aws_config(self) -> Dict[str, str]:
        """Get AWS configuration"""
        try:
            config = self.get_config()
            return config.get('aws', {})
        except Exception as e:
            logger.error(f"Error getting AWS config: {str(e)}")
            return {}
    
    def validate_config(self) -> Dict[str, Any]:
        """Validate the current configuration"""
        try:
            config = self.get_config()
            validation_result = {
                'is_valid': True,
                'errors': [],
                'warnings': []
            }
            
            # Check GitHub config
            github_config = config.get('github', {})
            if not github_config.get('token'):
                validation_result['warnings'].append("GitHub token not configured")
            
            # Check AWS config
            aws_config = config.get('aws', {})
            if not aws_config.get('access_key_id') or not aws_config.get('secret_access_key'):
                validation_result['errors'].append("AWS credentials not configured")
                validation_result['is_valid'] = False
            
            # Check non-functional requirements
            requirements = config.get('non_functional_requirements', {})
            required_task_types = ['development', 'refactoring', 'testing']
            for task_type in required_task_types:
                if task_type not in requirements or not requirements[task_type]:
                    validation_result['warnings'].append(f"No requirements defined for {task_type}")
            
            return validation_result
            
        except Exception as e:
            logger.error(f"Error validating config: {str(e)}")
            return {
                'is_valid': False,
                'errors': [f"Configuration validation failed: {str(e)}"],
                'warnings': []
            }
    
    def export_config(self) -> str:
        """Export configuration as JSON string"""
        try:
            config = self.get_config()
            # Remove sensitive information for export
            export_config = config.copy()
            if 'github' in export_config and 'token' in export_config['github']:
                export_config['github']['token'] = '***HIDDEN***'
            if 'aws' in export_config:
                if 'access_key_id' in export_config['aws']:
                    export_config['aws']['access_key_id'] = '***HIDDEN***'
                if 'secret_access_key' in export_config['aws']:
                    export_config['aws']['secret_access_key'] = '***HIDDEN***'
            
            return json.dumps(export_config, indent=2)
            
        except Exception as e:
            logger.error(f"Error exporting config: {str(e)}")
            raise Exception(f"Failed to export configuration: {str(e)}")
    
    def backup_config(self) -> str:
        """Create a backup of the current configuration"""
        try:
            import datetime
            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_filename = f"{self.config_file}.backup_{timestamp}"
            
            config = self.get_config()
            with open(backup_filename, 'w') as f:
                json.dump(config, f, indent=2)
            
            logger.info(f"Configuration backed up to: {backup_filename}")
            return backup_filename
            
        except Exception as e:
            logger.error(f"Error backing up config: {str(e)}")
            raise Exception(f"Failed to backup configuration: {str(e)}") 