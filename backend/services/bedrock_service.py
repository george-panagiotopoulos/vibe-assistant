import boto3
import json
import logging
import os
from typing import Dict, Any, Optional, Generator
from botocore.exceptions import ClientError, NoCredentialsError
from config.env_loader import env_loader

logger = logging.getLogger(__name__)

class BedrockService:
    """
    Service for interacting with AWS Bedrock Claude models with streaming support.
    """
    
    def __init__(self):
        self.client = None
        self.model_id = os.getenv('AWS_BEDROCK_MODEL_ID', 'anthropic.claude-3-5-sonnet-20240620-v1:0')
        self._initialize_client()
    
    def _initialize_client(self):
        """Initialize the Bedrock client with AWS credentials."""
        try:
            # Get AWS credentials from environment
            aws_access_key_id = os.getenv('AWS_ACCESS_KEY_ID')
            aws_secret_access_key = os.getenv('AWS_SECRET_ACCESS_KEY')
            aws_region = os.getenv('AWS_DEFAULT_REGION', 'us-east-1')
            
            if not aws_access_key_id or not aws_secret_access_key:
                logger.error("AWS credentials not found in environment variables")
                return
            
            # Initialize Bedrock client
            self.client = boto3.client(
                'bedrock-runtime',
                aws_access_key_id=aws_access_key_id,
                aws_secret_access_key=aws_secret_access_key,
                region_name=aws_region
            )
            
            logger.info("Bedrock client initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize Bedrock client: {str(e)}")
            self.client = None
    
    def test_connection(self) -> bool:
        """Test the Bedrock connection with a simple request."""
        try:
            if not self.client:
                logger.error("Bedrock client not initialized")
                return False
            
            # Simple test request
            request_body = {
                "anthropic_version": "bedrock-2023-05-31",
                "max_tokens": 100,
                "temperature": 0.1,
                "messages": [
                    {
                        "role": "user",
                        "content": "Respond with 'Connection successful' if you can read this."
                    }
                ]
            }
            
            response = self.client.invoke_model(
                modelId=self.model_id,
                body=json.dumps(request_body),
                contentType='application/json'
            )
            
            response_body = json.loads(response['body'].read())
            content = response_body.get('content', [])
            
            if content and len(content) > 0:
                text_response = content[0].get('text', '')
                logger.info(f"Bedrock test response: {text_response}")
                return "Connection successful" in text_response
            
            return False
            
        except Exception as e:
            logger.error(f"Bedrock connection test failed: {str(e)}")
            return False
    
    def invoke_claude_streaming(
        self, 
        prompt: str, 
        system_prompt: str = None,
        max_tokens: int = 4000,
        temperature: float = 0.3
    ) -> Generator[str, None, None]:
        """
        Invoke Claude model with streaming response.
        
        Args:
            prompt: The user prompt
            system_prompt: Optional system prompt
            max_tokens: Maximum tokens to generate
            temperature: Temperature for response generation
            
        Yields:
            Streaming response chunks
        """
        try:
            if not self.client:
                raise Exception("Bedrock client not initialized")
            
            # Build request body
            request_body = {
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
                request_body["system"] = system_prompt
            
            # Invoke with streaming
            response = self.client.invoke_model_with_response_stream(
                modelId=self.model_id,
                body=json.dumps(request_body),
                contentType='application/json'
            )
            
            # Process streaming response
            for event in response["body"]:
                chunk = event.get("chunk")
                if chunk:
                    chunk_data = json.loads(chunk.get("bytes").decode())
                    
                    # Handle different chunk types
                    if chunk_data.get("type") == "content_block_delta":
                        delta = chunk_data.get("delta", {})
                        if "text" in delta:
                            yield delta["text"]
                    elif chunk_data.get("type") == "message_delta":
                        # Handle message completion
                        pass
                        
        except Exception as e:
            logger.error(f"Error in streaming Claude model: {str(e)}")
            raise
    
    def invoke_claude(
        self, 
        prompt: str, 
        system_prompt: str = None,
        max_tokens: int = 4000,
        temperature: float = 0.3,
        model_id: str = None
    ) -> str:
        """
        Invoke Claude model with the given prompt (non-streaming).
        
        Args:
            prompt: The user prompt
            system_prompt: Optional system prompt
            max_tokens: Maximum tokens to generate
            temperature: Temperature for response generation
            model_id: Optional model ID override
            
        Returns:
            The model's response text
        """
        try:
            if not self.client:
                raise Exception("Bedrock client not initialized")
            
            # Use provided model_id or default
            model_to_use = model_id or self.model_id
            
            # Build request body
            request_body = {
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
                request_body["system"] = system_prompt
            
            # Invoke the model
            response = self.client.invoke_model(
                modelId=model_to_use,
                body=json.dumps(request_body),
                contentType='application/json'
            )
            
            # Parse response
            response_body = json.loads(response['body'].read())
            content = response_body.get('content', [])
            
            if content and len(content) > 0:
                return content[0].get('text', '')
            else:
                raise Exception("No content in response")
                
        except Exception as e:
            logger.error(f"Error invoking Claude model: {str(e)}")
            raise

    def extract_relevant_requirements(self, prompt, all_requirements, task_type):
        """Extract relevant NFRs using LLM - no more mocks"""
        try:
            if not all_requirements:
                return []
            
            # Use LLM to select relevant requirements
            selection_prompt = f"""Given this user request: "{prompt}"
            
And these available non-functional requirements for {task_type}:
{chr(10).join(f"{i+1}. {req}" for i, req in enumerate(all_requirements))}

Select the 3-5 most relevant requirements that apply to this specific request. 
Respond with only the numbers (e.g., "1, 3, 5") of the relevant requirements."""

            response = self.invoke_claude(
                prompt=selection_prompt,
                max_tokens=100,
                temperature=0.1
            )
            
            # Parse the response to extract requirement indices
            import re
            numbers = re.findall(r'\d+', response)
            selected_indices = [int(n) - 1 for n in numbers if int(n) <= len(all_requirements)]
            
            # Return selected requirements
            return [all_requirements[i] for i in selected_indices if 0 <= i < len(all_requirements)]
            
        except Exception as e:
            logger.warning(f"Failed to extract relevant requirements: {str(e)}")
            # Fallback to first 3 requirements
            return all_requirements[:3] 