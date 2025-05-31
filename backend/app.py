from flask import Flask, request, jsonify
from flask_cors import CORS
import os
from dotenv import load_dotenv
import logging
import json

# Load environment variables first
load_dotenv()

from config.settings import Config
from services.github_service import GitHubService
from services.bedrock_service import BedrockService
from services.prompt_service import PromptService
from services.config_service import ConfigService

# Initialize Flask app
app = Flask(__name__)
app.config.from_object(Config)
CORS(app)

# Initialize services
config_service = ConfigService()
github_service = GitHubService()
bedrock_service = BedrockService()
prompt_service = PromptService(bedrock_service)

# Configure logging
log_level = os.environ.get('LOG_LEVEL', 'INFO')
logging.basicConfig(level=getattr(logging, log_level))
logger = logging.getLogger(__name__)

@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({"status": "healthy", "service": "vibe-assistant"})

@app.route('/api/config', methods=['GET', 'POST'])
def handle_config():
    """Get or update application configuration"""
    if request.method == 'GET':
        try:
            config = config_service.get_config()
            return jsonify({"success": True, "config": config})
        except Exception as e:
            logger.error(f"Error getting config: {str(e)}")
            return jsonify({"success": False, "error": str(e)}), 500
    
    elif request.method == 'POST':
        try:
            config_data = request.json
            updated_config = config_service.update_config(config_data)
            return jsonify({"success": True, "config": updated_config})
        except Exception as e:
            logger.error(f"Error updating config: {str(e)}")
            return jsonify({"success": False, "error": str(e)}), 500

@app.route('/api/repositories/files', methods=['POST'])
def get_repository_files():
    """Get file tree for a GitHub repository"""
    try:
        data = request.json
        repo_url = data.get('repo_url')
        github_token = data.get('github_token') or os.environ.get('GITHUB_TOKEN')
        
        if not repo_url:
            return jsonify({"success": False, "error": "Repository URL is required"}), 400
        
        github_service.set_token(github_token)
        file_tree = github_service.get_repository_files(repo_url)
        
        return jsonify({"success": True, "files": file_tree})
    except Exception as e:
        logger.error(f"Error getting repository files: {str(e)}")
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/api/repositories/file-content', methods=['POST'])
def get_file_content():
    """Get content of a specific file from repository"""
    try:
        data = request.json
        repo_url = data.get('repo_url')
        file_path = data.get('file_path')
        github_token = data.get('github_token') or os.environ.get('GITHUB_TOKEN')
        
        if not repo_url or not file_path:
            return jsonify({"success": False, "error": "Repository URL and file path are required"}), 400
        
        content = github_service.get_file_content(repo_url, file_path, github_token)
        
        return jsonify({"success": True, "content": content})
    except Exception as e:
        logger.error(f"Error getting file content: {str(e)}")
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/api/requirements', methods=['GET', 'POST'])
def handle_requirements():
    """Get or update non-functional requirements"""
    if request.method == 'GET':
        try:
            config = config_service.get_config()
            requirements = config.get('non_functional_requirements', {})
            return jsonify({"success": True, "requirements": requirements})
        except Exception as e:
            logger.error(f"Error getting requirements: {str(e)}")
            return jsonify({"success": False, "error": str(e)}), 500
    
    elif request.method == 'POST':
        try:
            data = request.json
            task_type = data.get('task_type')
            requirements = data.get('requirements')
            
            if not task_type or requirements is None:
                return jsonify({"success": False, "error": "Task type and requirements are required"}), 400
            
            updated_requirements = config_service.update_requirements(task_type, requirements)
            return jsonify({"success": True, "requirements": updated_requirements})
        except Exception as e:
            logger.error(f"Error updating requirements: {str(e)}")
            return jsonify({"success": False, "error": str(e)}), 500

