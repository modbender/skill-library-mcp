import { getPicqerConfig } from '../env.js';

export class PicqerAPI {
  private async apiRequest(path: string, searchParams?: Record<string, string>) {
    const { subdomain, apiKey } = getPicqerConfig();
    const url = new URL(`https://${subdomain}.picqer.com/api/v1${path}`);
    
    if (searchParams) {
      Object.entries(searchParams).forEach(([k, v]) => {
        if (v) url.searchParams.set(k, v);
      });
    }

    const res = await fetch(url.toString(), {
      headers: {
        'Authorization': `Basic ${Buffer.from(`${apiKey}:`).toString('base64')}`,
        'User-Agent': 'FutureFulfillment-Dashboard (internal)'
      }
    });

    if (!res.ok) {
      throw new Error(`Picqer API ${path} failed: ${res.status} ${res.statusText}`);
    }
    return res.json();
  }

  // Picklists
  async getPicklists(params?: { status?: 'open' | 'closed'; dateFrom?: string; dateTo?: string; picker?: string }) {
    const searchParams: Record<string, string> = {};
    if (params?.status) searchParams.status = params.status;
    if (params?.dateFrom) searchParams.datefrom = params.dateFrom;
    if (params?.dateTo) searchParams.dateto = params.dateTo;
    
    const data = await this.apiRequest('/picklists', searchParams);
    
    // Client-side filter for picker if specified
    if (params?.picker && Array.isArray(data)) {
      return data.filter((pl: any) => 
        (pl.assigned_to || '').toLowerCase().includes(params.picker!.toLowerCase())
      );
    }
    return data;
  }

  // Stock movements
  async getStockMovements(params?: { dateFrom?: string; dateTo?: string; client?: string }) {
    const searchParams: Record<string, string> = {};
    if (params?.dateFrom) searchParams.datefrom = params.dateFrom;
    if (params?.dateTo) searchParams.dateto = params.dateTo;
    
    const data = await this.apiRequest('/stock_movements', searchParams);
    
    // Client-side filter for client if specified
    if (params?.client && Array.isArray(data)) {
      return data.filter((sm: any) => 
        (sm.client_name || '').toLowerCase().includes(params.client!.toLowerCase())
      );
    }
    return data;
  }

  // Orders (for revenue)
  async getOrders(params?: { dateFrom?: string; dateTo?: string; client?: string }) {
    const searchParams: Record<string, string> = {};
    if (params?.dateFrom) searchParams.datefrom = params.dateFrom;
    if (params?.dateTo) searchParams.dateto = params.dateTo;
    
    const data = await this.apiRequest('/orders', searchParams);
    
    if (params?.client && Array.isArray(data)) {
      return data.filter((o: any) => 
        (o.customer_name || '').toLowerCase().includes(params.client!.toLowerCase())
      );
    }
    return data;
  }

  // Clients
  async getClients() {
    return this.apiRequest('/customers');
  }

  // Products (for value calculations)
    async getProducts() {
    return this.apiRequest('/products');
  }
}
