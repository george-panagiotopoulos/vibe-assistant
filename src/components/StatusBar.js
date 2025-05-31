import React, { useState, useEffect } from 'react';
import { ApiService } from '../services/ApiService';

const StatusBar = ({ loading, error, message, repositoryData, selectedFiles, config }) => {
  const [systemStatus, setSystemStatus] = useState({
    api: 'checking',
    bedrock: 'unknown'
  });

  useEffect(() => {
    checkSystemStatus();
    const interval = setInterval(checkSystemStatus, 30000); // Check every 30 seconds
    return () => clearInterval(interval);
  }, []);

  const checkSystemStatus = async () => {
    try {
      const healthResponse = await ApiService.healthCheck();
      setSystemStatus(prev => ({
        ...prev,
        api: healthResponse.status === 'healthy' ? 'healthy' : 'error'
      }));
    } catch (error) {
      setSystemStatus(prev => ({
        ...prev,
        api: 'error'
      }));
    }
  };

  const testBedrockConnection = async () => {
    try {
      setSystemStatus(prev => ({ ...prev, bedrock: 'checking' }));
      const response = await ApiService.testBedrockConnection(config);
      setSystemStatus(prev => ({
        ...prev,
        bedrock: response.connected ? 'healthy' : 'error'
      }));
    } catch (error) {
      setSystemStatus(prev => ({ ...prev, bedrock: 'error' }));
    }
  };

  const getStatusIcon = (status) => {
    switch (status) {
      case 'healthy':
        return '🟢';
      case 'error':
        return '🔴';
      case 'checking':
        return '🟡';
      default:
        return '⚪';
    }
  };

  const getStatusText = (status) => {
    switch (status) {
      case 'healthy':
        return 'Online';
      case 'error':
        return 'Error';
      case 'checking':
        return 'Checking...';
      default:
        return 'Unknown';
    }
  };

  return (
    <div className="h-7 flex items-center justify-between px-4 text-xs text-vibe-gray bg-vibe-darker">
      {/* Left side - Status info */}
      <div className="flex items-center space-x-6">
        {/* Loading indicator */}
        {loading && (
          <div className="flex items-center space-x-2">
            <div className="animate-spin w-3 h-3 border border-vibe-blue border-t-transparent rounded-full"></div>
            <span>Loading...</span>
          </div>
        )}

        {/* Error message */}
        {error && (
          <div className="flex items-center space-x-2 text-vibe-red">
            <span>⚠️</span>
            <span>{error}</span>
          </div>
        )}

        {/* Status message */}
        {message && !loading && !error && (
          <div className="flex items-center space-x-2 text-vibe-green">
            <span>ℹ️</span>
            <span>{message}</span>
          </div>
        )}

        {/* Repository info */}
        {repositoryData && (
          <div className="flex items-center space-x-4">
            <span className="text-vibe-gray opacity-60">|</span>
            <div className="flex items-center space-x-1">
              <span>📁</span>
              <span className="font-mono">{repositoryData.owner}/{repositoryData.name}</span>
            </div>
            {selectedFiles.length > 0 && (
              <div className="flex items-center space-x-1">
                <span>✓</span>
                <span>{selectedFiles.length} file{selectedFiles.length !== 1 ? 's' : ''} selected</span>
              </div>
            )}
          </div>
        )}
      </div>

      {/* Right side - System status and health check */}
      <div className="flex items-center space-x-4">
        {/* API Status */}
        <div className="flex items-center space-x-1">
          <span>{getStatusIcon(systemStatus.api)}</span>
          <span>API: {getStatusText(systemStatus.api)}</span>
        </div>

        {/* Bedrock Status */}
        <div className="flex items-center space-x-1">
          <span>{getStatusIcon(systemStatus.bedrock)}</span>
          <span>Bedrock: {getStatusText(systemStatus.bedrock)}</span>
        </div>

        {/* Health check button */}
        <button
          onClick={testBedrockConnection}
          disabled={!config.aws?.access_key_id}
          className="px-2 py-1 text-xs bg-vibe-gray-dark hover:bg-vibe-gray text-vibe-gray rounded transition-colors duration-200 disabled:opacity-50 disabled:cursor-not-allowed"
          title="Test Bedrock Connection"
        >
          🔄 Test
        </button>
      </div>
    </div>
  );
};

export default StatusBar; 