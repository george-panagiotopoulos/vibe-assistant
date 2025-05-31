import React, { useState } from 'react';
import { ApiService } from '../services/ApiService';

const FileTree = ({ files, selectedFiles = [], onFileSelect }) => {
  const [expandedFolders, setExpandedFolders] = useState(new Set());

  const toggleFolder = (path) => {
    setExpandedFolders(prev => {
      const newSet = new Set(prev);
      if (newSet.has(path)) {
        newSet.delete(path);
      } else {
        newSet.add(path);
      }
      return newSet;
    });
  };

  const isFileSelected = (file) => {
    return selectedFiles.some(selected => selected.path === file.path);
  };

  const getFileIcon = (file) => {
    if (file.type === 'dir') {
      return expandedFolders.has(file.path) ? '📂' : '📁';
    }
    return ApiService.getFileIcon(file.name);
  };

  const renderFileNode = (file, depth = 0) => {
    const isFolder = file.type === 'dir';
    const isExpanded = expandedFolders.has(file.path);
    const isSelected = isFileSelected(file);
    
    return (
      <div key={file.path}>
        <div
          className={`file-tree-item ${isSelected ? 'selected' : ''} ${isFolder ? 'folder' : 'file'}`}
          style={{ paddingLeft: `${8 + depth * 16}px` }}
          onClick={() => {
            if (isFolder) {
              toggleFolder(file.path);
            } else {
              onFileSelect(file, !isSelected);
            }
          }}
          title={file.path}
        >
          <span className="icon">
            {getFileIcon(file)}
          </span>
          <span className="flex-1 truncate">
            {file.name}
          </span>
          {file.size && (
            <span className="text-small text-muted">
              {ApiService.formatFileSize(file.size)}
            </span>
          )}
          {isSelected && !isFolder && (
            <span className="text-small text-muted ml-1">✓</span>
          )}
        </div>
        
        {isFolder && isExpanded && file.children && (
          <div className="file-tree-children">
            {file.children.map(child => renderFileNode(child, depth + 1))}
          </div>
        )}
      </div>
    );
  };

  if (!files || files.length === 0) {
    return (
      <div className="p-2 text-small text-muted">
        No files to display
      </div>
    );
  }

  return (
    <div className="file-tree">
      {files.map(file => renderFileNode(file))}
    </div>
  );
};

export default FileTree; 