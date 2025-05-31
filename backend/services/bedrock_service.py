import boto3
import json
import logging
import os
from dotenv import load_dotenv
from botocore.exceptions import ClientError, NoCredentialsError
from config.settings import Config

# Load environment variables
load_dotenv()

logger = logging.getLogger(__name__)

class BedrockService:
    """Service for interacting with AWS Bedrock AI models"""
    
    def __init__(self):
        self.client = None
        self.model_id = 'anthropic.claude-3-5-sonnet-20240620-v1:0'  # Use the working model
        self.region = 'us-east-1'  # Changed to us-east-1 as specified
        self._initialize_client()
    
    def _load_user_config(self):
        """Load AWS credentials from user config file"""
        try:
            config_path = os.path.join(os.path.dirname(__file__), '..', 'config', 'user_config.json')
            if os.path.exists(config_path):
                with open(config_path, 'r') as f:
                    config = json.load(f)
                    aws_config = config.get('aws', {})
                    return {
                        'access_key_id': aws_config.get('access_key_id'),
                        'secret_access_key': aws_config.get('secret_access_key'),
                        'region': aws_config.get('region', 'us-east-1'),
                        'model_id': aws_config.get('bedrock_model_id', self.model_id)
                    }
        except Exception as e:
            logger.warning(f"Could not load user config: {str(e)}")
        
        # Fallback to environment variables
        return {
            'access_key_id': os.getenv("AWS_ACCESS_KEY_ID"),
            'secret_access_key': os.getenv("AWS_SECRET_ACCESS_KEY"),
            'region': os.getenv("AWS_REGION", 'us-east-1'),
            'model_id': self.model_id
        }
    
    def _initialize_client(self):
        """Initialize AWS Bedrock client following the working example pattern"""
        try:
            # Load credentials from user config first, then environment variables
            creds = self._load_user_config()
            
            if not creds['access_key_id'] or not creds['secret_access_key']:
                raise Exception("AWS credentials not found in user config or environment variables")
            
            self.client = boto3.client(
                service_name='bedrock-runtime',  # Following the working example
                region_name=creds['region'],
                aws_access_key_id=creds['access_key_id'],
                aws_secret_access_key=creds['secret_access_key'],
            )
            
            # Update model ID from config
            if creds['model_id']:
                self.model_id = creds['model_id']
            
            logger.info(f"AWS Bedrock client initialized successfully in region {creds['region']} with model {self.model_id}")
        except Exception as e:
            logger.error(f"Error initializing Bedrock client: {str(e)}")
            raise Exception(f"Failed to initialize AWS Bedrock: {str(e)}")
    
    def test_model_connection(self, model_id):
        """Test connection with a specific model ID"""
        try:
            print(f"Testing connection to model: {model_id}")
            
            request_body = json.dumps({
                "anthropic_version": "bedrock-2023-05-31",
                "max_tokens": 50,
                "temperature": 0.1,
                "messages": [{"role": "user", "content": "Hello, please respond with 'Connection successful'"}]
            })

            response = self.client.invoke_model(
                modelId=model_id,
                body=request_body,
                contentType='application/json'
            )

            response_body = json.loads(response['body'].read())
            
            if 'content' in response_body and len(response_body['content']) > 0:
                result = response_body['content'][0]['text']
                print(f"✅ Model {model_id} responded: {result}")
                return True, result
            else:
                print(f"❌ Unexpected response format from {model_id}")
                return False, "Unexpected response format"
                
        except ClientError as e:
            error_code = e.response['Error']['Code']
            error_message = e.response['Error']['Message']
            print(f"❌ AWS Error for {model_id}: {error_code} - {error_message}")
            return False, f"{error_code}: {error_message}"
        except Exception as e:
            print(f"❌ Unexpected error for {model_id}: {str(e)}")
            return False, str(e)

    def test_all_models(self):
        """Test both model IDs mentioned by the user"""
        models_to_test = [
            'anthropic.claude-3-7-sonnet-20250219-v1:0',
            'anthropic.claude-sonnet-4-20250514-v1:0'
        ]
        
        results = {}
        print(f"Testing models in region: {self.region}")
        print("=" * 50)
        
        for model_id in models_to_test:
            success, message = self.test_model_connection(model_id)
            results[model_id] = {'success': success, 'message': message}
            print()
        
        return results

    def invoke_claude(self, prompt, system_prompt=None, max_tokens=4000, temperature=0.7, model_id=None):
        """Invoke Claude model via Bedrock - updated to follow working example pattern"""
        try:
            # Use provided model_id or default
            current_model_id = model_id or self.model_id
            
            # Prepare the request body for Claude (following working example)
            body = {
                "anthropic_version": "bedrock-2023-05-31",
                "max_tokens": max_tokens,
                "temperature": temperature,
                "messages": [
                    {
                        "role": "user",
                        "content": prompt
                    }
                ]
            }
            
            # Add system prompt if provided
            if system_prompt:
                body["system"] = system_prompt
            
            # Invoke the model
            response = self.client.invoke_model(
                modelId=current_model_id,
                body=json.dumps(body),
                contentType='application/json'
            )
            
            # Parse the response
            response_body = json.loads(response['body'].read())
            
            if 'content' in response_body and len(response_body['content']) > 0:
                return response_body['content'][0]['text']
            else:
                raise Exception("Unexpected response format from Claude")
                
        except ClientError as e:
            logger.error(f"AWS Bedrock client error: {str(e)}")
            raise Exception(f"Bedrock API error: {str(e)}")
        except Exception as e:
            logger.error(f"Error invoking Claude: {str(e)}")
            raise Exception(f"Failed to get AI response: {str(e)}")

    def stream_bedrock_response(self, message, model_id=None):
        """Stream responses from AWS Bedrock model - following the working example"""
        current_model_id = model_id or self.model_id

        request_body = json.dumps({
            "anthropic_version": "bedrock-2023-05-31",
            "max_tokens": 1000,
            "temperature": 0.7,
            "messages": [{"role": "user", "content": message}]
        })

        try:
            print(f"Streaming from AWS Bedrock model: {current_model_id}")
            response = self.client.invoke_model_with_response_stream(
                modelId=current_model_id,
                body=request_body
            )

            # Stream and process response
            full_response = ""
            for event in response["body"]:
                event_str = event.get("chunk", {}).get("bytes", "")
                if event_str:
                    chunk = json.loads(event_str)
                    if "delta" in chunk and "text" in chunk["delta"]:
                        text = chunk["delta"]["text"]
                        print(text, end="", flush=True)  # Print the text
                        full_response += text

            print()  # Ensure newline after completion
            return full_response

        except ClientError as e:
            error_msg = f"AWS Error: {e.response['Error']['Code']} - {e.response['Error']['Message']}"
            print(error_msg)
            raise Exception(error_msg)
        except Exception as e:
            error_msg = f"Unexpected AWS error: {str(e)}"
            print(error_msg)
            raise Exception(error_msg)

    def enhance_prompt(self, user_prompt, task_type='development'):
        """Enhance a user prompt using Claude"""
        system_prompt = """You are an expert at creating effective prompts for AI coding assistants. 
Your job is to take a user's basic prompt and enhance it to be more specific, actionable, and likely to produce better results.

Guidelines for enhancement:
1. Make the prompt more specific and detailed
2. Add context about best practices for the task type
3. Include relevant technical considerations
4. Structure the prompt clearly with sections if needed
5. Preserve the user's original intent and requirements
6. Add clarifying questions or considerations the AI should address

Task types and their considerations:
- development: Focus on code quality, architecture, testing, documentation
- refactoring: Emphasize maintainability, performance, code organization
- testing: Include test coverage, edge cases, different testing strategies
- debugging: Add systematic debugging approaches, logging, error handling

Return only the enhanced prompt, nothing else."""

        enhancement_prompt = f"""Task Type: {task_type}

Original User Prompt:
{user_prompt}

Please enhance this prompt to be more effective for an AI coding assistant."""

        try:
            enhanced = self.invoke_claude(
                prompt=enhancement_prompt,
                system_prompt=system_prompt,
                max_tokens=2000,
                temperature=0.3
            )
            return enhanced.strip()
        except Exception as e:
            logger.error(f"Error enhancing prompt: {str(e)}")
            # Return original prompt if enhancement fails
            return user_prompt
    
    def analyze_task_type(self, prompt):
        """Analyze a prompt to determine the most appropriate task type"""
        system_prompt = """Analyze the given coding prompt and categorize it into one of these task types:
- development: Creating new features, applications, or components
- refactoring: Improving existing code structure, performance, or maintainability  
- testing: Writing tests, debugging, or troubleshooting issues

Return only the task type (development, refactoring, or testing), nothing else."""

        analysis_prompt = f"""Prompt to analyze:
{prompt}

What task type is this?"""

        try:
            result = self.invoke_claude(
                prompt=analysis_prompt,
                system_prompt=system_prompt,
                max_tokens=50,
                temperature=0.1
            )
            
            task_type = result.strip().lower()
            if task_type in ['development', 'refactoring', 'testing']:
                return task_type
            else:
                return 'development'  # Default fallback
                
        except Exception as e:
            logger.error(f"Error analyzing task type: {str(e)}")
            return 'development'  # Default fallback
    
    def extract_relevant_requirements(self, prompt, all_requirements, task_type):
        """Extract requirements relevant to the specific prompt"""
        system_prompt = f"""You are analyzing a coding prompt to determine which non-functional requirements are most relevant.

Given a prompt and a list of available requirements for {task_type} tasks, select only the requirements that are directly relevant to the prompt.

Return a JSON array containing only the requirement text that applies to this specific prompt. Be selective - only include requirements that are actually relevant to what the user is asking for.

Example response format:
["requirement 1", "requirement 2", "requirement 3"]"""

        requirements_text = "\n".join([f"- {req}" for req in all_requirements])
        
        extraction_prompt = f"""Task Type: {task_type}

User Prompt:
{prompt}

Available Requirements:
{requirements_text}

Which requirements are relevant to this specific prompt?"""

        try:
            result = self.invoke_claude(
                prompt=extraction_prompt,
                system_prompt=system_prompt,
                max_tokens=1000,
                temperature=0.2
            )
            
            # Try to parse as JSON
            import json
            relevant_requirements = json.loads(result.strip())
            
            if isinstance(relevant_requirements, list):
                return relevant_requirements
            else:
                return all_requirements  # Fallback to all requirements
                
        except Exception as e:
            logger.error(f"Error extracting relevant requirements: {str(e)}")
            return all_requirements  # Fallback to all requirements
    
    def test_connection(self):
        """Test the Bedrock connection"""
        try:
            test_prompt = "Hello, please respond with 'Connection successful' if you can read this."
            response = self.invoke_claude(test_prompt, max_tokens=50, temperature=0)
            return "successful" in response.lower()
        except Exception as e:
            logger.error(f"Bedrock connection test failed: {str(e)}")
            return False 