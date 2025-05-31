class LoggingService {
  constructor() {
    this.logs = [];
    this.maxLogs = 1000; // Keep last 1000 logs in memory
    this.setupGlobalErrorHandler();
  }

  setupGlobalErrorHandler() {
    // Capture unhandled errors
    window.addEventListener('error', (event) => {
      this.logError('unhandled_error', event.error?.message || event.message, {
        filename: event.filename,
        lineno: event.lineno,
        colno: event.colno,
        stack: event.error?.stack
      });
    });

    // Capture unhandled promise rejections
    window.addEventListener('unhandledrejection', (event) => {
      this.logError('unhandled_promise_rejection', event.reason?.message || event.reason, {
        stack: event.reason?.stack
      });
    });
  }

  log(level, message, context = {}) {
    const logEntry = {
      timestamp: new Date().toISOString(),
      level,
      message,
      context,
      url: window.location.href,
      userAgent: navigator.userAgent
    };

    this.logs.push(logEntry);
    
    // Keep only the last maxLogs entries
    if (this.logs.length > this.maxLogs) {
      this.logs = this.logs.slice(-this.maxLogs);
    }

    // Also log to console for development
    console[level] || console.log(`[${level.toUpperCase()}]`, message, context);

    // Send to backend if it's an error
    if (level === 'error') {
      this.sendLogToBackend(logEntry);
    }
  }

  logInfo(message, context = {}) {
    this.log('info', message, context);
  }

  logWarning(message, context = {}) {
    this.log('warn', message, context);
  }

  logError(type, message, context = {}) {
    this.log('error', `${type}: ${message}`, context);
  }

  logApiRequest(endpoint, method, requestData, responseData = null, error = null) {
    const logEntry = {
      type: 'api_request',
      endpoint,
      method,
      requestData,
      responseData,
      error,
      success: !error
    };

    if (error) {
      this.logError('api_request_failed', `${method} ${endpoint} failed: ${error}`, logEntry);
    } else {
      this.logInfo(`API request successful: ${method} ${endpoint}`, logEntry);
    }
  }

  async sendLogToBackend(logEntry) {
    try {
      // Send error logs to backend for persistent storage
      await fetch('/api/log-frontend-error', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(logEntry)
      });
    } catch (error) {
      // Don't log this error to avoid infinite loops
      console.error('Failed to send log to backend:', error);
    }
  }

  async downloadLogs() {
    try {
      const logsData = {
        timestamp: new Date().toISOString(),
        logs: this.logs,
        summary: {
          total_logs: this.logs.length,
          error_count: this.logs.filter(log => log.level === 'error').length,
          warning_count: this.logs.filter(log => log.level === 'warn').length,
          info_count: this.logs.filter(log => log.level === 'info').length
        }
      };

      const blob = new Blob([JSON.stringify(logsData, null, 2)], { type: 'application/json' });
      const url = URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `frontend_logs_${new Date().toISOString().split('T')[0]}.json`;
      document.body.appendChild(a);
      a.click();
      document.body.removeChild(a);
      URL.revokeObjectURL(url);
    } catch (error) {
      console.error('Failed to download logs:', error);
    }
  }

  clearLogs() {
    this.logs = [];
  }

  getLogs() {
    return [...this.logs];
  }

  getErrorLogs() {
    return this.logs.filter(log => log.level === 'error');
  }
}

// Create global instance
const loggingService = new LoggingService();

export default loggingService; 