@app.route('/api/bedrock/test', methods=['POST'])
def test_bedrock_connection():
    try:
        data = request.get_json()
        # Use provided credentials or fall back to environment variables
        aws_access_key_id = data.get('aws_access_key_id') or os.environ.get('AWS_ACCESS_KEY_ID')
        aws_secret_access_key = data.get('aws_secret_access_key') or os.environ.get('AWS_SECRET_ACCESS_KEY')
        aws_region = data.get('aws_region') or os.environ.get('AWS_DEFAULT_REGION', 'us-east-1')
        model_id = data.get('model_id') or os.environ.get('AWS_BEDROCK_MODEL_ID', 'anthropic.claude-sonnet-4-20250514-v1:0')

        if not all([aws_access_key_id, aws_secret_access_key, model_id]):
            return jsonify({
                'connected': False,
                'error': 'Missing required AWS credentials or model ID'
            }), 400

        # Test connection to Bedrock
        import boto3
        from botocore.exceptions import ClientError, NoCredentialsError

        try:
            # Create a Bedrock client
            bedrock = boto3.client(
                'bedrock-runtime',
                aws_access_key_id=aws_access_key_id,
                aws_secret_access_key=aws_secret_access_key,
                region_name=aws_region
            )

            # Test with a simple request
            response = bedrock.invoke_model(
                modelId=model_id,
                body=json.dumps({
                    "anthropic_version": "bedrock-2023-05-31",
                    "max_tokens": 10,
                    "messages": [
                        {
                            "role": "user",
                            "content": "Hello"
                        }
                    ]
                }),
                contentType='application/json'
            )

            return jsonify({
                'connected': True,
                'message': 'Successfully connected to AWS Bedrock'
            })

        except ClientError as e:
            error_code = e.response['Error']['Code']
            if error_code == 'UnauthorizedOperation':
                error_msg = 'Invalid AWS credentials'
            elif error_code == 'ValidationException':
                error_msg = 'Invalid model ID or request format'
            else:
                error_msg = f'AWS Error: {e.response["Error"]["Message"]}'
            
            return jsonify({
                'connected': False,
                'error': error_msg
            }), 401

        except NoCredentialsError:
            return jsonify({
                'connected': False,
                'error': 'AWS credentials not found'
            }), 401

    except Exception as e:
        logger.error(f"Bedrock connection test failed: {str(e)}")
        return jsonify({
            'connected': False,
            'error': str(e)
        }), 500

@app.route('/api/bedrock/chat', methods=['POST'])
def chat_with_ai():
    try:
        data = request.get_json()
        message = data.get('message', '')
        current_prompt = data.get('current_prompt', '')
        selected_files = data.get('selected_files', [])
        config_data = data.get('config', {})

        # Use provided credentials or fall back to environment variables
        aws_access_key_id = config_data.get('aws_access_key_id') or os.environ.get('AWS_ACCESS_KEY_ID')
        aws_secret_access_key = config_data.get('aws_secret_access_key') or os.environ.get('AWS_SECRET_ACCESS_KEY')
        aws_region = config_data.get('aws_region') or os.environ.get('AWS_DEFAULT_REGION', 'us-east-1')
        model_id = config_data.get('model_id') or os.environ.get('AWS_BEDROCK_MODEL_ID', 'anthropic.claude-sonnet-4-20250514-v1:0')

        if not all([aws_access_key_id, aws_secret_access_key, model_id]):
            return jsonify({
                'error': 'Missing required AWS credentials or model ID'
            }), 400

        import boto3
        from botocore.exceptions import ClientError

        # Create Bedrock client
        bedrock = boto3.client(
            'bedrock-runtime',
            aws_access_key_id=aws_access_key_id,
            aws_secret_access_key=aws_secret_access_key,
            region_name=aws_region
        )

        # Build context from selected files
        file_context = ""
        if selected_files:
            file_context = "\n\nSelected files context:\n"
            for file in selected_files[:5]:  # Limit to 5 files to avoid token limits
                file_context += f"- {file['path']} ({file['type']})\n"

        # Build the system prompt
        system_prompt = f"""You are an AI assistant helping with prompt engineering and code analysis.

Current prompt being worked on:
{current_prompt}

{file_context}

Please provide helpful, concise responses to assist with prompt improvement and code understanding."""

        # Prepare the request
        request_body = {
            "anthropic_version": "bedrock-2023-05-31",
            "max_tokens": 1000,
            "system": system_prompt,
            "messages": [
                {
                    "role": "user",
                    "content": message
                }
            ]
        }

        try:
            response = bedrock.invoke_model(
                modelId=model_id,
                body=json.dumps(request_body),
                contentType='application/json'
            )

            response_body = json.loads(response['body'].read())
            ai_response = response_body.get('content', [{}])[0].get('text', 'No response generated')

            return jsonify({
                'response': ai_response,
                'success': True
            })

        except ClientError as e:
            return jsonify({
                'error': f'AWS Bedrock error: {str(e)}',
                'success': False
            }), 500

    except Exception as e:
        logger.error(f"AI chat failed: {str(e)}")
        return jsonify({
            'error': str(e),
            'success': False
        }), 500

