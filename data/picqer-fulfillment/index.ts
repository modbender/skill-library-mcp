import { Skill, Context } from '@openclaw/sdk';
import { fetchDashboardData, DashboardFilters } from './tools/data-processor.js';

export default class FutureFulfillmentDashboardSkill extends Skill {
  name = 'futurefulfillment-dashboard';
  description = 'Data API for FutureFulfillment Picqer dashboard (JSON only).';

  async execute(context: Context) {
    try {
      const { command, filters } = context.input as { 
        command: string; 
        filters?: DashboardFilters;
      };

      switch (command) {
        case 'dashboard.fetch':
          return await fetchDashboardData(filters || {});

        case 'picklists.fetch':
          return (await fetchDashboardData(filters || {})).picklists;

        case 'stock.fetch':
          return (await fetchDashboardData(filters || {})).stock;

        case 'revenue.fetch':
          return (await fetchDashboardData(filters || {})).revenue;

        default:
          return { error: `Unknown command: ${command}` };
      }
    } catch (error: any) {
      return { 
        error: error.message || 'Unknown error',
        timestamp: new Date().toISOString()
      };
    }
  }
}
