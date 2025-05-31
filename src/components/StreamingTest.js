import React, { useState } from 'react';
import { ApiService } from '../services/ApiService';

const StreamingTest = () => {
  const [prompt, setPrompt] = useState('');
  const [response, setResponse] = useState('');
  const [isStreaming, setIsStreaming] = useState(false);
  const [error, setError] = useState(null);

  const handleStreamTest = async () => {
    if (!prompt.trim()) {
      setError('Please enter a prompt');
      return;
    }

    setIsStreaming(true);
    setResponse('');
    setError(null);

    try {
      await ApiService.streamResponse(prompt, {
        onChunk: (chunk) => {
          setResponse(prev => prev + chunk);
        },
        onComplete: () => {
          setIsStreaming(false);
          console.log('Streaming completed');
        },
        onError: (err) => {
          setError(err.message);
          setIsStreaming(false);
        }
      });
    } catch (err) {
      setError(err.message);
      setIsStreaming(false);
    }
  };

  const clearResponse = () => {
    setResponse('');
    setError(null);
  };

  return (
    <div className="max-w-4xl mx-auto p-6 bg-white rounded-lg shadow-lg">
      <h2 className="text-2xl font-bold mb-6 text-gray-800">
        🚀 AWS Bedrock Streaming Test
      </h2>
      
      <div className="space-y-4">
        {/* Input Section */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Enter your prompt:
          </label>
          <textarea
            value={prompt}
            onChange={(e) => setPrompt(e.target.value)}
            placeholder="e.g., Explain microservices architecture in detail..."
            className="w-full p-3 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            rows={3}
            disabled={isStreaming}
          />
        </div>

        {/* Controls */}
        <div className="flex gap-3">
          <button
            onClick={handleStreamTest}
            disabled={isStreaming || !prompt.trim()}
            className={`px-6 py-2 rounded-md font-medium transition-colors ${
              isStreaming || !prompt.trim()
                ? 'bg-gray-300 text-gray-500 cursor-not-allowed'
                : 'bg-blue-600 text-white hover:bg-blue-700'
            }`}
          >
            {isStreaming ? (
              <>
                <span className="inline-block animate-spin mr-2">⏳</span>
                Streaming...
              </>
            ) : (
              'Start Streaming'
            )}
          </button>
          
          <button
            onClick={clearResponse}
            disabled={isStreaming}
            className="px-6 py-2 bg-gray-500 text-white rounded-md hover:bg-gray-600 disabled:bg-gray-300 disabled:cursor-not-allowed transition-colors"
          >
            Clear
          </button>
        </div>

        {/* Error Display */}
        {error && (
          <div className="p-4 bg-red-50 border border-red-200 rounded-md">
            <div className="flex">
              <span className="text-red-500 mr-2">❌</span>
              <div>
                <h3 className="text-sm font-medium text-red-800">Error</h3>
                <p className="text-sm text-red-700 mt-1">{error}</p>
              </div>
            </div>
          </div>
        )}

        {/* Response Display */}
        {(response || isStreaming) && (
          <div className="mt-6">
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Streaming Response:
            </label>
            <div className="bg-gray-50 border border-gray-200 rounded-md p-4 min-h-[200px]">
              <pre className="whitespace-pre-wrap text-sm text-gray-800 font-mono">
                {response}
                {isStreaming && (
                  <span className="inline-block animate-pulse bg-blue-500 w-2 h-4 ml-1"></span>
                )}
              </pre>
            </div>
            
            {response && !isStreaming && (
              <div className="mt-2 text-sm text-gray-600">
                ✅ Response completed ({response.length} characters)
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
};

export default StreamingTest; 