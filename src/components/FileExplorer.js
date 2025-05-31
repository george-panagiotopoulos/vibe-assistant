import React, { useState, useEffect, useCallback } from 'react';
import { ApiService } from '../services/ApiService';

const FileExplorer = ({ repositoryPath, selectedFiles, onFileSelect, onFileDeselect, onSelectionChange }) => {
  const [files, setFiles] = useState([]);
  const [expandedDirs, setExpandedDirs] = useState(new Set());
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [searchQuery, setSearchQuery] = useState('');
  const [filteredFiles, setFilteredFiles] = useState([]);

  // Load repository files
  const loadFiles = useCallback(async () => {
    if (!repositoryPath) return;

    setLoading(true);
    setError(null);
    try {
      const response = await ApiService.getRepositoryFiles(repositoryPath);
      setFiles(response.files || []);
    } catch (err) {
      setError(`Failed to load files: ${err.message}`);
      setFiles([]);
    } finally {
      setLoading(false);
    }
  }, [repositoryPath]);

  useEffect(() => {
    loadFiles();
  }, [loadFiles]);

  // Filter files based on search query
  useEffect(() => {
    if (!searchQuery.trim()) {
      setFilteredFiles(files);
      return;
    }

    const query = searchQuery.toLowerCase();
    const filtered = files.filter(file => 
      file.name.toLowerCase().includes(query) || 
      file.path.toLowerCase().includes(query)
    );
    setFilteredFiles(filtered);
  }, [files, searchQuery]);

  const toggleDirectory = (dirPath) => {
    const newExpanded = new Set(expandedDirs);
    if (newExpanded.has(dirPath)) {
      newExpanded.delete(dirPath);
    } else {
      newExpanded.add(dirPath);
    }
    setExpandedDirs(newExpanded);
  };

  const isFileSelected = (file) => {
    return selectedFiles.some(selected => selected.path === file.path);
  };

  const handleFileClick = (file) => {
    if (file.type === 'directory') {
      toggleDirectory(file.path);
      return;
    }

    if (isFileSelected(file)) {
      onFileDeselect(file);
    } else {
      onFileSelect(file);
    }
  };

  const getFileIcon = (file) => {
    if (file.type === 'directory') {
      return expandedDirs.has(file.path) ? '📂' : '📁';
    }
    return ApiService.getFileIcon(file.name);
  };

  const buildFileTree = (files) => {
    const tree = {};
    
    files.forEach(file => {
      const parts = file.path.split('/');
      let current = tree;
      
      for (let i = 0; i < parts.length; i++) {
        const part = parts[i];
        if (!current[part]) {
          current[part] = {
            name: part,
            path: parts.slice(0, i + 1).join('/'),
            type: i === parts.length - 1 ? file.type : 'directory',
            size: file.size,
            children: {}
          };
        }
        current = current[part].children;
      }
    });

    return tree;
  };

  const renderFileTree = (tree, depth = 0) => {
    return Object.values(tree).map(file => {
      const isSelected = isFileSelected(file);
      const isExpanded = expandedDirs.has(file.path);
      const hasChildren = Object.keys(file.children || {}).length > 0;

      return (
        <div key={file.path}>
          <div
            className={`flex items-center px-2 py-1 cursor-pointer hover:bg-vibe-gray-dark transition-colors ${
              isSelected ? 'bg-vibe-accent bg-opacity-20 border-l-2 border-vibe-accent' : ''
            }`}
            style={{ paddingLeft: `${depth * 16 + 8}px` }}
            onClick={() => handleFileClick(file)}
          >
            <span className="mr-2 text-sm">
              {getFileIcon(file)}
            </span>
            <span className={`text-sm flex-1 ${isSelected ? 'text-vibe-accent font-medium' : 'text-vibe-gray'}`}>
              {file.name}
            </span>
            {file.size && (
              <span className="text-xs text-vibe-gray opacity-60 ml-2">
                {ApiService.formatFileSize(file.size)}
              </span>
            )}
          </div>
          
          {file.type === 'directory' && isExpanded && hasChildren && (
            <div>
              {renderFileTree(file.children, depth + 1)}
            </div>
          )}
        </div>
      );
    });
  };

  const clearSelection = () => {
    selectedFiles.forEach(file => onFileDeselect(file));
  };

  const selectAll = () => {
    const fileItems = files.filter(f => f.type === 'file');
    fileItems.forEach(file => {
      if (!isFileSelected(file)) {
        onFileSelect(file);
      }
    });
  };

  if (loading) {
    return (
      <div className="h-full flex items-center justify-center bg-vibe-dark">
        <div className="text-center">
          <div className="text-2xl mb-2">🔄</div>
          <div className="text-vibe-gray">Loading files...</div>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="h-full flex items-center justify-center bg-vibe-dark p-6">
        <div className="text-center">
          <div className="text-2xl mb-2">❌</div>
          <div className="text-red-400 mb-4">{error}</div>
          <button
            onClick={loadFiles}
            className="btn-secondary"
          >
            🔄 Retry
          </button>
        </div>
      </div>
    );
  }

  const fileTree = buildFileTree(filteredFiles);

  return (
    <div className="h-full flex flex-col bg-vibe-dark">
      {/* Header */}
      <div className="p-4 border-b border-vibe-gray-dark">
        <div className="flex items-center justify-between mb-4">
          <h2 className="text-lg font-medium text-vibe-gray">File Explorer</h2>
          <div className="flex space-x-2">
            <button
              onClick={selectAll}
              className="text-xs btn-secondary"
              title="Select all files"
            >
              ✅ All
            </button>
            <button
              onClick={clearSelection}
              className="text-xs btn-secondary"
              title="Clear selection"
            >
              🗑️ Clear
            </button>
          </div>
        </div>

        {/* Search */}
        <div className="relative">
          <input
            type="text"
            placeholder="Search files..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="input-primary w-full pl-8"
          />
          <div className="absolute left-2 top-1/2 transform -translate-y-1/2 text-vibe-gray opacity-60">
            🔍
          </div>
          {searchQuery && (
            <button
              onClick={() => setSearchQuery('')}
              className="absolute right-2 top-1/2 transform -translate-y-1/2 text-vibe-gray hover:text-vibe-accent"
            >
              ✕
            </button>
          )}
        </div>

        {/* Selection info */}
        {selectedFiles.length > 0 && (
          <div className="mt-3 p-2 bg-vibe-gray-dark rounded text-sm">
            <div className="text-vibe-accent">
              📋 {selectedFiles.length} file{selectedFiles.length !== 1 ? 's' : ''} selected
            </div>
            <div className="text-xs text-vibe-gray opacity-75 mt-1">
              Total size: {ApiService.formatFileSize(
                selectedFiles.reduce((sum, file) => sum + (file.size || 0), 0)
              )}
            </div>
          </div>
        )}
      </div>

      {/* File Tree */}
      <div className="flex-1 overflow-auto">
        {Object.keys(fileTree).length === 0 ? (
          <div className="text-center p-8 text-vibe-gray opacity-60">
            {searchQuery ? (
              <>
                <div className="text-xl mb-2">🔍</div>
                <div>No files match "{searchQuery}"</div>
              </>
            ) : (
              <>
                <div className="text-xl mb-2">📁</div>
                <div>No files found</div>
              </>
            )}
          </div>
        ) : (
          <div className="p-2">
            {renderFileTree(fileTree)}
          </div>
        )}
      </div>

      {/* Footer */}
      <div className="p-3 border-t border-vibe-gray-dark bg-vibe-black">
        <div className="text-xs text-vibe-gray opacity-60 text-center">
          {filteredFiles.length} file{filteredFiles.length !== 1 ? 's' : ''}
          {searchQuery && filteredFiles.length !== files.length && ` (filtered from ${files.length})`}
        </div>
      </div>
    </div>
  );
};

export default FileExplorer; 