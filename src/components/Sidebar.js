import React, { useState } from 'react';
import FileTree from './FileTree';
import RepositoryLoader from './RepositoryLoader';

const Sidebar = ({
  activeView,
  onViewChange,
  repositoryData,
  selectedFiles,
  onFileSelect,
  onRepositoryLoad,
  config
}) => {
  const [sidebarTab, setSidebarTab] = useState('files');

  const views = [
    { id: 'builder', label: 'Prompt Builder', icon: '✨' },
    { id: 'requirements', label: 'Requirements', icon: '📋' },
    { id: 'config', label: 'Configuration', icon: '⚙️' },
  ];

  const sidebarTabs = [
    { id: 'files', label: 'Files', icon: '📁' },
    { id: 'selected', label: 'Selected', icon: '✓' },
  ];

  // Helper function to get files array from repository data
  const getFilesArray = () => {
    if (!repositoryData) return [];
    
    // Handle different possible data structures
    if (repositoryData.files?.tree) {
      return repositoryData.files.tree;
    }
    if (repositoryData.tree) {
      return repositoryData.tree;
    }
    if (repositoryData.files && Array.isArray(repositoryData.files)) {
      return repositoryData.files;
    }
    
    return [];
  };

  const renderFileContent = () => {
    switch (sidebarTab) {
      case 'files':
        return (
          <div className="flex-1 overflow-auto">
            <RepositoryLoader
              onRepositoryLoad={onRepositoryLoad}
              config={config}
            />
            {repositoryData && (
              <FileTree
                files={getFilesArray()}
                selectedFiles={selectedFiles}
                onFileSelect={onFileSelect}
              />
            )}
          </div>
        );
      
      case 'selected':
        return (
          <div className="flex-1 overflow-auto p-2">
            <div className="text-small text-muted mb-2">
              Selected Files ({selectedFiles.length})
            </div>
            {selectedFiles.length === 0 ? (
              <div className="text-small text-muted p-2">
                No files selected. Click on files in the file tree to select them.
              </div>
            ) : (
              <div className="space-y-1">
                {selectedFiles.map((file, index) => (
                  <div
                    key={`${file.path}-${index}`}
                    className="file-tree-item selected"
                    onClick={() => onFileSelect(file, false)}
                  >
                    <span className="icon">📄</span>
                    <span className="flex-1 truncate" title={file.path}>
                      {file.name || file.path.split('/').pop()}
                    </span>
                    <span className="text-small text-muted">×</span>
                  </div>
                ))}
              </div>
            )}
          </div>
        );
      
      default:
        return null;
    }
  };

  // Helper function to get repository info
  const getRepositoryInfo = () => {
    if (!repositoryData) return null;
    
    if (repositoryData.files?.repository) {
      return repositoryData.files.repository;
    }
    if (repositoryData.repository) {
      return repositoryData.repository;
    }
    
    return {
      name: repositoryData.name || 'Repository',
      description: repositoryData.description || null
    };
  };

  const repoInfo = getRepositoryInfo();

  return (
    <div className="sidebar">
      {/* Navigation */}
      <div className="header">
        <span>Vibe Assistant</span>
      </div>
      
      {/* View Navigation */}
      <div className="border-b border-gray-600">
        {views.map((view) => (
          <div
            key={view.id}
            className={`file-tree-item ${activeView === view.id ? 'selected' : ''}`}
            onClick={() => onViewChange(view.id)}
          >
            <span className="icon">{view.icon}</span>
            <span>{view.label}</span>
          </div>
        ))}
      </div>

      {/* Sidebar Tabs */}
      {activeView === 'builder' && (
        <>
          <div className="tabs">
            {sidebarTabs.map((tab) => (
              <button
                key={tab.id}
                className={`tab ${sidebarTab === tab.id ? 'active' : ''}`}
                onClick={() => setSidebarTab(tab.id)}
              >
                <span className="mr-1">{tab.icon}</span>
                {tab.label}
              </button>
            ))}
          </div>

          {/* Repository Info */}
          {repoInfo && (
            <div className="p-2 border-b border-gray-600">
              <div className="text-small text-muted">Repository</div>
              <div className="text-small font-medium">
                {repoInfo.name}
              </div>
              {repoInfo.description && (
                <div className="text-small text-muted mt-1">
                  {repoInfo.description}
                </div>
              )}
              <div className="text-small text-muted mt-1">
                Files: {getFilesArray().length}
              </div>
            </div>
          )}

          {/* File Content */}
          {renderFileContent()}
        </>
      )}

      {/* Configuration/Requirements specific sidebar content */}
      {(activeView === 'config' || activeView === 'requirements') && (
        <div className="p-2 text-small text-muted">
          <div className="mb-2">
            {activeView === 'config' && 'Configure your GitHub and AWS settings here.'}
            {activeView === 'requirements' && 'Manage non-functional requirements for different task types.'}
          </div>
        </div>
      )}
    </div>
  );
};

export default Sidebar; 