import React, { useState, useRef, useEffect, useCallback } from 'react';
import { ApiService } from '../services/ApiService';

const AIAssistant = ({ 
  currentPrompt, 
  onPromptUpdate, 
  selectedFiles,
  config 
}) => {
  const [messages, setMessages] = useState([]);
  const [inputMessage, setInputMessage] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [isConnected, setIsConnected] = useState(false);
  const messagesEndRef = useRef(null);

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const testBedrockConnection = useCallback(async () => {
    try {
      // Test Bedrock connection with current config
      const response = await ApiService.testBedrockConnection(config);
      setIsConnected(response.connected);
      if (!response.connected) {
        setMessages(prev => [...prev, {
          id: Date.now(),
          type: 'system',
          content: 'AWS Bedrock connection failed. Please check your configuration.',
          timestamp: new Date()
        }]);
      }
    } catch (error) {
      setIsConnected(false);
      setMessages(prev => [...prev, {
        id: Date.now(),
        type: 'system',
        content: `Connection error: ${error.message}`,
        timestamp: new Date()
      }]);
    }
  }, [config]);

  useEffect(() => {
    testBedrockConnection();
  }, [testBedrockConnection]);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  const enhancePrompt = async () => {
    if (!currentPrompt.trim()) return;

    setIsLoading(true);
    try {
      const response = await ApiService.enhancePrompt(
        currentPrompt,
        selectedFiles,
        config
      );

      const enhancedPrompt = response.enhanced_prompt || response.final_prompt || currentPrompt;
      onPromptUpdate(enhancedPrompt);
      
      setMessages(prev => [...prev, {
        id: Date.now(),
        type: 'assistant',
        content: 'Prompt enhanced successfully! The improved version has been applied to your prompt builder.',
        timestamp: new Date()
      }]);
    } catch (error) {
      setMessages(prev => [...prev, {
        id: Date.now(),
        type: 'error',
        content: `Enhancement failed: ${error.message}`,
        timestamp: new Date()
      }]);
    } finally {
      setIsLoading(false);
    }
  };

  const sendMessage = async (e) => {
    e.preventDefault();
    if (!inputMessage.trim() || isLoading) return;

    const userMessage = {
      id: Date.now(),
      type: 'user',
      content: inputMessage,
      timestamp: new Date()
    };

    setMessages(prev => [...prev, userMessage]);
    setInputMessage('');
    setIsLoading(true);

    try {
      const response = await ApiService.chatWithAI(
        inputMessage,
        currentPrompt,
        selectedFiles,
        config
      );

      setMessages(prev => [...prev, {
        id: Date.now() + 1,
        type: 'assistant',
        content: response.response || response.content || 'No response received',
        timestamp: new Date()
      }]);
    } catch (error) {
      setMessages(prev => [...prev, {
        id: Date.now() + 1,
        type: 'error',
        content: `Error: ${error.message}`,
        timestamp: new Date()
      }]);
    } finally {
      setIsLoading(false);
    }
  };

  const getMessageIcon = (type) => {
    switch (type) {
      case 'user':
        return '👤';
      case 'assistant':
        return '🤖';
      case 'system':
        return 'ℹ️';
      case 'error':
        return '⚠️';
      default:
        return '💬';
    }
  };

  const getMessageStyle = (type) => {
    switch (type) {
      case 'user':
        return 'bg-vibe-blue text-white ml-8';
      case 'assistant':
        return 'bg-vibe-darker text-vibe-gray mr-8';
      case 'system':
        return 'bg-vibe-darkest text-vibe-gray border border-vibe-gray-dark';
      case 'error':
        return 'bg-vibe-red text-white border border-red-600';
      default:
        return 'bg-vibe-darker text-vibe-gray';
    }
  };

  return (
    <div className="h-full flex flex-col bg-vibe-dark border-l border-vibe-gray-dark">
      {/* Header */}
      <div className="p-4 border-b border-vibe-gray-dark">
        <div className="flex items-center justify-between">
          <h3 className="text-lg font-medium text-vibe-gray">AI Assistant</h3>
          <div className="flex items-center space-x-2">
            <div className={`w-2 h-2 rounded-full ${isConnected ? 'bg-vibe-green' : 'bg-vibe-red'}`}></div>
            <span className="text-sm text-vibe-gray">
              {isConnected ? 'Connected' : 'Disconnected'}
            </span>
          </div>
        </div>
        
        {/* Quick Actions */}
        <div className="mt-3 flex space-x-2">
          <button
            onClick={enhancePrompt}
            disabled={!currentPrompt.trim() || isLoading || !isConnected}
            className="btn-primary text-sm disabled:opacity-50 disabled:cursor-not-allowed"
          >
            ✨ Enhance Prompt
          </button>
          <button
            onClick={() => setMessages([])}
            className="btn-secondary text-sm"
          >
            🗑️ Clear Chat
          </button>
        </div>
      </div>

      {/* Messages */}
      <div className="flex-1 overflow-y-auto p-4 space-y-4">
        {messages.length === 0 ? (
          <div className="text-center text-vibe-gray opacity-60 mt-8">
            <div className="text-4xl mb-2">🤖</div>
            <p>Start a conversation to get help with your prompts!</p>
            <p className="text-sm mt-2">Try asking me to enhance your current prompt or help with requirements.</p>
          </div>
        ) : (
          messages.map((message) => (
            <div key={message.id} className="fade-in">
              <div className={`p-3 rounded-lg ${getMessageStyle(message.type)}`}>
                <div className="flex items-start space-x-2">
                  <span className="text-sm">{getMessageIcon(message.type)}</span>
                  <div className="flex-1">
                    <div className="whitespace-pre-wrap text-sm">{message.content}</div>
                    <div className="text-xs opacity-60 mt-1">
                      {message.timestamp.toLocaleTimeString()}
                    </div>
                  </div>
                </div>
              </div>
            </div>
          ))
        )}
        
        {isLoading && (
          <div className="flex items-center space-x-2 text-vibe-gray">
            <div className="animate-spin w-4 h-4 border border-vibe-blue border-t-transparent rounded-full"></div>
            <span className="text-sm">AI is thinking...</span>
          </div>
        )}
        
        <div ref={messagesEndRef} />
      </div>

      {/* Input */}
      <div className="p-4 border-t border-vibe-gray-dark">
        <form onSubmit={sendMessage} className="flex space-x-2">
          <input
            type="text"
            value={inputMessage}
            onChange={(e) => setInputMessage(e.target.value)}
            placeholder="Ask me anything about your prompt..."
            className="flex-1 input-primary text-sm"
            disabled={isLoading || !isConnected}
          />
          <button
            type="submit"
            disabled={!inputMessage.trim() || isLoading || !isConnected}
            className="btn-primary text-sm disabled:opacity-50 disabled:cursor-not-allowed"
          >
            Send
          </button>
        </form>
        
        {!isConnected && (
          <div className="mt-2 text-xs text-vibe-red">
            Please configure AWS Bedrock connection in settings
          </div>
        )}
      </div>
    </div>
  );
};

export default AIAssistant; 