/**
 * Analytics Engine
 * 
 * Cross-platform analytics aggregation and optimization engine.
 * Pulls data from Postiz, analyzes performance, and auto-implements improvements.
 */

const fs = require('fs');
const path = require('path');
const { execSync } = require('child_process');

class AnalyticsEngine {
  constructor(config) {
    this.config = config;
    this.postiz = config.postiz || {};
    // Prefer env var over config file for API key
    this.postiz.apiKey = process.env.POSTIZ_API_KEY || this.postiz.apiKey;
    this.revenuecat = config.revenuecat;
  }

  /**
   * Escape a string for safe use in shell arguments.
   * @private
   */
  _shellEscape(str) {
    if (typeof str !== 'string') str = String(str);
    return "'" + str.replace(/'/g, "'\\''") + "'";
  }

  /**
   * Generate comprehensive analytics report
   * 
   * @param {string} accountDir - Account directory path
   * @param {Object} options - Report options
   * @returns {Promise<Object>} Analytics report with actionable insights
   */
  async generateReport(accountDir, options = {}) {
    const {
      days = 7,
      autoImplement = false,
      includeRevenue = false
    } = options;

    console.log(`📊 Generating ${days}-day analytics report...`);

    // Collect data from multiple sources
    const [
      postMetrics,
      platformMetrics,
      revenueMetrics,
      hookPerformance
    ] = await Promise.all([
      this._getPostMetrics(days),
      this._getPlatformMetrics(days),
      includeRevenue ? this._getRevenueMetrics(days) : null,
      this._analyzeHookPerformance(accountDir, days)
    ]);

    // Generate insights and recommendations
    const insights = this._generateInsights({
      posts: postMetrics,
      platform: platformMetrics,
      revenue: revenueMetrics,
      hooks: hookPerformance
    });

    // Auto-implement improvements if enabled
    if (autoImplement && insights.actions.length > 0) {
      console.log('🔧 Auto-implementing improvements...');
      await this._implementActions(accountDir, insights.actions);
    }

    // Save report
    const reportPath = this._saveReport(accountDir, {
      period: { days, startDate: this._getDateDaysAgo(days) },
      metrics: { posts: postMetrics, platform: platformMetrics, revenue: revenueMetrics },
      insights,
      timestamp: new Date().toISOString()
    });

    return {
      insights,
      metrics: { posts: postMetrics, platform: platformMetrics, revenue: revenueMetrics },
      reportPath
    };
  }

  /**
   * Get post-level metrics from Postiz
   * @private
   */
  async _getPostMetrics(days) {
    try {
      // Get recent posts
      const cmd = `POSTIZ_API_KEY=${this._shellEscape(this.postiz.apiKey)} postiz posts:list --limit 50`;
      const output = execSync(cmd, { encoding: 'utf8' });
      const posts = JSON.parse(output);

      // Filter posts from last N days
      const cutoffDate = new Date();
      cutoffDate.setDate(cutoffDate.getDate() - days);
      
      const recentPosts = posts.filter(post => 
        new Date(post.publishDate) >= cutoffDate
      );

      // Get analytics for each post
      const postsWithAnalytics = [];
      for (const post of recentPosts) {
        try {
          const analyticsCmd = `POSTIZ_API_KEY=${this._shellEscape(this.postiz.apiKey)} postiz analytics:post ${this._shellEscape(post.id)}`;
          const analyticsOutput = execSync(analyticsCmd, { encoding: 'utf8' });
          const analytics = JSON.parse(analyticsOutput);
          
          postsWithAnalytics.push({
            ...post,
            analytics: analytics.metrics || {}
          });
        } catch (error) {
          // Analytics might not be available immediately
          postsWithAnalytics.push({
            ...post,
            analytics: { views: 0, likes: 0, comments: 0, shares: 0 }
          });
        }
      }

      return this._aggregatePostMetrics(postsWithAnalytics);
      
    } catch (error) {
      console.error('Failed to fetch post metrics:', error.message);
      return { posts: [], totalViews: 0, totalEngagement: 0, avgEngagementRate: 0 };
    }
  }

  /**
   * Get platform-level metrics
   * @private
   */
  async _getPlatformMetrics(days) {
    try {
      const integrationId = this.postiz.integrationIds?.tiktok || this.postiz.integrationId;
      const cmd = `POSTIZ_API_KEY=${this._shellEscape(this.postiz.apiKey)} postiz analytics:platform ${this._shellEscape(integrationId)}`;
      const output = execSync(cmd, { encoding: 'utf8' });
      return JSON.parse(output);
    } catch (error) {
      console.error('Failed to fetch platform metrics:', error.message);
      return { followers: 0, totalViews: 0, profileViews: 0 };
    }
  }

  /**
   * Analyze hook performance patterns
   * @private
   */
  async _analyzeHookPerformance(accountDir, days) {
    const hookPerformancePath = path.join(accountDir, 'analytics', 'hook-performance.json');
    
    if (!fs.existsSync(hookPerformancePath)) {
      return { topPerformers: [], underPerformers: [], recommendations: [] };
    }

    const hookData = JSON.parse(fs.readFileSync(hookPerformancePath, 'utf8'));
    
    // Analyze patterns
    const analysis = {
      topPerformers: this._getTopPerformingHooks(hookData, 5),
      underPerformers: this._getUnderPerformingHooks(hookData, 5),
      contentTypeInsights: this._analyzeContentTypePerformance(hookData),
      recommendations: []
    };

    // Generate hook recommendations
    analysis.recommendations = this._generateHookRecommendations(analysis);

    return analysis;
  }

  /**
   * Generate actionable insights from metrics
   * @private
   */
  _generateInsights(data) {
    const insights = {
      summary: this._generateSummary(data),
      alerts: [],
      opportunities: [],
      actions: []
    };

    // Performance alerts
    if (data.posts.avgEngagementRate < 0.02) {
      insights.alerts.push({
        type: 'low_engagement',
        message: 'Engagement rate below 2% - hook optimization needed',
        severity: 'high'
      });
      
      insights.actions.push({
        type: 'hook_diversification',
        description: 'Rotate to top-performing hook patterns',
        priority: 'high'
      });
    }

    // Growth opportunities
    if (data.hooks.topPerformers?.length > 0) {
      const topHook = data.hooks.topPerformers[0];
      insights.opportunities.push({
        type: 'scale_winner',
        message: `"${topHook.pattern}" hooks averaging ${topHook.avgViews} views`,
        action: 'Create 3 variations of this hook pattern'
      });

      insights.actions.push({
        type: 'create_hook_variations',
        hookPattern: topHook.pattern,
        variations: 3,
        priority: 'medium'
      });
    }

    // Posting optimization
    if (data.posts.posts.length < 3) {
      insights.alerts.push({
        type: 'low_posting_frequency',
        message: 'Less than 3 posts this period - consistency important for growth',
        severity: 'medium'
      });
    }

    return insights;
  }

  /**
   * Auto-implement optimization actions
   * @private
   */
  async _implementActions(accountDir, actions) {
    for (const action of actions) {
      try {
        await this._executeAction(accountDir, action);
        console.log(`✅ Implemented: ${action.description || action.type}`);
      } catch (error) {
        console.error(`❌ Failed to implement ${action.type}:`, error.message);
      }
    }
  }

  /**
   * Execute a specific optimization action
   * @private
   */
  async _executeAction(accountDir, action) {
    switch (action.type) {
      case 'hook_diversification':
        await this._rotateToTopHooks(accountDir);
        break;
        
      case 'create_hook_variations':
        await this._generateHookVariations(accountDir, action.hookPattern, action.variations);
        break;
        
      case 'adjust_posting_times':
        await this._optimizePostingSchedule(accountDir, action.optimalTimes);
        break;
        
      default:
        console.log(`⚠️ Unknown action type: ${action.type}`);
    }
  }

  /**
   * Save analytics report to file
   * @private
   */
  _saveReport(accountDir, reportData) {
    const reportsDir = path.join(accountDir, 'analytics', 'reports');
    if (!fs.existsSync(reportsDir)) {
      fs.mkdirSync(reportsDir, { recursive: true });
    }
    
    const filename = `report-${new Date().toISOString().split('T')[0]}.json`;
    const reportPath = path.join(reportsDir, filename);
    
    fs.writeFileSync(reportPath, JSON.stringify(reportData, null, 2));
    
    // Also save a human-readable summary
    const summaryPath = path.join(reportsDir, `summary-${new Date().toISOString().split('T')[0]}.md`);
    fs.writeFileSync(summaryPath, this._generateMarkdownSummary(reportData));
    
    return reportPath;
  }

  /**
   * Generate human-readable markdown summary
   * @private
   */
  _generateMarkdownSummary(reportData) {
    const { period, metrics, insights } = reportData;
    
    return `# Analytics Report - ${period.startDate}

## Summary
- **Posts Published**: ${metrics.posts.posts.length}
- **Total Views**: ${metrics.posts.totalViews.toLocaleString()}
- **Avg Engagement Rate**: ${(metrics.posts.avgEngagementRate * 100).toFixed(1)}%
- **Platform Followers**: ${metrics.platform.followers?.toLocaleString() || 'N/A'}

## Alerts
${insights.alerts.map(alert => `- 🚨 **${alert.severity.toUpperCase()}**: ${alert.message}`).join('\n') || 'None'}

## Opportunities
${insights.opportunities.map(opp => `- 💡 ${opp.message}`).join('\n') || 'None'}

## Actions Taken
${insights.actions.map(action => `- ✅ ${action.description || action.type}`).join('\n') || 'None'}

---
*Generated ${new Date().toLocaleString()}*`;
  }

  // Helper methods for metric aggregation and analysis
  _aggregatePostMetrics(posts) {
    if (posts.length === 0) {
      return { posts: [], totalViews: 0, totalEngagement: 0, avgEngagementRate: 0 };
    }

    const totalViews = posts.reduce((sum, post) => sum + (post.analytics.views || 0), 0);
    const totalEngagement = posts.reduce((sum, post) => 
      sum + (post.analytics.likes || 0) + (post.analytics.comments || 0) + (post.analytics.shares || 0), 0);
    
    return {
      posts,
      totalViews,
      totalEngagement,
      avgEngagementRate: totalViews > 0 ? totalEngagement / totalViews : 0,
      avgViewsPerPost: Math.round(totalViews / posts.length)
    };
  }

  _getDateDaysAgo(days) {
    const date = new Date();
    date.setDate(date.getDate() - days);
    return date.toISOString().split('T')[0];
  }

  _generateSummary(data) {
    return {
      postsPublished: data.posts.posts.length,
      totalViews: data.posts.totalViews,
      avgEngagementRate: data.posts.avgEngagementRate,
      topPerformingHook: data.hooks.topPerformers?.[0]?.pattern || 'None identified'
    };
  }

  _getTopPerformingHooks(hookData, limit = 5) {
    return Object.entries(hookData)
      .map(([pattern, data]) => ({ pattern, ...data }))
      .sort((a, b) => b.avgViews - a.avgViews)
      .slice(0, limit);
  }

  _getUnderPerformingHooks(hookData, limit = 5) {
    return Object.entries(hookData)
      .map(([pattern, data]) => ({ pattern, ...data }))
      .sort((a, b) => a.avgViews - b.avgViews)
      .slice(0, limit);
  }
}

module.exports = AnalyticsEngine;