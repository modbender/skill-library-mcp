/**
 * WebMCP Browser Bridge
 * 
 * Questo script deve essere incluso nella pagina per abilitare
 * la comunicazione tra il browser e i modelli AI.
 * 
 * Inserisci nel tuo HTML:
 * <script src="/webmcp-bridge.js"></script>
 */

(function() {
  'use strict';

  const WEBMCP_VERSION = '1.0.0';
  const DEBUG = false;

  // ==========================================================================
  // Logging
  // ==========================================================================

  function log(...args) {
    if (DEBUG) {
      console.log('[WebMCP Bridge]', ...args);
    }
  }

  function error(...args) {
    console.error('[WebMCP Bridge]', ...args);
  }

  // ==========================================================================
  // Bridge Implementation
  // ==========================================================================

  class WebMCPBridge {
    constructor() {
      this.version = WEBMCP_VERSION;
      this.isReady = false;
      this.tools = new Map();
      this.eventListeners = new Map();
      this.sessionId = this.generateSessionId();
      
      this.init();
    }

    generateSessionId() {
      return `webmcp-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`;
    }

    init() {
      log('Initializing bridge...');
      
      // Setup message listener for cross-frame communication
      window.addEventListener('message', this.handleMessage.bind(this));
      
      // Notify parent that bridge is ready
      this.notifyReady();
      
      this.isReady = true;
      log('Bridge initialized with session:', this.sessionId);
    }

    // ========================================================================
    // Tool Registration
    // ========================================================================

    async registerTool(name, handler) {
      if (!name || typeof name !== 'string') {
        throw new Error('Tool name must be a non-empty string');
      }
      
      if (typeof handler !== 'function') {
        throw new Error('Tool handler must be a function');
      }

      this.tools.set(name, handler);
      log('Tool registered:', name);
      
      this.dispatchEvent('tool:registered', { name, timestamp: Date.now() });
      
      // Notify parent window
      this.postMessage('tool:registered', { name });
    }

    async unregisterTool(name) {
      if (this.tools.has(name)) {
        this.tools.delete(name);
        log('Tool unregistered:', name);
        
        this.dispatchEvent('tool:unregistered', { name, timestamp: Date.now() });
        this.postMessage('tool:unregistered', { name });
      }
    }

    // ========================================================================
    // Tool Execution
    // ========================================================================

    async dispatchAndWait(name, params) {
      const handler = this.tools.get(name);
      
      if (!handler) {
        throw new Error(`Tool not found: ${name}`);
      }

      const context = {
        sessionId: this.sessionId,
        timestamp: Date.now(),
        metadata: {}
      };

      log('Dispatching tool:', name, params);
      
      this.dispatchEvent('tool:invoked', { name, params, context });
      
      try {
        const result = await handler(params, context);
        
        log('Tool completed:', name, result);
        this.dispatchEvent('tool:completed', { name, result, context });
        
        return result;
      } catch (err) {
        error('Tool error:', name, err);
        this.dispatchEvent('tool:error', { 
          name, 
          error: err.message || 'Unknown error',
          context 
        });
        throw err;
      }
    }

    // ========================================================================
    // Event System
    // ========================================================================

    on(event, callback) {
      if (!this.eventListeners.has(event)) {
        this.eventListeners.set(event, new Set());
      }
      this.eventListeners.get(event).add(callback);
    }

    off(event, callback) {
      const listeners = this.eventListeners.get(event);
      if (listeners) {
        listeners.delete(callback);
      }
    }

    dispatchEvent(event, data) {
      const listeners = this.eventListeners.get(event);
      if (listeners) {
        listeners.forEach(callback => {
          try {
            callback(data);
          } catch (err) {
            error('Error in event listener:', err);
          }
        });
      }
      
      // Dispatch DOM event
      window.dispatchEvent(new CustomEvent(`webmcp:${event}`, { detail: data }));
    }

    // ========================================================================
    // Message Passing (for cross-frame communication)
    // ========================================================================

    handleMessage(event) {
      // Security: validate origin if needed
      // if (event.origin !== 'expected-origin') return;
      
      const { type, payload, id } = event.data || {};
      
      if (!type || !type.startsWith('webmcp:')) return;
      
      log('Received message:', type, payload);
      
      switch (type) {
        case 'webmcp:register-tool':
          this.handleRegisterTool(payload, id);
          break;
          
        case 'webmcp:unregister-tool':
          this.handleUnregisterTool(payload, id);
          break;
          
        case 'webmcp:dispatch':
          this.handleDispatch(payload, id, event.source);
          break;
          
        case 'webmcp:get-status':
          this.handleGetStatus(id, event.source);
          break;
      }
    }

    async handleRegisterTool({ name, handler }, id) {
      try {
        // Note: handler functions cannot be serialized across frames
        // This is a placeholder for when using same-origin frames
        await this.registerTool(name, handler);
        this.sendResponse(id, { success: true });
      } catch (err) {
        this.sendResponse(id, { success: false, error: err.message });
      }
    }

    async handleUnregisterTool({ name }, id) {
      try {
        await this.unregisterTool(name);
        this.sendResponse(id, { success: true });
      } catch (err) {
        this.sendResponse(id, { success: false, error: err.message });
      }
    }

    async handleDispatch({ name, params }, id, source) {
      try {
        const result = await this.dispatchAndWait(name, params);
        this.sendResponse(id, { success: true, result }, source);
      } catch (err) {
        this.sendResponse(id, { 
          success: false, 
          error: err.message || 'Unknown error' 
        }, source);
      }
    }

    handleGetStatus(id, source) {
      this.sendResponse(id, {
        version: this.version,
        isReady: this.isReady,
        sessionId: this.sessionId,
        toolCount: this.tools.size,
        tools: Array.from(this.tools.keys())
      }, source);
    }

    postMessage(type, payload) {
      if (window.parent !== window) {
        window.parent.postMessage({ type: `webmcp:${type}`, payload }, '*');
      }
    }

    sendResponse(id, data, target = window.parent) {
      if (target && target !== window) {
        target.postMessage({ type: 'webmcp:response', id, ...data }, '*');
      }
    }

    notifyReady() {
      this.postMessage('ready', {
        version: this.version,
        sessionId: this.sessionId
      });
    }

    // ========================================================================
    // Utility Methods
    // ========================================================================

    getStatus() {
      return {
        version: this.version,
        isReady: this.isReady,
        sessionId: this.sessionId,
        toolCount: this.tools.size,
        tools: Array.from(this.tools.keys())
      };
    }

    isToolRegistered(name) {
      return this.tools.has(name);
    }

    clearTools() {
      this.tools.clear();
      this.dispatchEvent('tools:cleared', { timestamp: Date.now() });
    }
  }

  // ==========================================================================
  // Setup Model Context on navigator
  // ==========================================================================

  function setupModelContext(bridge) {
    if (!navigator.modelContext) {
      navigator.modelContext = {
        async registerTool(name, handler) {
          return bridge.registerTool(name, handler);
        },
        
        async unregisterTool(name) {
          return bridge.unregisterTool(name);
        },
        
        async dispatchAndWait(name, params) {
          return bridge.dispatchAndWait(name, params);
        },
        
        on(event, callback) {
          bridge.on(event, callback);
        },
        
        off(event, callback) {
          bridge.off(event, callback);
        }
      };
      
      log('navigator.modelContext initialized');
    }
  }

  // ==========================================================================
  // Initialize
  // ==========================================================================

  function init() {
    if (window.webMCP) {
      log('WebMCP already initialized');
      return;
    }

    const bridge = new WebMCPBridge();
    
    // Expose on window
    window.webMCP = bridge;
    
    // Setup navigator.modelContext
    setupModelContext(bridge);
    
    // Dispatch ready event
    window.dispatchEvent(new CustomEvent('webmcp:ready', {
      detail: bridge.getStatus()
    }));
  }

  // Run initialization
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else {
    init();
  }

})();
