import React, { useState, useEffect } from 'react';
import loggingService from '../services/LoggingService';

const PromptBuilder = ({ selectedFiles, onPromptEnhancement, config }) => {
  const [prompt, setPrompt] = useState('');
  const [taskType, setTaskType] = useState('development');
  const [includeContext, setIncludeContext] = useState(true);
  const [includeRequirements, setIncludeRequirements] = useState(true);
  const [enhancedSpecification, setEnhancedSpecification] = useState('');
  const [isEnhancing, setIsEnhancing] = useState(false);
  const [enhancementMetadata, setEnhancementMetadata] = useState(null);

  const taskTypes = [
    { value: 'development', label: 'Development', icon: '💻' },
    { value: 'refactoring', label: 'Refactoring', icon: '🔧' },
    { value: 'testing', label: 'Testing', icon: '🧪' },
    { value: 'documentation', label: 'Documentation', icon: '📝' },
    { value: 'review', label: 'Code Review', icon: '👀' }
  ];

  useEffect(() => {
    if (config?.preferences?.default_task_type) {
      setTaskType(config.preferences.default_task_type);
    }
  }, [config]);

  const enhancePrompt = async () => {
    if (!prompt.trim()) {
      setEnhancedSpecification('');
      return;
    }

    setIsEnhancing(true);
    loggingService.logInfo('Starting prompt enhancement in PromptBuilder', {
      promptLength: prompt.length,
      taskType,
      selectedFilesCount: selectedFiles.length
    });

    try {
      const response = await onPromptEnhancement(prompt, taskType, selectedFiles);
      
      loggingService.logInfo('Received response from onPromptEnhancement', {
        response: response,
        hasEnhancedSpec: !!response?.enhanced_specification,
        responseKeys: Object.keys(response || {})
      });
      
      // The API returns the data directly (not wrapped in success)
      if (response && response.enhanced_specification) {
        setEnhancedSpecification(response.enhanced_specification);
        setEnhancementMetadata(response.metadata);
        loggingService.logInfo('Enhancement successful', {
          specLength: response.enhanced_specification.length,
          metadata: response.metadata
        });
      } else {
        const errorMsg = 'Enhancement failed. Response format unexpected.';
        setEnhancedSpecification(errorMsg);
        setEnhancementMetadata(null);
        loggingService.logError('enhancement_format_error', errorMsg, {
          response: response,
          responseType: typeof response,
          responseKeys: response ? Object.keys(response) : 'null'
        });
      }
    } catch (error) {
      console.error('Failed to enhance prompt:', error);
      const errorMsg = `Enhancement failed: ${error.message}`;
      setEnhancedSpecification(errorMsg);
      setEnhancementMetadata(null);
      loggingService.logError('enhancement_exception', error.message, {
        prompt: prompt.substring(0, 100) + '...',
        taskType,
        selectedFilesCount: selectedFiles.length,
        error: error.toString(),
        stack: error.stack
      });
    } finally {
      setIsEnhancing(false);
    }
  };

  const copyToClipboard = async () => {
    try {
      await navigator.clipboard.writeText(enhancedSpecification || prompt);
      loggingService.logInfo('Copied to clipboard successfully');
    } catch (error) {
      console.error('Failed to copy to clipboard:', error);
      loggingService.logError('clipboard_copy', error.message);
    }
  };

  const getTaskIcon = (type) => {
    const task = taskTypes.find(t => t.value === type);
    return task ? task.icon : '💻';
  };

  const getSelectedFilesPreview = () => {
    if (selectedFiles.length === 0) return 'No files selected';
    if (selectedFiles.length === 1) return selectedFiles[0].name;
    return `${selectedFiles.length} files selected`;
  };

  return (
    <div className="h-full flex flex-col bg-vibe-dark">
      {/* Header */}
      <div className="p-6 border-b border-vibe-gray-dark">
        <h2 className="text-xl font-medium text-vibe-gray mb-4">Prompt Builder</h2>
        
        {/* Controls */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-4">
          <div>
            <label className="block text-sm font-medium text-vibe-gray mb-2">
              Task Type
            </label>
            <select
              value={taskType}
              onChange={(e) => setTaskType(e.target.value)}
              className="input-primary w-full"
            >
              {taskTypes.map((type) => (
                <option key={type.value} value={type.value}>
                  {type.icon} {type.label}
                </option>
              ))}
            </select>
          </div>

          <div>
            <label className="block text-sm font-medium text-vibe-gray mb-2">
              Selected Files
            </label>
            <div className="input-primary w-full cursor-default flex items-center">
              <span className="text-vibe-gray opacity-75">
                📁 {getSelectedFilesPreview()}
              </span>
            </div>
          </div>

          <div className="space-y-2">
            <label className="block text-sm font-medium text-vibe-gray">
              Options
            </label>
            <div className="flex flex-col space-y-1">
              <label className="flex items-center text-sm text-vibe-gray">
                <input
                  type="checkbox"
                  checked={includeContext}
                  onChange={(e) => setIncludeContext(e.target.checked)}
                  className="mr-2"
                />
                Include file context
              </label>
              <label className="flex items-center text-sm text-vibe-gray">
                <input
                  type="checkbox"
                  checked={includeRequirements}
                  onChange={(e) => setIncludeRequirements(e.target.checked)}
                  className="mr-2"
                />
                Include requirements
              </label>
            </div>
          </div>
        </div>
      </div>

      {/* Main Content */}
      <div className="flex-1 flex flex-col p-6 space-y-6">
        {/* Prompt Input */}
        <div className="flex-1 flex flex-col">
          <div className="flex items-center justify-between mb-2">
            <label className="text-sm font-medium text-vibe-gray">
              {getTaskIcon(taskType)} Your Prompt
            </label>
            <div className="text-xs text-vibe-gray opacity-60">
              {prompt.length} characters
            </div>
          </div>
          <textarea
            value={prompt}
            onChange={(e) => setPrompt(e.target.value)}
            placeholder={`Describe what you want to ${taskType === 'development' ? 'build' : taskType === 'refactoring' ? 'refactor' : taskType === 'testing' ? 'test' : 'do'}...`}
            className="flex-1 input-primary resize-none font-mono text-sm"
            style={{ minHeight: '200px' }}
          />
        </div>

        {/* Action Buttons */}
        <div className="flex justify-between items-center">
          <div className="flex space-x-2">
            <button
              onClick={enhancePrompt}
              disabled={!prompt.trim() || isEnhancing}
              className="btn-primary disabled:opacity-50"
            >
              {isEnhancing ? '🔄 Enhancing...' : '✨ Enhance with AI'}
            </button>
            <button
              onClick={() => {
                setPrompt('');
                setEnhancedSpecification('');
                setEnhancementMetadata(null);
              }}
              className="btn-secondary"
            >
              🗑️ Clear
            </button>
          </div>
          
          {enhancedSpecification && (
            <button
              onClick={copyToClipboard}
              className="btn-secondary"
            >
              📋 Copy Specification
            </button>
          )}
        </div>

        {/* Enhanced Specification Preview */}
        {enhancedSpecification && (
          <div className="border-t border-vibe-gray-dark pt-6">
            <div className="flex items-center justify-between mb-2">
              <label className="text-sm font-medium text-vibe-gray">
                🎯 Enhanced Business Requirements Specification
              </label>
              <div className="text-xs text-vibe-gray opacity-60 flex items-center space-x-4">
                {enhancementMetadata && (
                  <>
                    <span>NFRs: {enhancementMetadata.nfr_count || 0}</span>
                    <span>Files: {enhancementMetadata.file_count || 0}</span>
                    <span>Model: {enhancementMetadata.model_used || 'Claude'}</span>
                  </>
                )}
                <span>{enhancedSpecification.length} characters</span>
              </div>
            </div>
            <div className="panel p-4 max-h-96 overflow-y-auto">
              <pre className="text-sm text-vibe-gray whitespace-pre-wrap font-mono">
                {enhancedSpecification}
              </pre>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default PromptBuilder; 