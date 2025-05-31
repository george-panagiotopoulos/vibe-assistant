import logging
from typing import Dict, List, Optional, Any
from datetime import datetime

logger = logging.getLogger(__name__)

class PromptConstructor:
    """
    Advanced prompt constructor for the Vibe Coding Assistant.
    Builds sophisticated LLM prompts that incorporate user input, non-functional requirements,
    and detailed instructions optimized for coding assistance.
    """
    
    def __init__(self, bedrock_service=None, config_service=None):
        self.bedrock_service = bedrock_service
        self.config_service = config_service
        
    def construct_enhanced_prompt(
        self, 
        user_input: str, 
        nfr_requirements: List[str] = None, 
        task_type: str = 'development',
        file_context: List[Dict] = None,
        config: Dict = None
    ) -> Dict[str, Any]:
        """
        Construct a comprehensive LLM prompt that transforms user input into a detailed
        Business Requirements Specification optimized for the Vibe Coding Assistant.
        
        Args:
            user_input: The original user prompt/request
            nfr_requirements: List of non-functional requirements
            task_type: Type of coding task (development, refactoring, testing, etc.)
            file_context: Selected files and their context
            config: Application configuration
            
        Returns:
            Dict containing the constructed prompt and metadata
        """
        try:
            # Get system prompt from config
            system_prompt = self._get_system_prompt(task_type)
            
            # Construct the main prompt
            main_prompt = self._build_main_prompt(
                user_input, 
                nfr_requirements, 
                task_type, 
                file_context, 
                config
            )
            
            # Add enhancement instructions
            enhancement_instructions = self._build_enhancement_instructions(task_type)
            
            # Combine all parts
            final_prompt = f"{main_prompt}\n\n{enhancement_instructions}"
            
            return {
                'system_prompt': system_prompt,
                'user_prompt': final_prompt,
                'original_input': user_input,
                'task_type': task_type,
                'nfr_count': len(nfr_requirements) if nfr_requirements else 0,
                'file_count': len(file_context) if file_context else 0,
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error constructing enhanced prompt: {str(e)}")
            raise
    
    def _get_system_prompt(self, task_type: str) -> str:
        """Get system prompt from config service"""
        try:
            if self.config_service:
                config = self.config_service.get_config()
                system_prompts = config.get('system_prompt', {})
                return system_prompts.get(task_type, self._get_default_system_prompt())
            else:
                return self._get_default_system_prompt()
        except Exception as e:
            logger.warning(f"Failed to get system prompt from config: {str(e)}")
            return self._get_default_system_prompt()
    
    def _get_default_system_prompt(self) -> str:
        """Fallback system prompt if config is not available"""
        return "You are an expert AI coding assistant. Provide detailed, actionable specifications for coding projects."
    
    def _build_main_prompt(
        self, 
        user_input: str, 
        nfr_requirements: List[str], 
        task_type: str, 
        file_context: List[Dict], 
        config: Dict
    ) -> str:
        """Build the main prompt incorporating all context and requirements."""
        
        prompt_sections = []
        
        # Header
        prompt_sections.append("# VIBE CODING ASSISTANT - ENHANCED SPECIFICATION REQUEST")
        prompt_sections.append(f"**Task Type:** {task_type.title()}")
        prompt_sections.append(f"**Timestamp:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        prompt_sections.append("")
        
        # Original user request
        prompt_sections.append("## ORIGINAL USER REQUEST")
        prompt_sections.append(f"```\n{user_input}\n```")
        prompt_sections.append("")
        
        # Non-functional requirements
        if nfr_requirements:
            prompt_sections.append("## NON-FUNCTIONAL REQUIREMENTS")
            prompt_sections.append("The following non-functional requirements must be incorporated:")
            for i, req in enumerate(nfr_requirements, 1):
                prompt_sections.append(f"{i}. {req}")
            prompt_sections.append("")
        
        # File context
        if file_context:
            prompt_sections.append("## CODEBASE CONTEXT")
            prompt_sections.append(f"Selected files for context ({len(file_context)} files):")
            for file_info in file_context[:10]:  # Limit to first 10 files
                file_name = file_info.get('name', file_info.get('path', 'Unknown'))
                file_type = file_info.get('type', 'file')
                prompt_sections.append(f"- **{file_name}** ({file_type})")
            
            if len(file_context) > 10:
                prompt_sections.append(f"- ... and {len(file_context) - 10} more files")
            prompt_sections.append("")
        
        # Configuration context
        if config:
            prompt_sections.append("## PROJECT CONFIGURATION")
            if config.get('preferences'):
                prefs = config['preferences']
                if prefs.get('coding_style'):
                    prompt_sections.append(f"- **Coding Style:** {prefs['coding_style']}")
                if prefs.get('framework_preference'):
                    prompt_sections.append(f"- **Framework Preference:** {prefs['framework_preference']}")
                if prefs.get('testing_framework'):
                    prompt_sections.append(f"- **Testing Framework:** {prefs['testing_framework']}")
            prompt_sections.append("")
        
        return "\n".join(prompt_sections)
    
    def _build_enhancement_instructions(self, task_type: str) -> str:
        """Build specific instructions for how the LLM should enhance the prompt."""
        
        return f"""## ENHANCEMENT INSTRUCTIONS

Transform the above user request into a comprehensive Business Requirements Specification for this {task_type} project.

Please provide:

1. **Executive Summary** - Clear project objective and scope
2. **Functional Requirements** - Specific features and capabilities
3. **Technical Specifications** - Architecture, technology stack, and implementation details
4. **Implementation Strategy** - Development approach and milestones
5. **Quality Assurance** - Testing strategy and quality standards
6. **Success Criteria** - Measurable acceptance criteria

**IMPORTANT:** Provide a detailed, actionable specification that serves as a complete Business Requirements Document."""
    
    def enhance_with_llm(self, constructed_prompt: Dict[str, Any]) -> Dict[str, Any]:
        """
        Send the constructed prompt to the LLM and get an enhanced specification.
        
        Args:
            constructed_prompt: The prompt dictionary from construct_enhanced_prompt
            
        Returns:
            Dict containing the LLM response and metadata
        """
        if not self.bedrock_service:
            raise ValueError("BedrockService not available for LLM enhancement")
        
        try:
            # Send to LLM using the configured model from BedrockService
            enhanced_response = self.bedrock_service.invoke_claude(
                prompt=constructed_prompt['user_prompt'],
                system_prompt=constructed_prompt['system_prompt'],
                max_tokens=4000,
                temperature=0.3
            )
            
            return {
                'enhanced_specification': enhanced_response.strip(),
                'original_input': constructed_prompt['original_input'],
                'constructed_prompt': constructed_prompt['user_prompt'],
                'system_prompt': constructed_prompt['system_prompt'],
                'task_type': constructed_prompt['task_type'],
                'metadata': {
                    'nfr_count': constructed_prompt['nfr_count'],
                    'file_count': constructed_prompt['file_count'],
                    'enhancement_timestamp': datetime.now().isoformat(),
                    'model_used': self.bedrock_service.model_id
                }
            }
            
        except Exception as e:
            logger.error(f"Error enhancing prompt with LLM: {str(e)}")
            raise 