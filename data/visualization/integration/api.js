// REST API Integration
const express = require('express');
const rateLimit = require('express-rate-limit');

class VisualizationAPI {
  constructor() {
    this.app = express();
    this.setupMiddleware();
    this.setupRoutes();
  }

  setupMiddleware() {
    // Rate limiting
    const limiter = rateLimit({
      windowMs: 15 * 60 * 1000, // 15 minutes
      max: 100, // limit each IP to 100 requests per windowMs
      message: 'Too many requests from this IP, please try again later.'
    });
    
    this.app.use(limiter);
    this.app.use(express.json({ limit: '10mb' }));
    
    // API key authentication
    this.app.use(this.authenticateAPIKey);
  }

  authenticateAPIKey(req, res, next) {
    const apiKey = req.headers['x-api-key'] || req.query.api_key;
    
    if (!apiKey) {
      return res.status(401).json({ error: 'API key required' });
    }
    
    // In real implementation, this would validate against a database
    if (this.isValidAPIKey(apiKey)) {
      req.apiKey = apiKey;
      next();
    } else {
      return res.status(403).json({ error: 'Invalid API key' });
    }
  }

  isValidAPIKey(apiKey) {
    // Placeholder validation - in real implementation would check against stored keys
    return apiKey.startsWith('viz_') && apiKey.length > 20;
  }

  setupRoutes() {
    // Health check
    this.app.get('/health', (req, res) => {
      res.json({ status: 'ok', version: '1.1.0' });
    });

    // Generate visualization
    this.app.post('/generate', async (req, res) => {
      try {
        const { template, parameters, format = 'png' } = req.body;
        
        if (!template || !parameters) {
          return res.status(400).json({ error: 'Template and parameters are required' });
        }
        
        // Generate visualization (would call main visualization logic)
        const result = await this.generateVisualization({
          template,
          parameters,
          format,
          apiKey: req.apiKey
        });
        
        res.json({
          success: true,
          result: result,
          requestId: this.generateRequestId()
        });
      } catch (error) {
        console.error('API error:', error);
        res.status(500).json({ error: 'Failed to generate visualization' });
      }
    });

    // Get template list
    this.app.get('/templates', (req, res) => {
      const templates = [
        { id: 'stock', name: 'Stock Technical Analysis' },
        { id: 'portfolio', name: 'Portfolio Dashboard' },
        { id: 'industry', name: 'Industry Comparison' },
        { id: 'macro', name: 'Macroeconomic Analysis' },
        { id: 'crypto', name: 'Cryptocurrency Analysis' }
      ];
      res.json({ templates });
    });

    // Save user preferences
    this.app.post('/preferences', (req, res) => {
      try {
        const { userId, preferences } = req.body;
        // Save preferences (would use proper storage)
        res.json({ success: true, message: 'Preferences saved' });
      } catch (error) {
        res.status(500).json({ error: 'Failed to save preferences' });
      }
    });
  }

  async generateVisualization(context) {
    // This would integrate with the main visualization logic
    // For now, return mock success
    return {
      url: `https://api.visualization.ai/results/${Date.now()}.png`,
      format: context.format,
      template: context.template
    };
  }

  generateRequestId() {
    return 'req_' + Date.now() + '_' + Math.random().toString(36).substr(2, 9);
  }

  start(port = 3000) {
    this.server = this.app.listen(port, () => {
      console.log(`Visualization API server running on port ${port}`);
    });
    return this.server;
  }

  stop() {
    if (this.server) {
      this.server.close();
    }
  }
}

module.exports = VisualizationAPI;