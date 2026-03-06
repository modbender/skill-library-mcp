import { PicqerAPI } from './picqer-api.js';

// Thresholds for mover classification
const FAST_MOVER_THRESHOLD = 50;
const SLOW_MOVER_THRESHOLD = 5;

// Clients whose stock we sell (configurable)
const SELL_STOCK_CLIENTS = ['Nike', 'Adidas', 'Puma', 'Reebok', 'New Balance'];

export interface DashboardFilters {
  dateFrom?: string; // ISO date
  dateTo?: string;
  picker?: string;
  client?: string;
}

export interface DashboardData {
  kpis: {
    openPicklists: number;
    closedPicklists: number;
    totalRevenue: number;
    activeClients: number;
    activePickers: number;
  };
  picklists: {
    open: any[];
    closed: any[];
    pickerStats: PickerStat[];
  };
  stock: {
    rows: StockRow[];
  };
  revenue: {
    perClient: RevenueClient[];
  };
  filtersUsed: DashboardFilters;
}

interface PickerStat {
  name: string;
  openCount: number;
  closedCount: number;
  total: number;
  efficiency: number;
}

interface StockRow {
  client: string;
  sku: string;
  productName: string;
  stockIn: number;
  stockOut: number;
  netMovement: number;
  value: number;
  speedCategory: 'fast' | 'slow' | 'normal';
}

interface RevenueClient {
  client: string;
  totalRevenue: number;
  orderCount: number;
  avgOrderValue: number;
  shippingOptions: { name: string; count: number }[];
}

export async function fetchDashboardData(filters: DashboardFilters): Promise<DashboardData> {
  const api = new PicqerAPI();

  // 1. Fetch raw data
  const [openPicklists, closedPicklists, stockMovements, orders] = await Promise.all([
    api.getPicklists({ status: 'open', ...filters }),
    api.getPicklists({ status: 'closed', ...filters }),
    api.getStockMovements(filters),
    api.getOrders(filters)
  ]);

  // 2. Process data
  const pickerStats = processPickerStats(openPicklists, closedPicklists);
  const stockRows = processStockMovements(stockMovements);
  const revenueData = processRevenue(orders);

  // 3. Compute KPIs
  const kpis = {
    openPicklists: openPicklists.length,
    closedPicklists: closedPicklists.length,
    totalRevenue: revenueData.reduce((sum, r) => sum + r.totalRevenue, 0),
    activeClients: new Set([
      ...openPicklists.map((p: any) => p.customer_name),
      ...closedPicklists.map((p: any) => p.customer_name),
      ...stockRows.map(s => s.client)
    ]).size,
    activePickers: pickerStats.length
  };

  return {
    kpis,
    picklists: {
      open: openPicklists,
      closed: closedPicklists,
      pickerStats
    },
    stock: {
      rows: stockRows
    },
    revenue: {
      perClient: revenueData
    },
    filtersUsed: filters
  };
}

function processPickerStats(openPicklists: any[], closedPicklists: any[]): PickerStat[] {
  const pickerMap = new Map<string, { open: number; closed: number }>();

  // Process open
  openPicklists.forEach((pl: any) => {
    const picker = pl.assigned_to || 'Unassigned';
    if (!pickerMap.has(picker)) {
      pickerMap.set(picker, { open: 0, closed: 0 });
    }
    pickerMap.get(picker)!.open++;
  });

  // Process closed
  closedPicklists.forEach((pl: any) => {
    const picker = pl.assigned_to || 'Unassigned';
    if (!pickerMap.has(picker)) {
      pickerMap.set(picker, { open: 0, closed: 0 });
    }
    pickerMap.get(picker)!.closed++;
  });

  // Calculate stats
  return Array.from(pickerMap.entries()).map(([name, stats]) => {
    const total = stats.open + stats.closed;
    return {
      name,
      openCount: stats.open,
      closedCount: stats.closed,
      total,
      efficiency: total > 0 ? Math.round((stats.closed / total) * 100) : 0
    };
  }).sort((a, b) => b.efficiency - a.efficiency);
}

function processStockMovements(movements: any[]): StockRow[] {
  const stockMap = new Map<string, {
    client: string;
    sku: string;
    productName: string;
    in: number;
    out: number;
    value: number;
  }>();

  movements.forEach((move: any) => {
    const key = `${move.client_name || 'Unknown'}_${move.productcode || 'N/A'}`;
    
    if (!stockMap.has(key)) {
      stockMap.set(key, {
        client: move.client_name || 'Unknown',
        sku: move.productcode || 'N/A',
        productName: move.product_name || 'Unknown Product',
        in: 0,
        out: 0,
        value: 0
      });
    }

    const stats = stockMap.get(key)!;
    
    if (move.type === 'in' || move.amount > 0) {
      stats.in += Math.abs(move.amount || 0);
    } else {
      stats.out += Math.abs(move.amount || 0);
    }
    
    stats.value += move.value || 0;
  });

  return Array.from(stockMap.values()).map(stats => {
    const netMovement = stats.in - stats.out;
    let speedCategory: 'fast' | 'slow' | 'normal' = 'normal';
    
    if (netMovement >= FAST_MOVER_THRESHOLD) {
      speedCategory = 'fast';
    } else if (netMovement <= SLOW_MOVER_THRESHOLD) {
      speedCategory = 'slow';
    }

    return {
      client: stats.client,
      sku: stats.sku,
      productName: stats.productName,
      stockIn: stats.in,
      stockOut: stats.out,
      netMovement,
      value: stats.value,
      speedCategory
    };
  }).sort((a, b) => b.netMovement - a.netMovement);
}

function processRevenue(orders: any[]): RevenueClient[] {
  const clientMap = new Map<string, {
    totalRevenue: number;
    orderCount: number;
    shippingOptions: Map<string, number>;
  }>();

  orders.forEach((order: any) => {
    const client = order.customer_name || 'Unknown';
    
    // Only include clients whose stock we sell
    const isSellStockClient = SELL_STOCK_CLIENTS.some(c => 
      client.toLowerCase().includes(c.toLowerCase())
    );
    
    if (!isSellStockClient) return;

    if (!clientMap.has(client)) {
      clientMap.set(client, {
        totalRevenue: 0,
        orderCount: 0,
        shippingOptions: new Map()
      });
    }

    const stats = clientMap.get(client)!;
    stats.totalRevenue += order.totalprice || 0;
    stats.orderCount++;

    const shippingMethod = order.shipping_method || 'Unknown';
    stats.shippingOptions.set(
      shippingMethod, 
      (stats.shippingOptions.get(shippingMethod) || 0) + 1
    );
  });

  return Array.from(clientMap.entries()).map(([client, stats]) => ({
    client,
    totalRevenue: stats.totalRevenue,
    orderCount: stats.orderCount,
    avgOrderValue: stats.orderCount > 0 ? stats.totalRevenue / stats.orderCount : 0,
    shippingOptions: Array.from(stats.shippingOptions.entries())
      .map(([name, count]) => ({ name, count }))
      .sort((a, b) => b.count - a.count)
  })).sort((a, b) => b.totalRevenue - a.totalRevenue);
}