# New prompt builder endpoints
@app.route('/api/prompt/build', methods=['POST'])
def build_prompt():
    try:
        data = request.get_json()
        prompt = data.get('prompt', '')
        task_type = data.get('task_type', 'development')
        selected_files = data.get('selected_files', [])
        include_context = data.get('include_context', True)
        include_requirements = data.get('include_requirements', True)
        
        # Load non-functional requirements from user config instead of requirements.txt
        requirements_list = []
        if include_requirements:
            try:
                config = config_service.get_config()
                nfr = config.get('non_functional_requirements', {})
                requirements_list = nfr.get(task_type, [])
            except Exception as e:
                logger.warning(f"Could not load non-functional requirements: {str(e)}")
        
        # Build context from selected files
        context_text = ""
        if include_context and selected_files:
            context_parts = []
            max_file_size = int(os.environ.get('MAX_FILE_SIZE_KB', '100')) * 1024
            
            for file_info in selected_files:
                try:
                    file_path = file_info.get('path', '')
                    if os.path.exists(file_path):
                        file_size = os.path.getsize(file_path)
                        if file_size <= max_file_size:
                            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                                content = f.read()
                                context_parts.append(f"File: {file_path}\n{content}\n")
                except Exception:
                    continue  # Skip files that can't be read
            context_text = "\n".join(context_parts)
        
        # Build final prompt
        final_prompt_parts = []
        
        # Add task type context
        task_contexts = {
            'development': 'You are a senior software developer. Focus on writing clean, maintainable, and efficient code.',
            'refactoring': 'You are a code refactoring expert. Focus on improving code structure, readability, and performance.',
            'testing': 'You are a testing specialist. Focus on comprehensive test coverage and quality assurance.',
            'documentation': 'You are a technical writer. Focus on clear, comprehensive documentation.',
            'review': 'You are a code reviewer. Focus on identifying issues, improvements, and best practices.'
        }
        
        if task_type in task_contexts:
            final_prompt_parts.append(task_contexts[task_type])
        
        # Add user prompt
        final_prompt_parts.append(f"Task: {prompt}")
        
        # Add non-functional requirements if available
        if requirements_list:
            requirements_text = f"Non-functional requirements for {task_type}:\n"
            requirements_text += "\n".join(f"- {req}" for req in requirements_list)
            final_prompt_parts.append(requirements_text)
        
        # Add file context if available
        if context_text:
            final_prompt_parts.append(f"Context from selected files:\n{context_text}")
        
        final_prompt = "\n\n".join(final_prompt_parts)
        
        return jsonify({
            'success': True,
            'final_prompt': final_prompt,
            'context_included': include_context and bool(context_text),
            'requirements_included': include_requirements and bool(requirements_list),
            'files_processed': len(selected_files) if include_context else 0,
            'requirements_applied': len(requirements_list)
        })
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/prompt/enhance', methods=['POST'])
def enhance_prompt():
    try:
        data = request.get_json()
        prompt = data.get('prompt', '')
        task_type = data.get('task_type', 'development')
        selected_files = data.get('selected_files', [])
        
        # Get user configuration for non-functional requirements
        config = config_service.get_config()
        requirements = config.get('non_functional_requirements', {}).get(task_type, [])
        
        # Initialize Bedrock service (it will load credentials from user config automatically)
        try:
            bedrock_service_instance = BedrockService()
            
            # Use AI to enhance the prompt with Claude
            enhanced_prompt = bedrock_service_instance.enhance_prompt(prompt, task_type)
            
            # Use AI to filter and add only relevant non-functional requirements
            relevant_requirements = []
            if requirements:
                relevant_requirements = bedrock_service_instance.extract_relevant_requirements(
                    prompt, requirements, task_type
                )
                
                if relevant_requirements:
                    enhanced_prompt += f"\n\nNon-functional requirements for {task_type}:\n"
                    enhanced_prompt += "\n".join(f"- {req}" for req in relevant_requirements)
            
            # Add file context if files are selected
            if selected_files:
                enhanced_prompt += f"\n\nContext: This request relates to {len(selected_files)} selected file(s). Please consider the file structure and content when providing your response."
            
            return jsonify({
                'success': True,
                'enhanced_prompt': enhanced_prompt,
                'original_prompt': prompt,
                'task_type': task_type,
                'requirements_applied': len(relevant_requirements),
                'ai_enhanced': True
            })
            
        except Exception as bedrock_error:
            logger.warning(f"Bedrock enhancement failed, using fallback: {str(bedrock_error)}")
            
            # Fallback to basic enhancement if Bedrock fails
            enhanced_prompt = prompt
            
            # Add basic task-specific guidance
            task_guidance = {
                'development': [
                    "Consider error handling and edge cases",
                    "Follow coding best practices and design patterns",
                    "Include appropriate comments and documentation",
                    "Consider performance and scalability"
                ],
                'refactoring': [
                    "Identify code smells and anti-patterns",
                    "Improve code organization and modularity", 
                    "Enhance readability and maintainability",
                    "Optimize performance where possible"
                ],
                'testing': [
                    "Create comprehensive test cases including edge cases",
                    "Follow testing best practices (AAA pattern, etc.)",
                    "Include both unit and integration tests",
                    "Consider test coverage and quality metrics"
                ]
            }
            
            if task_type in task_guidance:
                enhanced_prompt += "\n\nAdditional considerations:\n"
                enhanced_prompt += "\n".join(f"- {guidance}" for guidance in task_guidance[task_type])
            
            # Add non-functional requirements from config (limit to most relevant)
            if requirements:
                enhanced_prompt += f"\n\nNon-functional requirements for {task_type}:\n"
                enhanced_prompt += "\n".join(f"- {req}" for req in requirements[:5])  # Limit to first 5
            
            return jsonify({
                'success': True,
                'enhanced_prompt': enhanced_prompt,
                'original_prompt': prompt,
                'task_type': task_type,
                'requirements_applied': min(len(requirements), 5) if requirements else 0,
                'ai_enhanced': False,
                'fallback_used': True
            })
        
    except Exception as e:
        logger.error(f"Error enhancing prompt: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500

# User configuration endpoints
@app.route('/api/user/config', methods=['GET'])
def get_user_config():
    try:
        config_path = os.path.join(os.path.dirname(__file__), 'config', 'user_config.json')
        if os.path.exists(config_path):
            with open(config_path, 'r') as f:
                config = json.load(f)
        else:
            config = {
                'aws': {
                    'access_key_id': '',
                    'secret_access_key': '',
                    'region': os.environ.get('AWS_DEFAULT_REGION', 'us-east-1')
                },
                'github': {
                    'token': '',
                    'default_repo': ''
                },
                'preferences': {
                    'default_task_type': os.environ.get('DEFAULT_TASK_TYPE', 'development'),
                    'include_context_by_default': True,
                    'include_requirements_by_default': True
                }
            }
        
        return jsonify({'success': True, 'config': config})
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/user/config', methods=['POST'])
def update_user_config():
    try:
        data = request.get_json()
        config_path = os.path.join(os.path.dirname(__file__), 'config', 'user_config.json')
        
        with open(config_path, 'w') as f:
            json.dump(data, f, indent=2)
        
        return jsonify({'success': True, 'message': 'Configuration updated successfully'})
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

# Repository analysis endpoint
@app.route('/api/repository/analyze', methods=['GET'])
def analyze_repository():
    try:
        repo_path = request.args.get('repo_path', '')
        if not repo_path or not os.path.exists(repo_path):
            return jsonify({'success': False, 'error': 'Invalid repository path'}), 400
        
        analysis = {
            'total_files': 0,
            'total_size': 0,
            'file_types': {},
            'languages': {},
            'structure': {}
        }
        
        for root, dirs, files in os.walk(repo_path):
            for file in files:
                file_path = os.path.join(root, file)
                try:
                    file_size = os.path.getsize(file_path)
                    analysis['total_files'] += 1
                    analysis['total_size'] += file_size
                    
                    # Count file extensions
                    ext = os.path.splitext(file)[1].lower()
                    if ext:
                        analysis['file_types'][ext] = analysis['file_types'].get(ext, 0) + 1
                    
                    # Basic language detection
                    language_map = {
                        '.py': 'Python',
                        '.js': 'JavaScript',
                        '.jsx': 'React',
                        '.ts': 'TypeScript',
                        '.tsx': 'React TypeScript',
                        '.java': 'Java',
                        '.cpp': 'C++',
                        '.c': 'C',
                        '.html': 'HTML',
                        '.css': 'CSS',
                        '.json': 'JSON'
                    }
                    
                    if ext in language_map:
                        lang = language_map[ext]
                        analysis['languages'][lang] = analysis['languages'].get(lang, 0) + 1
                        
                except Exception:
                    continue
        
        return jsonify({'success': True, 'analysis': analysis})
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/github/test', methods=['POST'])
def test_github_connection():
    try:
        data = request.get_json()
        github_token = data.get('github_token') or data.get('token')
        test_repo = data.get('test_repo')
        
        # Get default repo from config if not provided
        if not test_repo:
            config = config_service.get_config()
            test_repo = config.get('github', {}).get('default_repo')
        
        if not test_repo:
            return jsonify({
                'connected': False,
                'error': 'No repository specified for testing'
            }), 400
        
        # Test GitHub connection
        github_service.set_token(github_token)
        
        try:
            # Try to get basic repository access first
            owner, repo_name = github_service.parse_repo_url(test_repo)
            repo = github_service.github.get_repo(f"{owner}/{repo_name}")
            
            # Basic info that should always be available
            basic_info = {
                'name': repo.name,
                'full_name': repo.full_name,
                'private': repo.private,
                'default_branch': repo.default_branch
            }
            
            return jsonify({
                'connected': True,
                'message': f'Successfully connected to {basic_info["full_name"]}',
                'repository': basic_info
            })
            
        except Exception as github_error:
            error_msg = str(github_error)
            if '404' in error_msg:
                error_msg = 'Repository not found or access denied'
            elif '401' in error_msg or 'Bad credentials' in error_msg:
                error_msg = 'Invalid GitHub token or insufficient permissions'
            elif '403' in error_msg:
                error_msg = 'Rate limit exceeded or access forbidden'
            
            return jsonify({
                'connected': False,
                'error': error_msg
            }), 401
        
    except Exception as e:
        logger.error(f"GitHub connection test failed: {str(e)}")
        return jsonify({
            'connected': False,
            'error': str(e)
        }), 500

@app.errorhandler(404)
def not_found(error):
    return jsonify({"success": False, "error": "Endpoint not found"}), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({"success": False, "error": "Internal server error"}), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    host = os.environ.get('HOST', '0.0.0.0')
    debug = os.environ.get('FLASK_DEBUG', 'True').lower() == 'true'
    
    app.run(debug=debug, host=host, port=port) 