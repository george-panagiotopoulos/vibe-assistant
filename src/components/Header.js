import React from 'react';

const Header = ({ currentView, onViewChange }) => {
  const views = [
    { id: 'builder', name: 'Prompt Builder', icon: '🔧' },
    { id: 'config', name: 'Configuration', icon: '⚙️' },
    { id: 'requirements', name: 'Requirements', icon: '📋' },
    { id: 'streaming', name: 'Streaming Test', icon: '🚀' }
  ];

  return (
    <header className="bg-vibe-darker border-b border-vibe-gray-dark px-4 py-2">
      <div className="flex items-center justify-between">
        <div className="flex items-center space-x-4">
          <h1 className="text-xl font-bold text-vibe-gray flex items-center">
            <span className="mr-2">🎯</span>
            Vibe Assistant
          </h1>
          
          <nav className="flex space-x-1">
            {views.map(view => (
              <button
                key={view.id}
                onClick={() => onViewChange(view.id)}
                className={`px-3 py-1 rounded text-sm transition-colors ${
                  currentView === view.id
                    ? 'bg-vibe-blue text-white'
                    : 'text-vibe-gray hover:bg-vibe-gray-dark'
                }`}
              >
                <span className="mr-1">{view.icon}</span>
                {view.name}
              </button>
            ))}
          </nav>
        </div>
        
        <div className="flex items-center space-x-2 text-sm text-vibe-gray">
          <span className="opacity-60">v1.0.0</span>
        </div>
      </div>
    </header>
  );
};

export default Header; 