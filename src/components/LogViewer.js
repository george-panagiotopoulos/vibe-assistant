import React, { useRef, useEffect } from 'react';

const LogViewer = ({ logs = [], onClearLogs }) => {
  const logsEndRef = useRef(null);

  useEffect(() => {
    scrollToBottom();
  }, [logs]);

  const scrollToBottom = () => {
    logsEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  const formatTimestamp = (timestamp) => {
    return new Date(timestamp).toLocaleTimeString();
  };

  const getLogTypeIcon = (type) => {
    switch (type) {
      case 'user_input':
        return '👤';
      case 'llm_prompt':
        return '🔄';
      case 'llm_response':
        return '🤖';
      case 'frontend_error':
        return '🔴';
      case 'backend_error':
        return '⚠️';
      case 'success':
        return '✅';
      default:
        return '📝';
    }
  };

  const getLogTypeStyle = (type) => {
    switch (type) {
      case 'user_input':
        return 'bg-vibe-blue text-white';
      case 'llm_prompt':
        return 'bg-vibe-darker text-vibe-gray border border-vibe-blue';
      case 'llm_response':
        return 'bg-vibe-darker text-vibe-gray border border-vibe-green';
      case 'frontend_error':
      case 'backend_error':
        return 'bg-vibe-red text-white';
      case 'success':
        return 'bg-vibe-green text-white';
      default:
        return 'bg-vibe-darker text-vibe-gray';
    }
  };

  const getLogTypeLabel = (type) => {
    switch (type) {
      case 'user_input':
        return 'User Input';
      case 'llm_prompt':
        return 'LLM Prompt';
      case 'llm_response':
        return 'LLM Response';
      case 'frontend_error':
        return 'Frontend Error';
      case 'backend_error':
        return 'Backend Error';
      case 'success':
        return 'Success';
      default:
        return 'Log';
    }
  };

  const copyToClipboard = async (content) => {
    try {
      await navigator.clipboard.writeText(content);
    } catch (error) {
      console.error('Failed to copy to clipboard:', error);
    }
  };

  return (
    <div className="h-full flex flex-col bg-vibe-dark border-l border-vibe-gray-dark">
      {/* Header */}
      <div className="p-4 border-b border-vibe-gray-dark">
        <div className="flex items-center justify-between">
          <h3 className="text-lg font-medium text-vibe-gray">System Logs</h3>
          <div className="flex items-center space-x-2">
            <span className="text-sm text-vibe-gray">
              {logs.length} entries
            </span>
            <button
              onClick={onClearLogs}
              className="btn-secondary text-sm"
              title="Clear all logs"
            >
              🗑️ Clear
            </button>
          </div>
        </div>
        <p className="text-sm text-vibe-gray opacity-75 mt-1">
          Real-time logs of user inputs, LLM interactions, and system events
        </p>
      </div>

      {/* Logs */}
      <div className="flex-1 overflow-y-auto p-4 space-y-3">
        {logs.length === 0 ? (
          <div className="text-center text-vibe-gray opacity-60 mt-8">
            <div className="text-4xl mb-2">📋</div>
            <p>No logs yet</p>
            <p className="text-sm mt-2">System activity will appear here</p>
          </div>
        ) : (
          logs.map((log, index) => (
            <div key={index} className="fade-in">
              <div className={`p-3 rounded-lg ${getLogTypeStyle(log.type)}`}>
                <div className="flex items-start justify-between mb-2">
                  <div className="flex items-center space-x-2">
                    <span className="text-sm">{getLogTypeIcon(log.type)}</span>
                    <span className="font-medium text-sm">
                      {getLogTypeLabel(log.type)}
                    </span>
                  </div>
                  <div className="flex items-center space-x-2">
                    <span className="text-xs opacity-75">
                      {formatTimestamp(log.timestamp)}
                    </span>
                    <button
                      onClick={() => copyToClipboard(log.content)}
                      className="text-xs opacity-75 hover:opacity-100 transition-opacity"
                      title="Copy to clipboard"
                    >
                      📋
                    </button>
                  </div>
                </div>
                
                <div className="text-sm">
                  {log.type === 'llm_prompt' || log.type === 'llm_response' ? (
                    <pre className="whitespace-pre-wrap font-mono text-xs bg-black bg-opacity-20 p-2 rounded overflow-x-auto">
                      {log.content}
                    </pre>
                  ) : (
                    <div className="whitespace-pre-wrap">
                      {log.content}
                    </div>
                  )}
                </div>

                {/* Additional metadata */}
                {log.metadata && (
                  <div className="mt-2 pt-2 border-t border-opacity-20 border-white">
                    <div className="text-xs opacity-75">
                      {Object.entries(log.metadata).map(([key, value]) => (
                        <div key={key} className="flex justify-between">
                          <span>{key}:</span>
                          <span>{value}</span>
                        </div>
                      ))}
                    </div>
                  </div>
                )}
              </div>
            </div>
          ))
        )}
        <div ref={logsEndRef} />
      </div>
    </div>
  );
};

export default LogViewer; 