import React, { useState, useEffect, useCallback } from 'react';
import { ApiService } from '../services/ApiService';

const RequirementsEditor = ({ config }) => {
  const [taskType, setTaskType] = useState('development');
  const [requirements, setRequirements] = useState([]);
  const [newRequirement, setNewRequirement] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState('');
  const [successMessage, setSuccessMessage] = useState('');

  const taskTypes = [
    { value: 'development', label: 'Development', icon: '💻' },
    { value: 'refactoring', label: 'Refactoring', icon: '🔄' },
    { value: 'testing', label: 'Testing', icon: '🧪' },
    { value: 'documentation', label: 'Documentation', icon: '📚' },
    { value: 'review', label: 'Code Review', icon: '👀' }
  ];

  const loadRequirements = useCallback(async () => {
    setIsLoading(true);
    setError('');
    
    try {
      const response = await ApiService.getRequirements(taskType, config);
      setRequirements(response.requirements || []);
    } catch (err) {
      setError(err.message || 'Failed to load requirements');
      setRequirements([]);
    } finally {
      setIsLoading(false);
    }
  }, [taskType, config]);

  useEffect(() => {
    loadRequirements();
  }, [loadRequirements]);

  const saveRequirements = async () => {
    setIsLoading(true);
    setError('');
    setSuccessMessage('');
    
    try {
      await ApiService.updateRequirements(taskType, requirements, config);
      setSuccessMessage('Requirements saved successfully!');
      setTimeout(() => setSuccessMessage(''), 3000);
    } catch (err) {
      setError(err.message || 'Failed to save requirements');
    } finally {
      setIsLoading(false);
    }
  };

  const addRequirement = () => {
    if (!newRequirement.trim()) return;
    
    const requirement = {
      id: Date.now(),
      text: newRequirement.trim(),
      priority: 'medium',
      category: 'functional'
    };
    
    setRequirements([...requirements, requirement]);
    setNewRequirement('');
  };

  const updateRequirement = (id, field, value) => {
    setRequirements(requirements.map(req => 
      req.id === id ? { ...req, [field]: value } : req
    ));
  };

  const removeRequirement = (id) => {
    setRequirements(requirements.filter(req => req.id !== id));
  };

  const getPriorityColor = (priority) => {
    switch (priority) {
      case 'high':
        return 'text-vibe-red';
      case 'medium':
        return 'text-vibe-orange';
      case 'low':
        return 'text-vibe-green';
      default:
        return 'text-vibe-gray';
    }
  };

  const getCategoryIcon = (category) => {
    switch (category) {
      case 'functional':
        return '⚙️';
      case 'performance':
        return '⚡';
      case 'security':
        return '🔒';
      case 'usability':
        return '👤';
      case 'reliability':
        return '🛡️';
      default:
        return '📝';
    }
  };

  return (
    <div className="h-full flex flex-col bg-vibe-dark">
      {/* Header */}
      <div className="p-4 border-b border-vibe-gray-dark">
        <h2 className="text-lg font-medium text-vibe-gray mb-4">Requirements Editor</h2>
        
        <div className="flex items-center space-x-4">
          <div className="flex-1">
            <label className="block text-sm font-medium text-vibe-gray mb-2">
              Task Type
            </label>
            <select
              value={taskType}
              onChange={(e) => setTaskType(e.target.value)}
              className="input-primary w-full"
            >
              {taskTypes.map(type => (
                <option key={type.value} value={type.value}>
                  {type.icon} {type.label}
                </option>
              ))}
            </select>
          </div>
          
          <button
            onClick={saveRequirements}
            disabled={isLoading}
            className="btn-primary mt-6 disabled:opacity-50"
          >
            {isLoading ? 'Saving...' : 'Save Requirements'}
          </button>
        </div>
        
        {error && (
          <div className="mt-2 p-2 bg-vibe-red bg-opacity-20 border border-vibe-red rounded text-vibe-red text-sm">
            {error}
          </div>
        )}
        
        {successMessage && (
          <div className="mt-2 p-2 bg-vibe-green bg-opacity-20 border border-vibe-green rounded text-vibe-green text-sm">
            {successMessage}
          </div>
        )}
      </div>

      {/* Add New Requirement */}
      <div className="p-4 border-b border-vibe-gray-dark">
        <div className="flex space-x-2">
          <input
            type="text"
            value={newRequirement}
            onChange={(e) => setNewRequirement(e.target.value)}
            placeholder="Add a new requirement..."
            className="flex-1 input-primary"
            onKeyPress={(e) => e.key === 'Enter' && addRequirement()}
          />
          <button
            onClick={addRequirement}
            disabled={!newRequirement.trim()}
            className="btn-primary disabled:opacity-50"
          >
            Add
          </button>
        </div>
      </div>

      {/* Requirements List */}
      <div className="flex-1 overflow-y-auto p-4">
        {isLoading && requirements.length === 0 ? (
          <div className="flex items-center justify-center py-8">
            <div className="animate-spin w-6 h-6 border border-vibe-blue border-t-transparent rounded-full"></div>
            <span className="ml-2 text-vibe-gray">Loading requirements...</span>
          </div>
        ) : requirements.length === 0 ? (
          <div className="text-center text-vibe-gray opacity-60 py-8">
            <div className="text-4xl mb-2">📋</div>
            <p>No requirements defined for {taskTypes.find(t => t.value === taskType)?.label}</p>
            <p className="text-sm mt-2">Add your first requirement above to get started.</p>
          </div>
        ) : (
          <div className="space-y-3">
            {requirements.map((requirement) => (
              <div
                key={requirement.id}
                className="bg-vibe-darker border border-vibe-gray-dark rounded p-3"
              >
                <div className="flex items-start space-x-3">
                  <span className="text-lg mt-1">
                    {getCategoryIcon(requirement.category)}
                  </span>
                  
                  <div className="flex-1">
                    <textarea
                      value={requirement.text}
                      onChange={(e) => updateRequirement(requirement.id, 'text', e.target.value)}
                      className="w-full bg-transparent text-vibe-gray resize-none border-none outline-none"
                      rows="2"
                    />
                    
                    <div className="flex items-center space-x-4 mt-2">
                      <select
                        value={requirement.priority}
                        onChange={(e) => updateRequirement(requirement.id, 'priority', e.target.value)}
                        className={`text-xs bg-vibe-darkest border border-vibe-gray-dark rounded px-2 py-1 ${getPriorityColor(requirement.priority)}`}
                      >
                        <option value="low">Low Priority</option>
                        <option value="medium">Medium Priority</option>
                        <option value="high">High Priority</option>
                      </select>
                      
                      <select
                        value={requirement.category}
                        onChange={(e) => updateRequirement(requirement.id, 'category', e.target.value)}
                        className="text-xs bg-vibe-darkest border border-vibe-gray-dark rounded px-2 py-1 text-vibe-gray"
                      >
                        <option value="functional">Functional</option>
                        <option value="performance">Performance</option>
                        <option value="security">Security</option>
                        <option value="usability">Usability</option>
                        <option value="reliability">Reliability</option>
                      </select>
                    </div>
                  </div>
                  
                  <button
                    onClick={() => removeRequirement(requirement.id)}
                    className="text-vibe-red hover:bg-vibe-red hover:bg-opacity-20 p-1 rounded"
                  >
                    🗑️
                  </button>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
};

export default RequirementsEditor; 