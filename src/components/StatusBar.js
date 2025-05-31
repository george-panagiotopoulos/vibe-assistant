import React, { useState, useEffect } from 'react';

const StatusBar = ({ loading, error, message, repositoryData, selectedFiles, config }) => {
  const [systemStatus, setSystemStatus] = useState({
    api: 'unknown',
    bedrock: 'unknown'
  });

  useEffect(() => {
    checkSystemStatus();
  }, []);

  const checkSystemStatus = async () => {
    try {
      setSystemStatus(prev => ({ ...prev, api: 'checking' }));
      const response = await fetch('/api/health');
      if (response.ok) {
        setSystemStatus(prev => ({
          ...prev,
          api: 'healthy'
        }));
      } else {
        setSystemStatus(prev => ({
          ...prev,
          api: 'error'
        }));
      }
    } catch (error) {
      setSystemStatus(prev => ({
        ...prev,
        api: 'error'
      }));
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

      {/* Right side - System status */}
      <div className="flex items-center space-x-4">
        {/* API Status */}
        <div className="flex items-center space-x-1">
          <span>{getStatusIcon(systemStatus.api)}</span>
          <span>API: {getStatusText(systemStatus.api)}</span>
        </div>

        {/* Configuration Status */}
        <div className="flex items-center space-x-1">
          <span>{config?.aws?.access_key_id ? '🟢' : '��'}</span>
          <span>Config: {config?.aws?.access_key_id ? 'Ready' : 'Missing'}</span>
        </div>
      </div>
    </div>
  );
};

export default StatusBar; 