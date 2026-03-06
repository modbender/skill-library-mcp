'use client';

import { useState, useEffect, useCallback } from 'react';
import { PieChart, Pie, Cell, ResponsiveContainer, Tooltip, Legend } from 'recharts';
import { TrendingUp, Plus, Download, RefreshCw, Trash2, Edit2, X, Wallet, BarChart3, DollarSign, ChevronDown, FolderPlus, Trash, Calendar, Percent } from 'lucide-react';
import { Holding, PriceData, PortfolioSummary, Portfolio, DividendSummary, HoldingWithDividends } from '@/lib/types';

const COLORS = ['#6366f1', '#22c55e', '#f59e0b', '#ef4444', '#8b5cf6', '#ec4899', '#14b8a6', '#f97316'];

export default function PortfolioPage() {
  const [portfolios, setPortfolios] = useState<Portfolio[]>([]);
  const [activePortfolioId, setActivePortfolioId] = useState<string | null>(null);
  const [holdings, setHoldings] = useState<Holding[]>([]);
  const [prices, setPrices] = useState<Record<string, PriceData>>({});
  const [loading, setLoading] = useState(true);
  const [showForm, setShowForm] = useState(false);
  const [showSellForm, setShowSellForm] = useState(false);
  const [editingId, setEditingId] = useState<string | null>(null);
  const [sellingHolding, setSellingHolding] = useState<Holding | null>(null);
  const [showPortfolioMenu, setShowPortfolioMenu] = useState(false);
  const [showNewPortfolio, setShowNewPortfolio] = useState(false);
  const [newPortfolioName, setNewPortfolioName] = useState('');
  const [realizedPL, setRealizedPL] = useState(0);
  const [dividendData, setDividendData] = useState<{
    holdings: HoldingWithDividends[];
    summary: DividendSummary;
  } | null>(null);
  const [showDividends, setShowDividends] = useState(false);

  const [formData, setFormData] = useState({
    symbol: '',
    name: '',
    type: 'stock' as 'stock' | 'crypto',
    quantity: '',
    purchasePrice: '',
    purchaseDate: new Date().toISOString().split('T')[0],
  });

  const [sellData, setSellData] = useState({
    quantity: '',
    sellPrice: '',
    sellDate: new Date().toISOString().split('T')[0],
  });

  const fetchPortfolio = useCallback(async () => {
    setLoading(true);
    try {
      const res = await fetch('/api/portfolio');
      const data = await res.json();
      setPortfolios(data.portfolios || []);
      setActivePortfolioId(data.activePortfolioId);
      setHoldings(data.portfolio?.holdings || []);
      setRealizedPL(data.realizedPL || 0);
      
      if (data.portfolio?.holdings?.length > 0) {
        const symbols = data.portfolio.holdings.map((h: Holding) => h.symbol);
        const types = data.portfolio.holdings.map((h: Holding) => h.type);
        
        const priceRes = await fetch('/api/prices', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ symbols, types }),
        });
        
        const priceData = await priceRes.json();
        setPrices(priceData);

        // Fetch dividend data
        const dividendRes = await fetch('/api/dividends');
        const dividendData = await dividendRes.json();
        setDividendData(dividendData);
      }
    } catch (error) {
      console.error('Error fetching portfolio:', error);
    }
    setLoading(false);
  }, []);

  // eslint-disable-next-line react-hooks/exhaustive-deps
  useEffect(() => {
    fetchPortfolio();
  }, []);

  async function createPortfolio() {
    if (!newPortfolioName.trim()) return;
    try {
      await fetch('/api/portfolio', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ action: 'createPortfolio', name: newPortfolioName }),
      });
      setNewPortfolioName('');
      setShowNewPortfolio(false);
      fetchPortfolio();
    } catch (error) {
      console.error('Error creating portfolio:', error);
    }
  }

  async function switchPortfolio(id: string) {
    try {
      await fetch('/api/portfolio', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ action: 'setActive', id }),
      });
      setShowPortfolioMenu(false);
      fetchPortfolio();
    } catch (error) {
      console.error('Error switching portfolio:', error);
    }
  }

  async function deletePortfolio(id: string) {
    if (!confirm('Delete this portfolio? This cannot be undone.')) return;
    try {
      await fetch('/api/portfolio', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ action: 'deletePortfolio', id }),
      });
      fetchPortfolio();
    } catch (error) {
      console.error('Error deleting portfolio:', error);
    }
  }

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    
    const holdingData = {
      symbol: formData.symbol.toUpperCase(),
      name: formData.name,
      type: formData.type,
      quantity: parseFloat(formData.quantity),
      purchasePrice: parseFloat(formData.purchasePrice),
      purchaseDate: formData.purchaseDate,
    };

    try {
      if (editingId) {
        await fetch('/api/portfolio', {
          method: 'PUT',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ id: editingId, updates: holdingData }),
        });
      } else {
        await fetch('/api/portfolio', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(holdingData),
        });
      }
      
      setFormData({
        symbol: '',
        name: '',
        type: 'stock',
        quantity: '',
        purchasePrice: '',
        purchaseDate: new Date().toISOString().split('T')[0],
      });
      setShowForm(false);
      setEditingId(null);
      fetchPortfolio();
    } catch (error) {
      console.error('Error saving holding:', error);
    }
  }

  async function handleDelete(id: string) {
    if (!confirm('Delete this holding?')) return;
    
    try {
      await fetch('/api/portfolio', {
        method: 'DELETE',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ id }),
      });
      fetchPortfolio();
    } catch (error) {
      console.error('Error deleting holding:', error);
    }
  }

  function handleEdit(holding: Holding) {
    setFormData({
      symbol: holding.symbol,
      name: holding.name,
      type: holding.type,
      quantity: holding.quantity.toString(),
      purchasePrice: holding.purchasePrice.toString(),
      purchaseDate: holding.purchaseDate,
    });
    setEditingId(holding.id);
    setShowForm(true);
  }

  function handleSellClick(holding: Holding) {
    setSellingHolding(holding);
    const currentPrice = prices[holding.symbol]?.price || holding.purchasePrice;
    setSellData({
      quantity: '',
      sellPrice: currentPrice.toString(),
      sellDate: new Date().toISOString().split('T')[0],
    });
    setShowSellForm(true);
  }

  async function handleSellSubmit(e: React.FormEvent) {
    e.preventDefault();
    if (!sellingHolding) return;
    
    try {
      const res = await fetch('/api/portfolio', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          action: 'sell',
          symbol: sellingHolding.symbol,
          quantity: sellData.quantity,
          sellPrice: sellData.sellPrice,
          sellDate: sellData.sellDate,
        }),
      });
      
      if (!res.ok) {
        const error = await res.json();
        alert(error.error || 'Failed to sell');
        return;
      }
      
      setShowSellForm(false);
      setSellingHolding(null);
      fetchPortfolio();
    } catch (error) {
      console.error('Error selling:', error);
    }
  }

  function exportCsv() {
    window.open('/api/export', '_blank');
  }

  const activePortfolio = portfolios.find(p => p.id === activePortfolioId);

  const summary: PortfolioSummary = holdings.reduce(
    (acc, h) => {
      const price = prices[h.symbol]?.price || h.purchasePrice;
      const value = price * h.quantity;
      const cost = h.purchasePrice * h.quantity;
      return {
        totalValue: acc.totalValue + value,
        totalCost: acc.totalCost + cost,
        totalGain: acc.totalGain + (value - cost),
        totalGainPercent: 0,
      };
    },
    { totalValue: 0, totalCost: 0, totalGain: 0, totalGainPercent: 0 }
  );
  summary.totalGainPercent = summary.totalCost > 0 
    ? (summary.totalGain / summary.totalCost) * 100 
    : 0;

  const allocationData = holdings.map((h, i) => {
    const value = (prices[h.symbol]?.price || h.purchasePrice) * h.quantity;
    return {
      name: h.symbol,
      value,
      color: COLORS[i % COLORS.length],
    };
  });

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-slate-800 to-slate-900 text-white">
      <div className="max-w-7xl mx-auto px-4 py-8">
        <div className="flex items-center justify-between mb-8">
          <div className="flex items-center gap-3">
            <div className="p-2 bg-indigo-600 rounded-xl">
              <Wallet size={28} />
            </div>
            <div>
              <div className="relative">
                <button 
                  onClick={() => setShowPortfolioMenu(!showPortfolioMenu)}
                  className="flex items-center gap-2 hover:text-indigo-400 transition-colors"
                >
                  <h1 className="text-2xl font-bold">{activePortfolio?.name || 'Portfolio'}</h1>
                  <ChevronDown size={18} />
                </button>
                {showPortfolioMenu && (
                  <div className="absolute top-full left-0 mt-2 w-56 bg-slate-800 border border-slate-700 rounded-xl shadow-xl z-50 overflow-hidden">
                    <div className="max-h-64 overflow-y-auto">
                      {portfolios.map(p => (
                        <div key={p.id} className="flex items-center justify-between px-4 py-2 hover:bg-slate-700/50">
                          <button 
                            onClick={() => switchPortfolio(p.id)}
                            className={`flex-1 text-left ${p.id === activePortfolioId ? 'text-indigo-400' : ''}`}
                          >
                            {p.name}
                          </button>
                          {portfolios.length > 1 && (
                            <button 
                              onClick={() => deletePortfolio(p.id)}
                              className="p-1 hover:bg-red-500/20 rounded"
                            >
                              <Trash size={14} className="text-red-400" />
                            </button>
                          )}
                        </div>
                      ))}
                    </div>
                    <div className="border-t border-slate-700">
                      <button 
                        onClick={() => { setShowNewPortfolio(true); setShowPortfolioMenu(false); }}
                        className="w-full flex items-center gap-2 px-4 py-3 hover:bg-slate-700/50 text-indigo-400"
                      >
                        <FolderPlus size={16} />
                        New Portfolio
                      </button>
                    </div>
                  </div>
                )}
              </div>
              <p className="text-slate-400 text-sm">Track your investments</p>
            </div>
          </div>
          <div className="flex gap-2">
            <button
              onClick={fetchPortfolio}
              className="flex items-center gap-2 px-4 py-2.5 bg-slate-700/50 hover:bg-slate-700 rounded-xl transition-colors"
            >
              <RefreshCw size={18} />
              <span className="hidden sm:inline">Refresh</span>
            </button>
            <button
              onClick={exportCsv}
              className="flex items-center gap-2 px-4 py-2.5 bg-slate-700/50 hover:bg-slate-700 rounded-xl transition-colors"
            >
              <Download size={18} />
              <span className="hidden sm:inline">Export</span>
            </button>
            <button
              onClick={() => { setShowForm(true); setEditingId(null); setFormData({
                symbol: '', name: '', type: 'stock', quantity: '',
                purchasePrice: '', purchaseDate: new Date().toISOString().split('T')[0],
              }); }}
              className="flex items-center gap-2 px-5 py-2.5 bg-indigo-600 hover:bg-indigo-500 rounded-xl transition-colors font-medium"
            >
              <Plus size={18} />
              <span className="hidden sm:inline">Add</span>
            </button>
          </div>
        </div>

        {loading ? (
          <div className="flex items-center justify-center h-64">
            <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-indigo-500"></div>
          </div>
        ) : (
          <>
            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-5 gap-4 mb-8">
              <div className="bg-slate-800/50 backdrop-blur-sm p-6 rounded-2xl border border-slate-700">
                <div className="flex items-center gap-2 mb-2">
                  <DollarSign size={18} className="text-indigo-400" />
                  <p className="text-slate-400 text-sm">Total Value</p>
                </div>
                <p className="text-2xl font-bold">${summary.totalValue.toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 })}</p>
              </div>
              <div className="bg-slate-800/50 backdrop-blur-sm p-6 rounded-2xl border border-slate-700">
                <div className="flex items-center gap-2 mb-2">
                  <Wallet size={18} className="text-slate-400" />
                  <p className="text-slate-400 text-sm">Total Cost</p>
                </div>
                <p className="text-2xl font-bold">${summary.totalCost.toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 })}</p>
              </div>
              <div className="bg-slate-800/50 backdrop-blur-sm p-6 rounded-2xl border border-slate-700">
                <div className="flex items-center gap-2 mb-2">
                  <BarChart3 size={18} className={realizedPL >= 0 ? 'text-green-400' : 'text-red-400'} />
                  <p className="text-slate-400 text-sm">Realized P&L</p>
                </div>
                <p className={`text-2xl font-bold ${realizedPL >= 0 ? 'text-green-400' : 'text-red-400'}`}>
                  {realizedPL >= 0 ? '+' : ''}{realizedPL.toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 })}
                </p>
              </div>
              <div className="bg-slate-800/50 backdrop-blur-sm p-6 rounded-2xl border border-slate-700">
                <div className="flex items-center gap-2 mb-2">
                  <TrendingUp size={18} className={summary.totalGain >= 0 ? 'text-green-400' : 'text-red-400'} />
                  <p className="text-slate-400 text-sm">Unrealized P&L</p>
                </div>
                <p className={`text-2xl font-bold ${summary.totalGain >= 0 ? 'text-green-400' : 'text-red-400'}`}>
                  {summary.totalGain >= 0 ? '+' : ''}{summary.totalGain.toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 })}
                </p>
              </div>
              <div className="bg-slate-800/50 backdrop-blur-sm p-6 rounded-2xl border border-slate-700">
                <div className="flex items-center gap-2 mb-2">
                  <TrendingUp size={18} className={(summary.totalGain + realizedPL) >= 0 ? 'text-green-400' : 'text-red-400'} />
                  <p className="text-slate-400 text-sm">Total P&L</p>
                </div>
                <p className={`text-2xl font-bold ${(summary.totalGain + realizedPL) >= 0 ? 'text-green-400' : 'text-red-400'}`}>
                  {(summary.totalGain + realizedPL) >= 0 ? '+' : ''}{(summary.totalGain + realizedPL).toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 })}
                </p>
              </div>
            </div>

            {/* Dividend Summary Cards */}
            {dividendData && dividendData.summary.totalProjectedIncome > 0 && (
              <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4 mb-8">
                <div className="bg-gradient-to-br from-emerald-900/50 to-emerald-800/30 backdrop-blur-sm p-6 rounded-2xl border border-emerald-700/50">
                  <div className="flex items-center gap-2 mb-2">
                    <DollarSign size={18} className="text-emerald-400" />
                    <p className="text-slate-400 text-sm">Annual Dividend Income</p>
                  </div>
                  <p className="text-2xl font-bold text-emerald-400">
                    ${dividendData.summary.totalProjectedIncome.toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 })}
                  </p>
                  <p className="text-sm text-slate-500 mt-1">
                    ${(dividendData.summary.totalProjectedIncome / 12).toFixed(2)}/mo
                  </p>
                </div>
                <div className="bg-gradient-to-br from-blue-900/50 to-blue-800/30 backdrop-blur-sm p-6 rounded-2xl border border-blue-700/50">
                  <div className="flex items-center gap-2 mb-2">
                    <Percent size={18} className="text-blue-400" />
                    <p className="text-slate-400 text-sm">Weighted Avg Yield</p>
                  </div>
                  <p className="text-2xl font-bold text-blue-400">
                    {dividendData.summary.weightedAvgYield.toFixed(2)}%
                  </p>
                </div>
                <div className="bg-gradient-to-br from-purple-900/50 to-purple-800/30 backdrop-blur-sm p-6 rounded-2xl border border-purple-700/50">
                  <div className="flex items-center gap-2 mb-2">
                    <TrendingUp size={18} className="text-purple-400" />
                    <p className="text-slate-400 text-sm">Yield on Cost</p>
                  </div>
                  <p className="text-2xl font-bold text-purple-400">
                    {dividendData.summary.totalYOC.toFixed(2)}%
                  </p>
                </div>
                <div className="bg-gradient-to-br from-amber-900/50 to-amber-800/30 backdrop-blur-sm p-6 rounded-2xl border border-amber-700/50">
                  <div className="flex items-center gap-2 mb-2">
                    <Calendar size={18} className="text-amber-400" />
                    <p className="text-slate-400 text-sm">Upcoming Ex-Dates</p>
                  </div>
                  <p className="text-2xl font-bold text-amber-400">
                    {dividendData.summary.upcomingExDates.length}
                  </p>
                  <p className="text-sm text-slate-500 mt-1">Next 30 days</p>
                </div>
              </div>
            )}

            {/* Toggle Dividends Button */}
            {dividendData && (
              <div className="mb-4">
                <button
                  onClick={() => setShowDividends(!showDividends)}
                  className="flex items-center gap-2 px-4 py-2.5 bg-emerald-600/20 hover:bg-emerald-600/30 border border-emerald-600/50 rounded-xl transition-colors text-emerald-400"
                >
                  <DollarSign size={18} />
                  <span>{showDividends ? 'Hide' : 'Show'} Dividend Details</span>
                </button>
              </div>
            )}

            {/* Dividends Section */}
            {showDividends && dividendData && (
              <div className="bg-slate-800/50 backdrop-blur-sm rounded-2xl border border-slate-700 overflow-hidden mb-8">
                <div className="p-6 border-b border-slate-700">
                  <h2 className="text-lg font-semibold flex items-center gap-2">
                    <DollarSign size={20} className="text-emerald-400" />
                    Dividend Details
                  </h2>
                </div>
                <div className="overflow-x-auto">
                  <table className="w-full">
                    <thead className="bg-slate-700/30">
                      <tr>
                        <th className="px-6 py-4 text-left text-xs font-medium text-slate-400 uppercase tracking-wider">Asset</th>
                        <th className="px-6 py-4 text-right text-xs font-medium text-slate-400 uppercase tracking-wider">Yield %</th>
                        <th className="px-6 py-4 text-right text-xs font-medium text-slate-400 uppercase tracking-wider">YOC %</th>
                        <th className="px-6 py-4 text-right text-xs font-medium text-slate-400 uppercase tracking-wider">Annual Income</th>
                        <th className="px-6 py-4 text-right text-xs font-medium text-slate-400 uppercase tracking-wider">Ex-Date</th>
                      </tr>
                    </thead>
                    <tbody className="divide-y divide-slate-700/50">
                      {dividendData.holdings
                        .filter(h => h.dividendData && h.dividendData.trailingYield > 0)
                        .map((h) => (
                          <tr key={h.id} className="hover:bg-slate-700/30 transition-colors">
                            <td className="px-6 py-4">
                              <div className="flex items-center gap-3">
                                <div className="w-10 h-10 rounded-full flex items-center justify-center text-sm font-bold bg-emerald-500/20 text-emerald-400">
                                  {h.symbol.slice(0, 2)}
                                </div>
                                <div>
                                  <div className="font-semibold">{h.symbol}</div>
                                  <div className="text-sm text-slate-400">{h.name}</div>
                                </div>
                              </div>
                            </td>
                            <td className="px-6 py-4 text-right">
                              <span className="text-emerald-400">
                                {h.dividendData?.trailingYield.toFixed(2)}%
                              </span>
                            </td>
                            <td className="px-6 py-4 text-right">
                              <span className="text-purple-400">
                                {h.yoc?.toFixed(2)}%
                              </span>
                            </td>
                            <td className="px-6 py-4 text-right font-semibold">
                              ${h.projectedIncome?.toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 })}
                            </td>
                            <td className="px-6 py-4 text-right text-slate-400">
                              {h.dividendData?.exDividendDate || 'N/A'}
                            </td>
                          </tr>
                        ))}
                    </tbody>
                  </table>
                </div>
                {dividendData.summary.upcomingExDates.length > 0 && (
                  <div className="p-6 border-t border-slate-700">
                    <h3 className="text-sm font-medium text-slate-400 mb-4 flex items-center gap-2">
                      <Calendar size={16} className="text-amber-400" />
                      Upcoming Ex-Dividend Dates (Next 30 Days)
                    </h3>
                    <div className="flex flex-wrap gap-2">
                      {dividendData.summary.upcomingExDates.map((item) => (
                        <div
                          key={item.symbol}
                          className="px-3 py-2 bg-amber-500/10 border border-amber-500/30 rounded-lg text-sm"
                        >
                          <span className="font-semibold text-amber-400">{item.symbol}</span>
                          <span className="text-slate-400 ml-2">{item.date}</span>
                          <span className="text-slate-500 ml-1">
                            ({item.daysUntil === 0 ? 'Today' : `${item.daysUntil}d`})
                          </span>
                        </div>
                      ))}
                    </div>
                  </div>
                )}
              </div>
            )}

            {allocationData.length > 0 && (
              <div className="bg-slate-800/50 backdrop-blur-sm p-6 rounded-2xl border border-slate-700 mb-8">
                <h2 className="text-lg font-semibold mb-4">Allocation</h2>
                <div className="h-72">
                  <ResponsiveContainer width="100%" height="100%">
                    <PieChart>
                      <Pie
                        data={allocationData}
                        cx="50%"
                        cy="50%"
                        innerRadius={70}
                        outerRadius={110}
                        paddingAngle={3}
                        dataKey="value"
                      >
                        {allocationData.map((entry, index) => (
                          <Cell key={`cell-${index}`} fill={entry.color} stroke="transparent" />
                        ))}
                      </Pie>
                      <Tooltip 
                        formatter={(value) => `$${Number(value).toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 })}`}
                        contentStyle={{ backgroundColor: '#1e293b', border: '1px solid #334155', borderRadius: '12px' }}
                        itemStyle={{ color: '#e2e8f0' }}
                      />
                      <Legend 
                        formatter={(value) => <span style={{ color: '#e2e8f0' }}>{value}</span>}
                      />
                    </PieChart>
                  </ResponsiveContainer>
                </div>
              </div>
            )}

            <div className="bg-slate-800/50 backdrop-blur-sm rounded-2xl border border-slate-700 overflow-hidden">
              <div className="overflow-x-auto">
                <table className="w-full">
                  <thead className="bg-slate-700/30">
                    <tr>
                      <th className="px-6 py-4 text-left text-xs font-medium text-slate-400 uppercase tracking-wider">Asset</th>
                      <th className="px-6 py-4 text-right text-xs font-medium text-slate-400 uppercase tracking-wider">Price</th>
                      <th className="px-6 py-4 text-right text-xs font-medium text-slate-400 uppercase tracking-wider">Qty</th>
                      <th className="px-6 py-4 text-right text-xs font-medium text-slate-400 uppercase tracking-wider">Value</th>
                      <th className="px-6 py-4 text-right text-xs font-medium text-slate-400 uppercase tracking-wider">Cost</th>
                      <th className="px-6 py-4 text-right text-xs font-medium text-slate-400 uppercase tracking-wider">P&L</th>
                      <th className="px-6 py-4 text-right text-xs font-medium text-slate-400 uppercase tracking-wider">Return</th>
                      <th className="px-6 py-4 text-right text-xs font-medium text-slate-400 uppercase tracking-wider"></th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-slate-700/50">
                    {holdings.length === 0 ? (
                      <tr>
                        <td colSpan={8} className="px-6 py-16 text-center text-slate-500">
                          <div className="flex flex-col items-center gap-3">
                            <Wallet size={48} className="text-slate-600" />
                            <p>No holdings yet. Add your first asset!</p>
                          </div>
                        </td>
                      </tr>
                    ) : (
                      holdings.map((h) => {
                        const price = prices[h.symbol]?.price || h.purchasePrice;
                        const change = prices[h.symbol]?.changePercent || 0;
                        const value = price * h.quantity;
                        const cost = h.purchasePrice * h.quantity;
                        const gain = value - cost;
                        const gainPercent = cost > 0 ? (gain / cost) * 100 : 0;
                        
                        return (
                          <tr key={h.id} className="hover:bg-slate-700/30 transition-colors">
                            <td className="px-6 py-4">
                              <div className="flex items-center gap-3">
                                <div className={`w-10 h-10 rounded-full flex items-center justify-center text-sm font-bold ${h.type === 'crypto' ? 'bg-purple-500/20 text-purple-400' : 'bg-blue-500/20 text-blue-400'}`}>
                                  {h.symbol.slice(0, 2)}
                                </div>
                                <div>
                                  <div className="font-semibold">{h.symbol}</div>
                                  <div className="text-sm text-slate-400">{h.name}</div>
                                </div>
                              </div>
                            </td>
                            <td className="px-6 py-4 text-right">
                              <div>${price.toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 })}</div>
                              <div className={`text-sm ${change >= 0 ? 'text-green-400' : 'text-red-400'}`}>
                                {change >= 0 ? '+' : ''}{change.toFixed(2)}%
                              </div>
                            </td>
                            <td className="px-6 py-4 text-right text-slate-300">{h.quantity}</td>
                            <td className="px-6 py-4 text-right font-semibold">${value.toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 })}</td>
                            <td className="px-6 py-4 text-right text-slate-400">${cost.toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 })}</td>
                            <td className={`px-6 py-4 text-right font-medium ${gain >= 0 ? 'text-green-400' : 'text-red-400'}`}>
                              {gain >= 0 ? '+' : ''}{gain.toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 })}
                            </td>
                            <td className={`px-6 py-4 text-right ${gainPercent >= 0 ? 'text-green-400' : 'text-red-400'}`}>
                              {gainPercent >= 0 ? '+' : ''}{gainPercent.toFixed(2)}%
                            </td>
                            <td className="px-6 py-4">
                              <div className="flex justify-end gap-1">
                                <button onClick={() => handleSellClick(h)} className="p-2 hover:bg-green-500/20 rounded-lg transition-colors" title="Sell">
                                  <DollarSign size={16} className="text-green-400" />
                                </button>
                                <button onClick={() => handleEdit(h)} className="p-2 hover:bg-slate-600 rounded-lg transition-colors">
                                  <Edit2 size={16} className="text-slate-400" />
                                </button>
                                <button onClick={() => handleDelete(h.id)} className="p-2 hover:bg-red-500/20 rounded-lg transition-colors">
                                  <Trash2 size={16} className="text-red-400" />
                                </button>
                              </div>
                            </td>
                          </tr>
                        );
                      })
                    )}
                  </tbody>
                </table>
              </div>
            </div>
          </>
        )}

        {showForm && (
          <div className="fixed inset-0 bg-black/70 backdrop-blur-sm flex items-center justify-center p-4 z-50">
            <div className="bg-slate-800 rounded-2xl p-6 w-full max-w-md border border-slate-700">
              <div className="flex items-center justify-between mb-6">
                <h2 className="text-xl font-semibold">{editingId ? 'Edit' : 'Add'} Asset</h2>
                <button onClick={() => { setShowForm(false); setEditingId(null); }} className="p-2 hover:bg-slate-700 rounded-lg">
                  <X size={20} />
                </button>
              </div>
              <form onSubmit={handleSubmit} className="space-y-4">
                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <label className="block text-sm font-medium text-slate-400 mb-2">Symbol</label>
                    <input
                      type="text"
                      value={formData.symbol}
                      onChange={(e) => setFormData({ ...formData, symbol: e.target.value })}
                      placeholder="AAPL"
                      className="w-full px-4 py-3 bg-slate-700 border border-slate-600 rounded-xl focus:outline-none focus:ring-2 focus:ring-indigo-500"
                      required
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-slate-400 mb-2">Type</label>
                    <select
                      value={formData.type}
                      onChange={(e) => setFormData({ ...formData, type: e.target.value as 'stock' | 'crypto' })}
                      className="w-full px-4 py-3 bg-slate-700 border border-slate-600 rounded-xl focus:outline-none focus:ring-2 focus:ring-indigo-500"
                    >
                      <option value="stock">Stock</option>
                      <option value="crypto">Crypto</option>
                    </select>
                  </div>
                </div>
                <div>
                  <label className="block text-sm font-medium text-slate-400 mb-2">Name</label>
                  <input
                    type="text"
                    value={formData.name}
                    onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                    placeholder="Apple Inc."
                    className="w-full px-4 py-3 bg-slate-700 border border-slate-600 rounded-xl focus:outline-none focus:ring-2 focus:ring-indigo-500"
                    required
                  />
                </div>
                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <label className="block text-sm font-medium text-slate-400 mb-2">Quantity</label>
                    <input
                      type="number"
                      step="any"
                      value={formData.quantity}
                      onChange={(e) => setFormData({ ...formData, quantity: e.target.value })}
                      placeholder="10"
                      className="w-full px-4 py-3 bg-slate-700 border border-slate-600 rounded-xl focus:outline-none focus:ring-2 focus:ring-indigo-500"
                      required
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-slate-400 mb-2">Purchase Price</label>
                    <input
                      type="number"
                      step="any"
                      value={formData.purchasePrice}
                      onChange={(e) => setFormData({ ...formData, purchasePrice: e.target.value })}
                      placeholder="150.00"
                      className="w-full px-4 py-3 bg-slate-700 border border-slate-600 rounded-xl focus:outline-none focus:ring-2 focus:ring-indigo-500"
                      required
                    />
                  </div>
                </div>
                <div>
                  <label className="block text-sm font-medium text-slate-400 mb-2">Purchase Date</label>
                  <input
                    type="date"
                    value={formData.purchaseDate}
                    onChange={(e) => setFormData({ ...formData, purchaseDate: e.target.value })}
                    className="w-full px-4 py-3 bg-slate-700 border border-slate-600 rounded-xl focus:outline-none focus:ring-2 focus:ring-indigo-500"
                    required
                  />
                </div>
                <div className="flex gap-3 pt-2">
                  <button
                    type="button"
                    onClick={() => { setShowForm(false); setEditingId(null); }}
                    className="flex-1 px-4 py-3 border border-slate-600 rounded-xl hover:bg-slate-700 transition-colors"
                  >
                    Cancel
                  </button>
                  <button type="submit" className="flex-1 px-4 py-3 bg-indigo-600 hover:bg-indigo-500 rounded-xl transition-colors font-medium">
                    {editingId ? 'Update' : 'Add Asset'}
                  </button>
                </div>
              </form>
            </div>
          </div>
        )}

        {showSellForm && sellingHolding && (
          <div className="fixed inset-0 bg-black/70 backdrop-blur-sm flex items-center justify-center p-4 z-50">
            <div className="bg-slate-800 rounded-2xl p-6 w-full max-w-md border border-slate-700">
              <div className="flex items-center justify-between mb-6">
                <h2 className="text-xl font-semibold">Sell {sellingHolding.symbol}</h2>
                <button onClick={() => { setShowSellForm(false); setSellingHolding(null); }} className="p-2 hover:bg-slate-700 rounded-lg">
                  <X size={20} />
                </button>
              </div>
              <div className="mb-4 p-3 bg-slate-700/50 rounded-xl">
                <p className="text-sm text-slate-400">Available: <span className="text-white font-semibold">{sellingHolding.quantity} {sellingHolding.symbol}</span></p>
              </div>
              <form onSubmit={handleSellSubmit} className="space-y-4">
                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <label className="block text-sm font-medium text-slate-400 mb-2">Quantity</label>
                    <input
                      type="number"
                      step="any"
                      value={sellData.quantity}
                      onChange={(e) => setSellData({ ...sellData, quantity: e.target.value })}
                      placeholder="5"
                      max={sellingHolding.quantity}
                      className="w-full px-4 py-3 bg-slate-700 border border-slate-600 rounded-xl focus:outline-none focus:ring-2 focus:ring-green-500"
                      required
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-slate-400 mb-2">Sell Price</label>
                    <input
                      type="number"
                      step="any"
                      value={sellData.sellPrice}
                      onChange={(e) => setSellData({ ...sellData, sellPrice: e.target.value })}
                      placeholder="180.00"
                      className="w-full px-4 py-3 bg-slate-700 border border-slate-600 rounded-xl focus:outline-none focus:ring-2 focus:ring-green-500"
                      required
                    />
                  </div>
                </div>
                <div>
                  <label className="block text-sm font-medium text-slate-400 mb-2">Sell Date</label>
                  <input
                    type="date"
                    value={sellData.sellDate}
                    onChange={(e) => setSellData({ ...sellData, sellDate: e.target.value })}
                    className="w-full px-4 py-3 bg-slate-700 border border-slate-600 rounded-xl focus:outline-none focus:ring-2 focus:ring-green-500"
                    required
                  />
                </div>
                <div className="flex gap-3 pt-2">
                  <button
                    type="button"
                    onClick={() => { setShowSellForm(false); setSellingHolding(null); }}
                    className="flex-1 px-4 py-3 border border-slate-600 rounded-xl hover:bg-slate-700 transition-colors"
                  >
                    Cancel
                  </button>
                  <button type="submit" className="flex-1 px-4 py-3 bg-green-600 hover:bg-green-500 rounded-xl transition-colors font-medium">
                    Sell
                  </button>
                </div>
              </form>
            </div>
          </div>
        )}

        {showNewPortfolio && (
          <div className="fixed inset-0 bg-black/70 backdrop-blur-sm flex items-center justify-center p-4 z-50">
            <div className="bg-slate-800 rounded-2xl p-6 w-full max-w-sm border border-slate-700">
              <div className="flex items-center justify-between mb-6">
                <h2 className="text-xl font-semibold">New Portfolio</h2>
                <button onClick={() => setShowNewPortfolio(false)} className="p-2 hover:bg-slate-700 rounded-lg">
                  <X size={20} />
                </button>
              </div>
              <div className="space-y-4">
                <div>
                  <label className="block text-sm font-medium text-slate-400 mb-2">Portfolio Name</label>
                  <input
                    type="text"
                    value={newPortfolioName}
                    onChange={(e) => setNewPortfolioName(e.target.value)}
                    placeholder="My Portfolio"
                    className="w-full px-4 py-3 bg-slate-700 border border-slate-600 rounded-xl focus:outline-none focus:ring-2 focus:ring-indigo-500"
                    autoFocus
                  />
                </div>
                <div className="flex gap-3">
                  <button
                    onClick={() => setShowNewPortfolio(false)}
                    className="flex-1 px-4 py-3 border border-slate-600 rounded-xl hover:bg-slate-700 transition-colors"
                  >
                    Cancel
                  </button>
                  <button 
                    onClick={createPortfolio}
                    className="flex-1 px-4 py-3 bg-indigo-600 hover:bg-indigo-500 rounded-xl transition-colors font-medium"
                  >
                    Create
                  </button>
                </div>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
