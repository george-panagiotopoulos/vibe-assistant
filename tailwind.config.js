/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    "./src/**/*.{js,jsx,ts,tsx}",
    "./public/index.html"
  ],
  theme: {
    extend: {
      colors: {
        'vibe': {
          'dark': '#1e1e1e',
          'darker': '#252526',
          'darkest': '#1a1a1a',
          'blue': '#007acc',
          'blue-hover': '#005a9e',
          'gray': '#cccccc',
          'gray-dark': '#3c3c3c',
          'gray-light': '#e8e8e8',
          'green': '#4caf50',
          'red': '#f44336',
          'orange': '#ff9800',
          'purple': '#9c27b0'
        }
      },
      fontFamily: {
        'mono': ['Monaco', 'Menlo', 'Ubuntu Mono', 'monospace']
      },
      spacing: {
        '320': '320px',
        '28': '28px',
        '40': '40px'
      }
    },
  },
  plugins: [],
  darkMode: 'class'
} 