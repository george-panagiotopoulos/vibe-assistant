import os
import json
import logging
from datetime import datetime
from typing import Dict, Any, Optional

class LoggingService:
    """Service for logging streaming responses and application events"""
    
    def __init__(self):
        self.logs_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), '..', 'logs')
        os.makedirs(self.logs_dir, exist_ok=True)
        
        # Set up logger
        self.logger = logging.getLogger(__name__)
    
    def log_streaming_response(self, prompt: str, response_chunks: list, metadata: Dict[str, Any] = None):
        """Log a complete streaming response"""
        try:
            timestamp = datetime.now().isoformat()
            log_entry = {
                "timestamp": timestamp,
                "type": "streaming_response",
                "prompt": prompt,
                "response_chunks": response_chunks,
                "full_response": "".join(response_chunks),
                "chunk_count": len(response_chunks),
                "total_length": len("".join(response_chunks)),
                "metadata": metadata or {}
            }
            
            # Write to streaming log file
            log_file = os.path.join(self.logs_dir, f"streaming_responses_{datetime.now().strftime('%Y%m%d')}.log")
            with open(log_file, 'a', encoding='utf-8') as f:
                f.write(json.dumps(log_entry, ensure_ascii=False) + '\n')
                
            self.logger.info(f"Logged streaming response: {len(response_chunks)} chunks, {len(''.join(response_chunks))} chars")
            
        except Exception as e:
            self.logger.error(f"Failed to log streaming response: {str(e)}")
    
    def log_api_request(self, endpoint: str, request_data: Dict[str, Any], response_data: Dict[str, Any] = None, error: str = None):
        """Log API requests and responses"""
        try:
            timestamp = datetime.now().isoformat()
            log_entry = {
                "timestamp": timestamp,
                "type": "api_request",
                "endpoint": endpoint,
                "request_data": request_data,
                "response_data": response_data,
                "error": error,
                "success": error is None
            }
            
            # Write to API log file
            log_file = os.path.join(self.logs_dir, f"api_requests_{datetime.now().strftime('%Y%m%d')}.log")
            with open(log_file, 'a', encoding='utf-8') as f:
                f.write(json.dumps(log_entry, ensure_ascii=False) + '\n')
                
        except Exception as e:
            self.logger.error(f"Failed to log API request: {str(e)}")
    
    def log_error(self, error_type: str, error_message: str, context: Dict[str, Any] = None):
        """Log application errors"""
        try:
            timestamp = datetime.now().isoformat()
            log_entry = {
                "timestamp": timestamp,
                "type": "error",
                "error_type": error_type,
                "error_message": error_message,
                "context": context or {}
            }
            
            # Write to error log file
            log_file = os.path.join(self.logs_dir, f"errors_{datetime.now().strftime('%Y%m%d')}.log")
            with open(log_file, 'a', encoding='utf-8') as f:
                f.write(json.dumps(log_entry, ensure_ascii=False) + '\n')
                
        except Exception as e:
            self.logger.error(f"Failed to log error: {str(e)}")

# Global logging service instance
logging_service = LoggingService() 