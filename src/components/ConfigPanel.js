import React, { useState, useEffect } from 'react';

const ConfigPanel = ({ config, onConfigUpdate }) => {
  const [localConfig, setLocalConfig] = useState({
    aws: {
      access_key_id: '',
      secret_access_key: '',
      region: 'us-east-1',
      bedrock_model_id: 'anthropic.claude-3-5-sonnet-20240620-v1:0'
    },
    github: {
      token: '',
      default_repo: ''
    },
    preferences: {
      auto_enhance: false,
      include_file_content: true,
      max_file_size: 100,
      editor_theme: 'dark'
    }
  });

  const [showSecrets, setShowSecrets] = useState({
    aws_secret: false,
    github_token: false
  });

  useEffect(() => {
    if (config) {
      setLocalConfig(config);
    }
  }, [config]);

  const handleInputChange = (section, field, value) => {
    setLocalConfig(prev => ({
      ...prev,
      [section]: {
        ...prev[section],
        [field]: value
      }
    }));
  };

  const handleSave = async () => {
    try {
      await onConfigUpdate(localConfig);
    } catch (error) {
      console.error('Failed to save configuration:', error);
    }
  };

  const handleReset = () => {
    setLocalConfig({
      aws: {
        access_key_id: '',
        secret_access_key: '',
        region: 'us-east-1',
        bedrock_model_id: 'anthropic.claude-3-5-sonnet-20240620-v1:0'
      },
      github: {
        token: '',
        default_repo: ''
      },
      preferences: {
        auto_enhance: false,
        include_file_content: true,
        max_file_size: 100,
        editor_theme: 'dark'
      }
    });
  };

  return (
    <div className="h-full overflow-auto p-6 bg-vibe-dark">
      <div className="max-w-4xl mx-auto space-y-8">
        {/* Header */}
        <div className="border-b border-vibe-gray-dark pb-4">
          <h2 className="text-2xl font-semibold text-vibe-gray mb-2">Configuration</h2>
          <p className="text-sm text-vibe-gray opacity-75">
            Configure your AWS Bedrock and GitHub settings for the Vibe Assistant
          </p>
        </div>

        {/* AWS Configuration */}
        <div className="panel p-6">
          <div className="flex items-center justify-between mb-6">
            <h3 className="text-lg font-medium text-vibe-gray flex items-center space-x-2">
              <span>☁️</span>
              <span>AWS Bedrock Configuration</span>
            </h3>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div>
              <label className="block text-sm font-medium text-vibe-gray mb-2">
                Access Key ID
              </label>
              <input
                type="text"
                value={localConfig.aws.access_key_id}
                onChange={(e) => handleInputChange('aws', 'access_key_id', e.target.value)}
                className="input-primary w-full"
                placeholder="AKIA..."
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-vibe-gray mb-2">
                Secret Access Key
              </label>
              <div className="relative">
                <input
                  type={showSecrets.aws_secret ? 'text' : 'password'}
                  value={localConfig.aws.secret_access_key}
                  onChange={(e) => handleInputChange('aws', 'secret_access_key', e.target.value)}
                  className="input-primary w-full pr-10"
                  placeholder="Enter secret key..."
                />
                <button
                  type="button"
                  onClick={() => setShowSecrets(prev => ({ ...prev, aws_secret: !prev.aws_secret }))}
                  className="absolute right-3 top-3 text-vibe-gray hover:text-vibe-blue"
                >
                  {showSecrets.aws_secret ? '🙈' : '👁️'}
                </button>
              </div>
            </div>

            <div>
              <label className="block text-sm font-medium text-vibe-gray mb-2">
                AWS Region
              </label>
              <select
                value={localConfig.aws.region}
                onChange={(e) => handleInputChange('aws', 'region', e.target.value)}
                className="input-primary w-full"
              >
                <option value="us-east-1">US East (N. Virginia)</option>
                <option value="us-west-2">US West (Oregon)</option>
                <option value="eu-west-1">Europe (Ireland)</option>
                <option value="ap-southeast-1">Asia Pacific (Singapore)</option>
                <option value="ap-northeast-1">Asia Pacific (Tokyo)</option>
              </select>
            </div>

            <div>
              <label className="block text-sm font-medium text-vibe-gray mb-2">
                Bedrock Model ID
              </label>
              <input
                type="text"
                value={localConfig.aws.bedrock_model_id}
                onChange={(e) => handleInputChange('aws', 'bedrock_model_id', e.target.value)}
                className="input-primary w-full"
                placeholder="anthropic.claude-3-5-sonnet-20240620-v1:0"
              />
              <p className="text-xs text-vibe-gray opacity-60 mt-1">
                Enter the exact Bedrock model ID (e.g., anthropic.claude-3-5-sonnet-20240620-v1:0)
              </p>
            </div>
          </div>
        </div>

        {/* GitHub Configuration */}
        <div className="panel p-6">
          <div className="flex items-center justify-between mb-6">
            <h3 className="text-lg font-medium text-vibe-gray flex items-center space-x-2">
              <span>🐙</span>
              <span>GitHub Configuration</span>
            </h3>
          </div>

          <div className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-vibe-gray mb-2">
                Personal Access Token (Optional)
              </label>
              <div className="relative">
                <input
                  type={showSecrets.github_token ? 'text' : 'password'}
                  value={localConfig.github.token}
                  onChange={(e) => handleInputChange('github', 'token', e.target.value)}
                  className="input-primary w-full pr-10"
                  placeholder="ghp_..."
                />
                <button
                  type="button"
                  onClick={() => setShowSecrets(prev => ({ ...prev, github_token: !prev.github_token }))}
                  className="absolute right-3 top-3 text-vibe-gray hover:text-vibe-blue"
                >
                  {showSecrets.github_token ? '🙈' : '👁️'}
                </button>
              </div>
              <p className="text-xs text-vibe-gray opacity-60 mt-1">
                Required for private repositories. Generate at GitHub Settings → Developer settings → Personal access tokens
              </p>
            </div>

            <div>
              <label className="block text-sm font-medium text-vibe-gray mb-2">
                Default Repository
              </label>
              <input
                type="text"
                value={localConfig.github.default_repo}
                onChange={(e) => handleInputChange('github', 'default_repo', e.target.value)}
                className="input-primary w-full"
                placeholder="owner/repository or https://github.com/owner/repository"
              />
              <p className="text-xs text-vibe-gray opacity-60 mt-1">
                Default repository for analysis (e.g., facebook/react or https://github.com/facebook/react)
              </p>
            </div>
          </div>
        </div>

        {/* Preferences */}
        <div className="panel p-6">
          <h3 className="text-lg font-medium text-vibe-gray mb-6 flex items-center space-x-2">
            <span>⚙️</span>
            <span>Preferences</span>
          </h3>

          <div className="space-y-4">
            <div className="flex items-center justify-between">
              <div>
                <label className="text-sm font-medium text-vibe-gray">Auto-enhance prompts</label>
                <p className="text-xs text-vibe-gray opacity-60">Automatically enhance prompts when submitted</p>
              </div>
              <input
                type="checkbox"
                checked={localConfig.preferences.auto_enhance}
                onChange={(e) => handleInputChange('preferences', 'auto_enhance', e.target.checked)}
                className="toggle"
              />
            </div>

            <div className="flex items-center justify-between">
              <div>
                <label className="text-sm font-medium text-vibe-gray">Include file content</label>
                <p className="text-xs text-vibe-gray opacity-60">Include actual file content in prompts</p>
              </div>
              <input
                type="checkbox"
                checked={localConfig.preferences.include_file_content}
                onChange={(e) => handleInputChange('preferences', 'include_file_content', e.target.checked)}
                className="toggle"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-vibe-gray mb-2">
                Max file size (KB)
              </label>
              <input
                type="number"
                value={localConfig.preferences.max_file_size}
                onChange={(e) => handleInputChange('preferences', 'max_file_size', parseInt(e.target.value))}
                className="input-primary w-32"
                min="1"
                max="1000"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-vibe-gray mb-2">
                Editor theme
              </label>
              <select
                value={localConfig.preferences.editor_theme}
                onChange={(e) => handleInputChange('preferences', 'editor_theme', e.target.value)}
                className="input-primary w-48"
              >
                <option value="dark">Dark</option>
                <option value="light">Light</option>
                <option value="auto">Auto</option>
              </select>
            </div>
          </div>
        </div>

        {/* Action Buttons */}
        <div className="flex justify-between items-center pt-6 border-t border-vibe-gray-dark">
          <button
            onClick={handleReset}
            className="btn-secondary"
          >
            🔄 Reset to Defaults
          </button>
          
          <div className="space-x-4">
            <button
              onClick={handleSave}
              className="btn-primary"
            >
              💾 Save Configuration
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};

export default ConfigPanel; 