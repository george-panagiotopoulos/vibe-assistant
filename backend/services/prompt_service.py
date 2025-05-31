import logging
from typing import List, Dict, Any

logger = logging.getLogger(__name__)

class PromptService:
    """Service for building and enhancing prompts"""
    
    def __init__(self, bedrock_service):
        self.bedrock_service = bedrock_service
    
    def enhance_prompt(self, user_prompt: str, task_type: str = 'development') -> str:
        """Enhance a user prompt using AI"""
        try:
            enhanced = self.bedrock_service.enhance_prompt(user_prompt, task_type)
            return enhanced
        except Exception as e:
            logger.error(f"Error enhancing prompt: {str(e)}")
            return user_prompt  # Fallback to original prompt
    
    def build_final_prompt(
        self, 
        base_prompt: str, 
        requirements: List[str], 
        selected_files: List[Dict], 
        task_type: str = 'development'
    ) -> str:
        """Build final prompt with non-functional requirements and file references"""
        try:
            # Extract only relevant requirements using AI
            if requirements:
                relevant_requirements = self.bedrock_service.extract_relevant_requirements(
                    base_prompt, requirements, task_type
                )
            else:
                relevant_requirements = []
            
            # Build the final prompt
            final_prompt = self._construct_final_prompt(
                base_prompt, relevant_requirements, selected_files, task_type
            )
            
            return final_prompt
            
        except Exception as e:
            logger.error(f"Error building final prompt: {str(e)}")
            return base_prompt  # Fallback to base prompt
    
    def _construct_final_prompt(
        self, 
        base_prompt: str, 
        requirements: List[str], 
        selected_files: List[Dict], 
        task_type: str
    ) -> str:
        """Construct the final prompt with all components"""
        
        prompt_parts = []
        
        # Add task type context
        task_context = self._get_task_context(task_type)
        if task_context:
            prompt_parts.append(f"## Context\n{task_context}")
        
        # Add main prompt
        prompt_parts.append(f"## Task\n{base_prompt}")
        
        # Add file references if any
        if selected_files:
            file_refs = self._format_file_references(selected_files)
            prompt_parts.append(f"## Referenced Files\n{file_refs}")
        
        # Add relevant requirements
        if requirements:
            req_text = self._format_requirements(requirements, task_type)
            prompt_parts.append(f"## Non-Functional Requirements\n{req_text}")
        
        # Add general guidelines based on task type
        guidelines = self._get_task_guidelines(task_type)
        if guidelines:
            prompt_parts.append(f"## Guidelines\n{guidelines}")
        
        return "\n\n".join(prompt_parts)
    
    def _get_task_context(self, task_type: str) -> str:
        """Get context information based on task type"""
        contexts = {
            'development': "You are helping with new feature development or application creation. Focus on writing clean, maintainable, and well-tested code.",
            'refactoring': "You are helping with code refactoring. Focus on improving code structure, performance, and maintainability while preserving functionality.",
            'testing': "You are helping with testing and debugging. Focus on comprehensive test coverage, edge cases, and systematic problem-solving approaches."
        }
        return contexts.get(task_type, "")
    
    def _format_file_references(self, selected_files: List[Dict]) -> str:
        """Format selected files for inclusion in prompt"""
        if not selected_files:
            return ""
        
        file_refs = []
        for file_info in selected_files:
            if isinstance(file_info, dict):
                path = file_info.get('path', 'unknown')
                name = file_info.get('name', 'unknown')
                file_refs.append(f"- `{path}` ({name})")
            else:
                file_refs.append(f"- `{file_info}`")
        
        return "Please reference and consider the following files:\n" + "\n".join(file_refs)
    
    def _format_requirements(self, requirements: List[str], task_type: str) -> str:
        """Format requirements for inclusion in prompt"""
        if not requirements:
            return ""
        
        req_text = f"When working on this {task_type} task, please ensure you follow these requirements:\n\n"
        for i, req in enumerate(requirements, 1):
            req_text += f"{i}. {req}\n"
        
        return req_text
    
    def _get_task_guidelines(self, task_type: str) -> str:
        """Get general guidelines based on task type"""
        guidelines = {
            'development': """- Write clean, readable, and maintainable code
- Include appropriate error handling and validation
- Consider performance implications
- Add necessary documentation and comments
- Think about testing strategies
- Follow established patterns and conventions""",
            
            'refactoring': """- Preserve existing functionality while improving structure
- Identify and eliminate code duplication
- Improve naming and organization
- Consider performance optimizations
- Maintain or improve test coverage
- Document significant changes and rationale""",
            
            'testing': """- Ensure comprehensive test coverage including edge cases
- Use appropriate testing strategies (unit, integration, e2e)
- Include both positive and negative test scenarios
- Consider error conditions and boundary values
- Make tests maintainable and well-documented
- Follow testing best practices and patterns"""
        }
        return guidelines.get(task_type, "")
    
    def analyze_prompt_complexity(self, prompt: str) -> Dict[str, Any]:
        """Analyze prompt complexity and provide recommendations"""
        try:
            analysis = {
                'length': len(prompt),
                'word_count': len(prompt.split()),
                'has_file_references': bool(self._extract_file_references(prompt)),
                'estimated_complexity': 'low',
                'recommendations': []
            }
            
            # Estimate complexity
            if analysis['word_count'] > 200:
                analysis['estimated_complexity'] = 'high'
                analysis['recommendations'].append("Consider breaking down into smaller, focused prompts")
            elif analysis['word_count'] > 100:
                analysis['estimated_complexity'] = 'medium'
            
            # Check for specific patterns
            if 'test' in prompt.lower() or 'debug' in prompt.lower():
                analysis['recommendations'].append("Consider including specific error messages or test cases")
            
            if 'refactor' in prompt.lower():
                analysis['recommendations'].append("Consider specifying the current issues with the code")
            
            return analysis
            
        except Exception as e:
            logger.error(f"Error analyzing prompt complexity: {str(e)}")
            return {'error': str(e)}
    
    def _extract_file_references(self, prompt: str) -> List[str]:
        """Extract potential file references from prompt"""
        import re
        # Look for common file patterns
        patterns = [
            r'`([^`]+\.[a-zA-Z0-9]+)`',  # `filename.ext`
            r'([a-zA-Z0-9_/.-]+\.[a-zA-Z0-9]+)',  # filename.ext
            r'(\w+\.py)',  # Python files
            r'(\w+\.js)',  # JavaScript files
            r'(\w+\.tsx?)',  # TypeScript files
            r'(\w+\.java)',  # Java files
        ]
        
        file_refs = []
        for pattern in patterns:
            matches = re.findall(pattern, prompt)
            file_refs.extend(matches)
        
        return list(set(file_refs))  # Remove duplicates
    
    def suggest_improvements(self, prompt: str) -> List[str]:
        """Suggest improvements for a prompt"""
        suggestions = []
        
        # Basic checks
        if len(prompt) < 20:
            suggestions.append("Prompt seems very short. Consider adding more detail about what you want to achieve.")
        
        if not any(word in prompt.lower() for word in ['please', 'help', 'create', 'build', 'implement', 'fix', 'refactor', 'test']):
            suggestions.append("Consider adding a clear action verb (create, build, implement, fix, etc.)")
        
        if 'error' in prompt.lower() and 'message' not in prompt.lower():
            suggestions.append("When mentioning errors, consider including the actual error message.")
        
        if len(prompt.split('.')) < 2:
            suggestions.append("Consider breaking your request into multiple sentences for clarity.")
        
        return suggestions 