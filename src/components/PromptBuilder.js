import React, { useState, useEffect } from 'react';
import { ApiService } from '../services/ApiService';

const PromptBuilder = ({ selectedFiles, onPromptChange, config }) => {
  const [prompt, setPrompt] = useState('');
  const [taskType, setTaskType] = useState('development');
  const [includeContext, setIncludeContext] = useState(true);
  const [includeRequirements, setIncludeRequirements] = useState(true);
  const [finalPrompt, setFinalPrompt] = useState('');
  const [isBuilding, setIsBuilding] = useState(false);

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

  useEffect(() => {
    onPromptChange(prompt);
  }, [prompt, onPromptChange]);

  const buildFinalPrompt = async () => {
    if (!prompt.trim()) {
      setFinalPrompt('');
      return;
    }

    setIsBuilding(true);
    try {
      const response = await ApiService.buildFinalPrompt({
        prompt,
        task_type: taskType,
        selected_files: selectedFiles,
        include_context: includeContext,
        include_requirements: includeRequirements,
        config
      });
      setFinalPrompt(response.final_prompt);
    } catch (error) {
      console.error('Failed to build final prompt:', error);
      setFinalPrompt(prompt); // Fallback to original prompt
    } finally {
      setIsBuilding(false);
    }
  };

  const copyToClipboard = async () => {
    try {
      await navigator.clipboard.writeText(finalPrompt || prompt);
    } catch (error) {
      console.error('Failed to copy to clipboard:', error);
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
              onClick={buildFinalPrompt}
              disabled={!prompt.trim() || isBuilding}
              className="btn-primary disabled:opacity-50"
            >
              {isBuilding ? '🔄 Building...' : '🔨 Build Final Prompt'}
            </button>
            <button
              onClick={() => setPrompt('')}
              className="btn-secondary"
            >
              🗑️ Clear
            </button>
          </div>
          
          {finalPrompt && (
            <button
              onClick={copyToClipboard}
              className="btn-secondary"
            >
              📋 Copy Final
            </button>
          )}
        </div>

        {/* Final Prompt Preview */}
        {finalPrompt && (
          <div className="border-t border-vibe-gray-dark pt-6">
            <div className="flex items-center justify-between mb-2">
              <label className="text-sm font-medium text-vibe-gray">
                🎯 Final Prompt
              </label>
              <div className="text-xs text-vibe-gray opacity-60">
                {finalPrompt.length} characters
              </div>
            </div>
            <div className="panel p-4 max-h-64 overflow-y-auto">
              <pre className="text-sm text-vibe-gray whitespace-pre-wrap font-mono">
                {finalPrompt}
              </pre>
            </div>
          </div>
        )}

        {/* Context Preview */}
        {selectedFiles.length > 0 && (
          <div className="border-t border-vibe-gray-dark pt-6">
            <label className="text-sm font-medium text-vibe-gray mb-2 block">
              📁 Selected Files Context
            </label>
            <div className="panel p-4 max-h-32 overflow-y-auto">
              <div className="space-y-1">
                {selectedFiles.map((file, index) => (
                  <div key={index} className="flex items-center text-sm text-vibe-gray">
                    <span className="mr-2">
                      {file.type === 'file' ? '📄' : '📁'}
                    </span>
                    <span className="font-mono">{file.path}</span>
                    {file.size && (
                      <span className="ml-auto text-xs opacity-60">
                        {(file.size / 1024).toFixed(1)} KB
                      </span>
                    )}
                  </div>
                ))}
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default PromptBuilder; 