import React, { useState } from 'react';
import { ApiService } from '../services/ApiService';

const RepositoryLoader = ({ onRepositoryLoad, config }) => {
  const [repoUrl, setRepoUrl] = useState('');
  const [githubToken, setGithubToken] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [showTokenInput, setShowTokenInput] = useState(false);

  // Get token from config if available
  React.useEffect(() => {
    if (config?.github?.token) {
      setGithubToken(config.github.token);
    }
  }, [config]);

  const handleLoad = async () => {
    if (!repoUrl.trim()) {
      setError('Repository URL is required');
      return;
    }

    if (!ApiService.validateGitHubUrl(repoUrl.trim())) {
      setError('Please enter a valid GitHub repository URL (e.g., https://github.com/owner/repo or owner/repo)');
      return;
    }

    try {
      setLoading(true);
      setError(null);
      
      const tokenToUse = githubToken.trim() || config?.github?.token || null;
      await onRepositoryLoad(repoUrl.trim(), tokenToUse);
      
      // Clear the URL after successful load
      setRepoUrl('');
    } catch (err) {
      setError(err.message || 'Failed to load repository');
    } finally {
      setLoading(false);
    }
  };

  const handleKeyPress = (e) => {
    if (e.key === 'Enter' && !loading) {
      handleLoad();
    }
  };

  return (
    <div className="p-2 border-b border-gray-600">
      <div className="form-group">
        <label className="text-small font-medium">Repository URL</label>
        <input
          type="text"
          className="input"
          placeholder="https://github.com/owner/repo or owner/repo"
          value={repoUrl}
          onChange={(e) => setRepoUrl(e.target.value)}
          onKeyPress={handleKeyPress}
          disabled={loading}
        />
      </div>

      {/* GitHub Token Input (optional) */}
      <div className="form-group">
        <div className="flex items-center justify-between">
          <label className="text-small font-medium">GitHub Token</label>
          <button
            className="btn-secondary btn-small"
            onClick={() => setShowTokenInput(!showTokenInput)}
            type="button"
          >
            {showTokenInput ? 'Hide' : 'Show'}
          </button>
        </div>
        
        {showTokenInput && (
          <div>
            <input
              type="password"
              className="input"
              placeholder="GitHub Personal Access Token (optional)"
              value={githubToken}
              onChange={(e) => setGithubToken(e.target.value)}
              disabled={loading}
            />
            <div className="text-small text-muted mt-1">
              Optional. Required for private repositories or to avoid rate limits.
            </div>
          </div>
        )}
        
        {config?.github?.token && !showTokenInput && (
          <div className="text-small text-muted">
            Using token from configuration
          </div>
        )}
      </div>

      <button
        className="btn"
        onClick={handleLoad}
        disabled={loading || !repoUrl.trim()}
      >
        {loading ? (
          <>
            <span className="loading-spinner mr-1"></span>
            Loading...
          </>
        ) : (
          'Load Repository'
        )}
      </button>

      {error && (
        <div className="error-message mt-2">
          {error}
        </div>
      )}

      <div className="text-small text-muted mt-2">
        <div className="mb-1">Supported formats:</div>
        <div>• https://github.com/owner/repo</div>
        <div>• owner/repo</div>
      </div>
    </div>
  );
};

export default RepositoryLoader; 