import React, { useState, useEffect, useCallback } from 'react';
import { ApiService } from '../services/ApiService';

const RepositorySelector = ({ onFilesSelected, config }) => {
  const [repoUrl, setRepoUrl] = useState('');
  const [files, setFiles] = useState([]);
  const [selectedFiles, setSelectedFiles] = useState([]);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState('');
  const [expandedFolders, setExpandedFolders] = useState(new Set());

  const loadRepositoryFiles = useCallback(async () => {
    if (!repoUrl.trim()) return;

    setIsLoading(true);
    setError('');
    
    try {
      const response = await ApiService.getRepositoryFiles(repoUrl, config);
      setFiles(response.files || []);
    } catch (err) {
      setError(err.message || 'Failed to load repository files');
      setFiles([]);
    } finally {
      setIsLoading(false);
    }
  }, [repoUrl, config]);

  useEffect(() => {
    const timeoutId = setTimeout(() => {
      if (repoUrl.trim()) {
        loadRepositoryFiles();
      }
    }, 500);

    return () => clearTimeout(timeoutId);
  }, [loadRepositoryFiles]);

  const handleFileToggle = (file) => {
    const isSelected = selectedFiles.some(f => f.path === file.path);
    let newSelection;
    
    if (isSelected) {
      newSelection = selectedFiles.filter(f => f.path !== file.path);
    } else {
      newSelection = [...selectedFiles, file];
    }
    
    setSelectedFiles(newSelection);
    onFilesSelected(newSelection);
  };

  const toggleFolder = (folderPath) => {
    const newExpanded = new Set(expandedFolders);
    if (newExpanded.has(folderPath)) {
      newExpanded.delete(folderPath);
    } else {
      newExpanded.add(folderPath);
    }
    setExpandedFolders(newExpanded);
  };

  const organizeFiles = (files) => {
    const organized = {};
    
    files.forEach(file => {
      const parts = file.path.split('/');
      let current = organized;
      
      for (let i = 0; i < parts.length - 1; i++) {
        const part = parts[i];
        if (!current[part]) {
          current[part] = { type: 'folder', children: {} };
        }
        current = current[part].children;
      }
      
      const fileName = parts[parts.length - 1];
      current[fileName] = { type: 'file', data: file };
    });
    
    return organized;
  };

  const renderFileTree = (items, path = '') => {
    return Object.entries(items).map(([name, item]) => {
      const currentPath = path ? `${path}/${name}` : name;
      
      if (item.type === 'folder') {
        const isExpanded = expandedFolders.has(currentPath);
        return (
          <div key={currentPath} className="ml-4">
            <div
              className="flex items-center py-1 px-2 hover:bg-vibe-darker rounded cursor-pointer"
              onClick={() => toggleFolder(currentPath)}
            >
              <span className="mr-2 text-vibe-blue">
                {isExpanded ? '📂' : '📁'}
              </span>
              <span className="text-vibe-gray text-sm">{name}</span>
            </div>
            {isExpanded && (
              <div className="ml-4">
                {renderFileTree(item.children, currentPath)}
              </div>
            )}
          </div>
        );
      } else {
        const isSelected = selectedFiles.some(f => f.path === item.data.path);
        return (
          <div
            key={currentPath}
            className={`flex items-center py-1 px-2 ml-4 hover:bg-vibe-darker rounded cursor-pointer ${
              isSelected ? 'bg-vibe-blue bg-opacity-20' : ''
            }`}
            onClick={() => handleFileToggle(item.data)}
          >
            <input
              type="checkbox"
              checked={isSelected}
              onChange={() => {}}
              className="mr-2 accent-vibe-blue"
            />
            <span className="mr-2">📄</span>
            <span className="text-vibe-gray text-sm">{name}</span>
            <span className="ml-auto text-xs text-vibe-gray opacity-60">
              {(item.data.size / 1024).toFixed(1)}KB
            </span>
          </div>
        );
      }
    });
  };

  const organizedFiles = organizeFiles(files);

  return (
    <div className="space-y-4">
      <div>
        <label className="block text-sm font-medium text-vibe-gray mb-2">
          Repository URL
        </label>
        <input
          type="text"
          value={repoUrl}
          onChange={(e) => setRepoUrl(e.target.value)}
          placeholder="https://github.com/username/repository"
          className="input-primary w-full"
        />
        {error && (
          <p className="text-vibe-red text-sm mt-1">{error}</p>
        )}
      </div>

      {isLoading && (
        <div className="flex items-center justify-center py-8">
          <div className="animate-spin w-6 h-6 border border-vibe-blue border-t-transparent rounded-full"></div>
          <span className="ml-2 text-vibe-gray">Loading repository files...</span>
        </div>
      )}

      {files.length > 0 && (
        <div>
          <div className="flex items-center justify-between mb-2">
            <h4 className="text-sm font-medium text-vibe-gray">
              Repository Files ({files.length})
            </h4>
            <span className="text-xs text-vibe-gray">
              {selectedFiles.length} selected
            </span>
          </div>
          
          <div className="max-h-64 overflow-y-auto border border-vibe-gray-dark rounded-lg bg-vibe-darkest p-2">
            {renderFileTree(organizedFiles)}
          </div>
          
          {selectedFiles.length > 0 && (
            <div className="mt-2 p-2 bg-vibe-darker rounded border border-vibe-gray-dark">
              <p className="text-xs text-vibe-gray mb-1">Selected files:</p>
              <div className="flex flex-wrap gap-1">
                {selectedFiles.map(file => (
                  <span
                    key={file.path}
                    className="inline-flex items-center px-2 py-1 bg-vibe-blue bg-opacity-20 text-vibe-blue text-xs rounded"
                  >
                    {file.path.split('/').pop()}
                    <button
                      onClick={() => handleFileToggle(file)}
                      className="ml-1 hover:text-vibe-red"
                    >
                      ×
                    </button>
                  </span>
                ))}
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  );
};

export default RepositorySelector; 