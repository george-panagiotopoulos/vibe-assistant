from flask import Flask, request, jsonify, Response
from flask_cors import CORS
import os
import logging
import json
from datetime import datetime

# RADICAL FIX: Force environment loading FIRST
from config.env_loader import env_loader
env_loader.ensure_loaded()

from config.settings import Config
from services.github_service import GitHubService
from services.bedrock_service import BedrockService
from services.prompt_service import PromptService
from services.config_service import ConfigService
from services.prompt_constructor import PromptConstructor
from services.logging_service import logging_service

# Configure logging EARLY
log_level = env_loader.get_env('LOG_LEVEL', 'INFO')
logging.basicConfig(
    level=getattr(logging, log_level),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# FORCE LOG ENVIRONMENT STATUS AT STARTUP
logger.info("🚀 STARTING VIBE ASSISTANT")
env_loader.log_environment_status()

# Initialize Flask app
app = Flask(__name__)
app.config.from_object(Config)
CORS(app)

# RADICAL FIX: Initialize services with explicit environment checking
logger.info("🔧 Initializing services...")

try:
    config_service = ConfigService()
    logger.info("✅ ConfigService initialized")
except Exception as e:
    logger.error(f"❌ ConfigService failed: {e}")
    raise

try:
    github_service = GitHubService()
    logger.info("✅ GitHubService initialized")
except Exception as e:
    logger.error(f"❌ GitHubService failed: {e}")
    raise

try:
    bedrock_service = BedrockService()
    logger.info("✅ BedrockService initialized")
except Exception as e:
    logger.error(f"❌ BedrockService failed: {e}")
    raise

try:
    prompt_service = PromptService(bedrock_service)
    logger.info("✅ PromptService initialized")
except Exception as e:
    logger.error(f"❌ PromptService failed: {e}")
    raise

try:
    prompt_constructor = PromptConstructor(bedrock_service, config_service)
    logger.info("✅ PromptConstructor initialized")
except Exception as e:
    logger.error(f"❌ PromptConstructor failed: {e}")
    raise

# FORCE CHECK CONFIGURATION AT STARTUP
try:
    startup_config = config_service.get_config()
    logger.info("🔍 STARTUP CONFIGURATION CHECK:")
    logger.info(f"GitHub repo: {startup_config.get('github', {}).get('default_repo', 'NOT SET')}")
    logger.info(f"AWS region: {startup_config.get('aws', {}).get('region', 'NOT SET')}")
    logger.info(f"AWS key set: {bool(startup_config.get('aws', {}).get('access_key_id'))}")
    logger.info(f"GitHub token set: {bool(startup_config.get('github', {}).get('token'))}")
except Exception as e:
    logger.error(f"❌ Startup configuration check failed: {e}")

logger.info("🎯 All services initialized successfully!")

@app.before_request
def before_request():
    """Ensure environment is loaded before each request"""
    env_loader.ensure_loaded()

@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint with environment status"""
    env_status = {
        'aws_configured': bool(env_loader.get_env('AWS_ACCESS_KEY_ID')),
        'github_configured': bool(env_loader.get_env('GITHUB_TOKEN')),
        'github_repo_set': bool(env_loader.get_env('GITHUB_DEFAULT_REPO'))
    }
    return jsonify({
        "status": "healthy", 
        "service": "vibe-assistant",
        "environment": env_status
    })

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
            data = request.get_json()
            task_type = data.get('task_type')
            requirements = data.get('requirements', [])
            
            if not task_type:
                return jsonify({"success": False, "error": "Task type is required"}), 400
            
            # Update requirements using config service
            updated_requirements = config_service.update_requirements(task_type, requirements)
            
            return jsonify({"success": True, "requirements": updated_requirements})
        except Exception as e:
            logger.error(f"Error updating requirements: {str(e)}")
            return jsonify({"success": False, "error": str(e)}), 500

@app.route('/api/enhance-prompt', methods=['POST'])
def enhance_prompt():
    """Enhanced prompt endpoint with real Bedrock integration"""
    try:
        data = request.get_json()
        
        if not data or 'prompt' not in data:
            return jsonify({'error': 'Prompt is required'}), 400
        
        user_prompt = data['prompt']
        task_type = data.get('task_type', 'development')
        selected_files = data.get('selected_files', [])
        
        logger.info(f"Processing enhance-prompt request: {user_prompt[:100]}...")
        
        # Log the API request
        logging_service.log_api_request(
            endpoint='/api/enhance-prompt',
            request_data={
                'prompt': user_prompt,
                'task_type': task_type,
                'selected_files_count': len(selected_files)
            }
        )
        
        # Get configuration and NFRs
        config = config_service.get_config()
        all_nfrs = config.get('non_functional_requirements', {}).get(task_type, [])
        
        # Initialize services
        bedrock_service = BedrockService()
        prompt_constructor = PromptConstructor(bedrock_service=bedrock_service, config_service=config_service)
        
        # Test Bedrock connection first
        if not bedrock_service.test_connection():
            error_msg = "Bedrock connection test failed"
            logger.error(error_msg)
            logging_service.log_error("bedrock_connection", error_msg)
            return jsonify({'error': 'AI service temporarily unavailable'}), 503
        
        # Construct the enhanced prompt
        constructed_prompt = prompt_constructor.construct_enhanced_prompt(
            user_input=user_prompt,
            nfr_requirements=all_nfrs,
            task_type=task_type,
            file_context=selected_files,
            config=config
        )
        
        # Get enhanced specification from LLM
        enhanced_result = prompt_constructor.enhance_with_llm(constructed_prompt)
        
        logger.info(f"Successfully enhanced prompt for task_type: {task_type}")
        
        # Log successful response
        logging_service.log_api_request(
            endpoint='/api/enhance-prompt',
            request_data={
                'prompt': user_prompt,
                'task_type': task_type,
                'selected_files_count': len(selected_files)
            },
            response_data={
                'success': True,
                'enhanced_length': len(enhanced_result['enhanced_specification'])
            }
        )
        
        return jsonify({
            'enhanced_specification': enhanced_result['enhanced_specification'],
            'original_input': enhanced_result['original_input'],
            'task_type': enhanced_result['task_type'],
            'metadata': enhanced_result['metadata']
        })
        
    except Exception as e:
        error_msg = f"Error in enhance-prompt endpoint: {str(e)}"
        logger.error(error_msg)
        logging_service.log_error("enhance_prompt", error_msg, {'prompt': user_prompt[:100] if 'user_prompt' in locals() else 'unknown'})
        return jsonify({'error': f'Failed to enhance prompt: {str(e)}'}), 500

@app.route('/api/stream-response', methods=['POST'])
def stream_response():
    """Stream responses from AWS Bedrock"""
    try:
        data = request.get_json()
        
        if not data or 'prompt' not in data:
            return jsonify({'error': 'Prompt is required'}), 400
        
        user_prompt = data['prompt']
        system_prompt = data.get('system_prompt', None)
        max_tokens = data.get('max_tokens', 4000)
        temperature = data.get('temperature', 0.3)
        
        logger.info(f"Processing streaming request: {user_prompt[:100]}...")
        
        # Log the streaming request
        logging_service.log_api_request(
            endpoint='/api/stream-response',
            request_data={
                'prompt': user_prompt,
                'max_tokens': max_tokens,
                'temperature': temperature
            }
        )
        
        # Initialize Bedrock service
        bedrock_service = BedrockService()
        
        # Test connection first
        if not bedrock_service.test_connection():
            error_msg = "Bedrock connection test failed"
            logger.error(error_msg)
            logging_service.log_error("bedrock_connection", error_msg)
            return jsonify({'error': 'AI service temporarily unavailable'}), 503
        
        # Collect chunks for logging
        response_chunks = []
        
        def generate():
            try:
                for chunk in bedrock_service.invoke_claude_streaming(
                    prompt=user_prompt,
                    system_prompt=system_prompt,
                    max_tokens=max_tokens,
                    temperature=temperature
                ):
                    # Collect chunk for logging
                    response_chunks.append(chunk)
                    
                    # Send each chunk as Server-Sent Events
                    yield f"data: {json.dumps({'chunk': chunk})}\n\n"
                
                # Log the complete streaming response
                logging_service.log_streaming_response(
                    prompt=user_prompt,
                    response_chunks=response_chunks,
                    metadata={
                        'max_tokens': max_tokens,
                        'temperature': temperature,
                        'system_prompt': system_prompt is not None
                    }
                )
                
                # Send completion signal
                yield f"data: {json.dumps({'done': True})}\n\n"
                
            except Exception as e:
                error_msg = f"Error in streaming: {str(e)}"
                logger.error(error_msg)
                logging_service.log_error("streaming", error_msg, {'prompt': user_prompt[:100]})
                yield f"data: {json.dumps({'error': str(e)})}\n\n"
        
        return Response(
            generate(),
            mimetype='text/plain',
            headers={
                'Cache-Control': 'no-cache',
                'Connection': 'keep-alive',
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Headers': 'Content-Type'
            }
        )
        
    except Exception as e:
        error_msg = f"Error in stream-response endpoint: {str(e)}"
        logger.error(error_msg)
        logging_service.log_error("stream_response", error_msg)
        return jsonify({'error': f'Failed to stream response: {str(e)}'}), 500

@app.route('/api/generate-specification', methods=['POST'])
def generate_specification():
    """Generate detailed technical specification from enhanced prompt"""
    try:
        data = request.get_json()
        
        if not data or 'enhanced_prompt' not in data:
            return jsonify({
                'success': False,
                'error': 'Enhanced prompt is required'
            }), 400
        
        enhanced_prompt = data['enhanced_prompt']
        nfr_requirements = data.get('nfr_requirements', [])
        file_context = data.get('file_context', '')
        
        # Initialize Bedrock service
        bedrock_service = BedrockService()
        
        # Generate detailed specification
        specification = bedrock_service.generate_detailed_specification(
            enhanced_prompt, nfr_requirements, file_context
        )
        
        return jsonify({
            'success': True,
            'specification': specification,
            'enhanced_prompt': enhanced_prompt,
            'nfr_requirements': nfr_requirements
        })
        
    except Exception as e:
        logger.error(f"Error in generate_specification: {str(e)}")
        return jsonify({
            'success': False,
            'error': f'Failed to generate specification: {str(e)}'
        }), 500

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

@app.route('/api/log-frontend-error', methods=['POST'])
def log_frontend_error():
    """Receive and log frontend errors"""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        # Log the frontend error
        logging_service.log_error(
            error_type="frontend_error",
            error_message=data.get('message', 'Unknown frontend error'),
            context={
                'frontend_data': data,
                'timestamp': data.get('timestamp'),
                'url': data.get('url'),
                'user_agent': data.get('userAgent')
            }
        )
        
        return jsonify({'success': True, 'message': 'Error logged successfully'})
        
    except Exception as e:
        logger.error(f"Error logging frontend error: {str(e)}")
        return jsonify({'error': 'Failed to log error'}), 500

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