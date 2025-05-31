import axios from 'axios';

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:5000';
const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: 10000,
});

// Request interceptor
api.interceptors.request.use(
  (config) => {
    console.log(`Making ${config.method?.toUpperCase()} request to ${config.url}`);
    return config;
  },
  (error) => {
    console.error('Request interceptor error:', error);
    return Promise.reject(error);
  }
);

// Response interceptor
api.interceptors.response.use(
  (response) => {
    if (response.data && !response.data.success && response.data.error) {
      throw new Error(response.data.error);
    }
    return response;
  },
  (error) => {
    if (error.response?.data?.error) {
      throw new Error(error.response.data.error);
    }
    if (error.code === 'ECONNABORTED') {
      throw new Error('Request timeout - please try again');
    }
    if (error.code === 'ECONNREFUSED') {
      throw new Error('Cannot connect to server - is it running?');
    }
    throw error;
  }
);

export const ApiService = {
  // Health check
  async checkHealth() {
    const response = await api.get('/api/health');
    return response.data;
  },

  // Configuration operations
  async getConfig() {
    const response = await api.get('/api/user/config');
    return response.data.config;
  },

  async updateConfig(config) {
    const response = await api.post('/api/user/config', config);
    return response.data.config;
  },

  async loadConfig() {
    const response = await api.get('/api/config');
    return response.data;
  },

  async saveConfig(config) {
    const response = await api.post('/api/config', config);
    return response.data;
  },

  // GitHub operations
  async cloneRepository(repoUrl, branch = 'main') {
    const response = await api.post('/api/github/clone', {
      repo_url: repoUrl,
      branch: branch
    });
    return response.data;
  },

  async getRepositoryFiles(repoUrl, config = {}) {
    const response = await api.post('/api/repositories/files', {
      repo_url: repoUrl,
      github_token: config.github?.token
    });
    return response.data;
  },

  async getFileContent(repoUrl, filePath, config = {}) {
    const response = await api.post('/api/repositories/file-content', {
      repo_url: repoUrl,
      file_path: filePath,
      github_token: config.github?.token
    });
    return response.data;
  },

  // Requirements operations
  async getRequirements(taskType, config = {}) {
    const response = await api.get('/api/requirements', {
      params: { task_type: taskType }
    });
    return response.data;
  },

  async updateRequirements(taskType, requirements, config = {}) {
    const response = await api.post('/api/requirements', { 
      task_type: taskType,
      requirements 
    });
    return response.data;
  },

  // Test connections
  async testGitHubConnection(config = {}) {
    const response = await api.post('/api/github/test', { 
      github_token: config.github?.token,
      test_repo: config.github?.default_repo
    });
    return response.data;
  },

  // Bedrock operations
  async testBedrockConnection(config = {}) {
    const response = await api.post('/api/bedrock/test', {
      aws_access_key_id: config.aws?.access_key_id,
      aws_secret_access_key: config.aws?.secret_access_key,
      aws_region: config.aws?.region,
      model_id: config.aws?.bedrock_model_id
    });
    return response.data;
  },

  async chatWithAI(message, currentPrompt = '', selectedFiles = [], config = {}) {
    const response = await api.post('/api/bedrock/chat', {
      message,
      current_prompt: currentPrompt,
      selected_files: selectedFiles,
      config: {
        aws_access_key_id: config.aws?.access_key_id,
        aws_secret_access_key: config.aws?.secret_access_key,
        aws_region: config.aws?.region,
        model_id: config.aws?.bedrock_model_id
      }
    });
    return response.data;
  },

  // Prompt Builder methods
  async buildFinalPrompt(data) {
    const response = await api.post('/api/prompt/build', data);
    return response.data;
  },

  async enhancePrompt(prompt, selectedFiles = [], config = {}) {
    const response = await api.post('/api/prompt/enhance', {
      prompt,
      task_type: config.preferences?.default_task_type || 'development',
      selected_files: selectedFiles
    });
    return response.data;
  },

  // User configuration management
  async getUserConfig() {
    const response = await api.get('/api/user/config');
    return response.data;
  },

  async updateUserConfig(config) {
    const response = await api.post('/api/user/config', config);
    return response.data;
  },

  // Repository analysis
  async analyzeRepository(repoPath) {
    const response = await api.get('/api/repository/analyze', {
      params: { repo_path: repoPath }
    });
    return response.data;
  },

  // File operations
  async searchFiles(query, repoPath) {
    const response = await api.get('/api/repository/search', {
      params: { query, repo_path: repoPath }
    });
    return response.data;
  },

  async getFileMetadata(filePath) {
    const response = await api.get('/api/repository/file/metadata', {
      params: { file_path: filePath }
    });
    return response.data;
  },

  // Utility methods
  validateGitHubUrl(url) {
    const githubRegex = /^https:\/\/github\.com\/[a-zA-Z0-9_.-]+\/[a-zA-Z0-9_.-]+\/?$/;
    const shortFormRegex = /^[a-zA-Z0-9_.-]+\/[a-zA-Z0-9_.-]+$/;
    return githubRegex.test(url) || shortFormRegex.test(url);
  },

  formatFileSize(bytes) {
    if (!bytes) return '0 B';
    const k = 1024;
    const sizes = ['B', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
  },

  getFileIcon(fileName) {
    const extension = fileName.split('.').pop()?.toLowerCase();
    const iconMap = {
      js: '📄',
      jsx: '⚛️',
      ts: '📘',
      tsx: '⚛️',
      py: '🐍',
      java: '☕',
      cpp: '⚙️',
      c: '⚙️',
      css: '🎨',
      html: '🌐',
      json: '📋',
      md: '📝',
      txt: '📄',
      png: '🖼️',
      jpg: '🖼️',
      gif: '🖼️',
      svg: '🖼️'
    };
    return iconMap[extension] || '📄';
  }
};

export default ApiService; 