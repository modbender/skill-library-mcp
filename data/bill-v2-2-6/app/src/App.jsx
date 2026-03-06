import React from 'react';
import { 
  LayoutDashboard, 
  Receipt, 
  RefreshCcw, 
  Wallet, 
  TrendingUp, 
  Activity,
  ChevronRight,
  PieChart as PieChartIcon
} from 'lucide-react';
import { 
  AreaChart, 
  Area, 
  XAxis, 
  YAxis, 
  CartesianGrid, 
  Tooltip, 
  ResponsiveContainer,
  BarChart,
  Bar,
  Cell
} from 'recharts';

const Card = ({ title, amount, subtext, icon: Icon, color = "blue", balance }) => (
  <div className="p-6 rounded-3xl bg-slate-800/40 border border-slate-700/50 backdrop-blur-xl hover:border-slate-500/50 transition-all group">
    <div className="flex justify-between items-start mb-4">
      <div className={`p-2 rounded-xl bg-${color}-500/20 text-${color}-400`}>
        <Icon size={20} />
      </div>
      {balance && (
        <div className="text-[10px] font-bold px-2 py-1 rounded-lg bg-slate-700/50 text-slate-400 border border-slate-600/50">
          BAL: {balance}
        </div>
      )}
    </div>
    <div className="text-slate-500 font-bold text-xs uppercase tracking-widest mb-1">{title}</div>
    <div className="text-2xl font-black text-white tracking-tight flex items-baseline gap-1">
      {amount}
      <span className="text-[10px] text-slate-600 font-bold uppercase">USD</span>
    </div>
    {subtext && <div className="mt-2 text-[11px] text-slate-400 font-medium">{subtext}</div>}
  </div>
);

export default function App() {
  const [data, setData] = React.useState(null);
  const [loading, setLoading] = React.useState(true);

  const fetchData = () => {
    fetch('./usage.json')
      .then(res => res.json())
      .then(json => {
        setData(json);
        setLoading(false);
      })
      .catch(err => {
        console.error("Data fetch error:", err);
        setLoading(false);
      });
  };

  React.useEffect(() => {
    fetchData();
    const interval = setInterval(fetchData, 60000);
    return () => clearInterval(interval);
  }, []);

  if (loading || !data) {
    return (
      <div className="min-h-screen bg-[#0f172a] flex items-center justify-center">
        <div className="flex flex-col items-center gap-4">
          <Activity className="text-blue-500 animate-spin" size={48} />
          <p className="text-slate-400 font-bold tracking-widest animate-pulse">LOADING INTELLIGENCE...</p>
        </div>
      </div>
    );
  }

  const getVal = (name) => {
    const val = data.models[name];
    return isNaN(parseFloat(val)) ? 0 : parseFloat(val);
  };

  const totalToday = getVal("openai") + getVal("claude") + getVal("gemini") + getVal("kimi") + getVal("deepseek");
  
  const chartData = [
    { name: 'OpenAI', value: getVal("openai"), color: '#10b981' },
    { name: 'Claude', value: getVal("claude"), color: '#f97316' },
    { name: 'Gemini', value: getVal("gemini"), color: '#3b82f6' },
    { name: 'Kimi', value: getVal("kimi"), color: '#d946ef' },
    { name: 'DeepSeek', value: getVal("deepseek"), color: '#06b6d4' },
  ].filter(item => item.value > 0);

  const now = new Date();
  const hoursPassed = now.getHours() + (now.getMinutes() / 60);
  const monthlyForecast = ((totalToday / (hoursPassed || 1)) * 24 * 30).toFixed(2);

  return (
    <div className="min-h-screen bg-[#0f172a] text-slate-200 p-4 md:p-8 font-sans selection:bg-blue-500/30">
      <header className="max-w-7xl mx-auto mb-10 flex flex-col md:flex-row justify-between items-start md:items-end gap-6">
        <div>
          <div className="flex items-center gap-3 mb-2">
            <div className="w-12 h-12 rounded-2xl bg-gradient-to-br from-blue-600 to-indigo-700 flex items-center justify-center shadow-2xl shadow-blue-500/20">
              <TrendingUp className="text-white" size={28} />
            </div>
            <div>
              <h1 className="text-3xl font-black tracking-tight text-white">AI Bill Intelligence</h1>
              <p className="text-slate-400 font-bold text-xs uppercase tracking-[0.2em]">Real-time Spend Analytics</p>
            </div>
          </div>
        </div>
        
        <div className="flex items-center gap-3">
          <div className="text-right hidden sm:block">
            <p className="text-[10px] font-bold text-slate-500 uppercase tracking-widest">Last Update</p>
            <p className="text-xs font-mono text-slate-300">{new Date(data.timestamp || Date.now()).toLocaleTimeString()}</p>
          </div>
          <button 
            onClick={() => { setLoading(true); fetchData(); }}
            className="group flex items-center gap-2 px-5 py-3 bg-slate-800/50 hover:bg-slate-700/50 border border-slate-700 rounded-2xl text-sm transition-all active:scale-95">
            <RefreshCcw size={16} className={`${loading ? 'animate-spin' : 'group-hover:rotate-180 transition-transform duration-500'}`} />
            <span className="font-bold text-slate-300">Sync</span>
          </button>
        </div>
      </header>

      <main className="max-w-7xl mx-auto">
        <div className="grid grid-cols-1 lg:grid-cols-4 gap-6 mb-8">
          <div className="lg:col-span-2 relative overflow-hidden p-8 rounded-[2.5rem] bg-gradient-to-br from-blue-600 via-indigo-700 to-violet-800 shadow-2xl shadow-blue-900/30">
            <div className="relative z-10 h-full flex flex-col justify-between">
              <div>
                <div className="text-blue-100/70 font-bold text-xs tracking-[0.2em] mb-4 flex items-center gap-2">
                  <Activity size={16} /> ACCUMULATED TODAY
                </div>
                <div className="text-7xl font-black text-white tracking-tighter flex items-baseline gap-3">
                  ${totalToday.toFixed(3)}
                  <span className="text-2xl font-medium text-blue-200/50 uppercase tracking-widest">USD</span>
                </div>
              </div>
              
              <div className="mt-8 flex flex-wrap gap-3">
                <div className="px-4 py-2 rounded-2xl bg-white/10 backdrop-blur-md border border-white/10 text-xs font-bold text-blue-50 flex items-center gap-2">
                  <span className="w-2 h-2 rounded-full bg-emerald-400 animate-pulse shadow-[0_0_8px_#10b981]"></span>
                  LIVE FEED ACTIVE
                </div>
                <div className="px-4 py-2 rounded-2xl bg-black/20 backdrop-blur-md border border-white/5 text-xs font-bold text-blue-100">
                  REF: FEBRUARY 2026
                </div>
              </div>
            </div>
            <div className="absolute top-[-20%] right-[-10%] w-80 h-80 bg-white/10 rounded-full blur-3xl animate-pulse"></div>
            <div className="absolute bottom-[-10%] left-[10%] w-40 h-40 bg-blue-400/20 rounded-full blur-2xl"></div>
          </div>
          
          <div className="p-8 rounded-[2.5rem] bg-slate-800/40 border border-slate-700/50 backdrop-blur-xl flex flex-col justify-between group hover:border-blue-500/30 transition-colors">
            <div>
              <div className="text-slate-400 font-bold mb-1 text-xs tracking-[0.2em] uppercase flex items-center gap-2">
                <TrendingUp size={14} className="text-blue-400" /> Monthly Forecast
              </div>
              <div className="text-5xl font-black text-white tracking-tight">${monthlyForecast}</div>
              <p className="text-[10px] text-slate-500 mt-2 font-bold uppercase tracking-wider">Projected cost at current pace</p>
            </div>
            <div className="mt-8">
              <div className="flex justify-between text-[10px] font-black mb-2 tracking-widest">
                <span className="text-slate-500">BUDGET PACING</span>
                <span className="text-blue-400">{Math.min(100, (monthlyForecast / 50) * 100).toFixed(0)}%</span>
              </div>
              <div className="h-4 bg-slate-900/50 rounded-xl overflow-hidden p-1 border border-slate-700/50">
                <div 
                  className="h-full bg-gradient-to-r from-blue-600 via-blue-400 to-indigo-400 rounded-lg transition-all duration-1000 shadow-[0_0_15px_rgba(59,130,246,0.4)]" 
                  style={{ width: `${Math.min(100, (monthlyForecast / 50) * 100)}%` }}>
                </div>
              </div>
            </div>
          </div>

          <div className="p-8 rounded-[2.5rem] bg-slate-800/40 border border-slate-700/50 backdrop-blur-xl flex flex-col justify-center">
            <div className="flex items-center gap-3 mb-6">
              <div className="w-10 h-10 rounded-xl bg-emerald-500/20 text-emerald-400 flex items-center justify-center">
                <PieChartIcon size={20} />
              </div>
              <span className="text-xs font-bold tracking-[0.2em] text-slate-400 uppercase">Usage Split</span>
            </div>
            <div className="h-40 w-full">
              <ResponsiveContainer width="100%" height="100%">
                <BarChart data={chartData} layout="vertical">
                  <XAxis type="number" hide />
                  <YAxis dataKey="name" type="category" hide />
                  <Tooltip 
                    cursor={{fill: 'transparent'}}
                    contentStyle={{ backgroundColor: '#1e293b', borderRadius: '12px', border: '1px solid #334155', fontSize: '12px' }}
                  />
                  <Bar dataKey="value" radius={[0, 4, 4, 0]} barSize={12}>
                    {chartData.map((entry, index) => (
                      <Cell key={`cell-${index}`} fill={entry.color} />
                    ))}
                  </Bar>
                </BarChart>
              </ResponsiveContainer>
            </div>
          </div>
        </div>

        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-5 gap-6">
          <Card 
            title="OpenAI" 
            amount={getVal("openai").toFixed(4)} 
            icon={TrendingUp} 
            color="emerald" 
            balance={data.models.openai_bal}
            subtext="GPT-4o / o1"
          />
          <Card 
            title="Claude" 
            amount={getVal("claude").toFixed(4)} 
            icon={TrendingUp} 
            color="orange" 
            balance={data.models.claude_bal}
            subtext="Sonnet 3.5 / Opus"
          />
          <Card 
            title="Gemini" 
            amount={getVal("gemini").toFixed(4)} 
            icon={TrendingUp} 
            color="blue" 
            balance={data.models.gemini_bal}
            subtext="1.5 Pro / Flash"
          />
          <Card 
            title="Kimi" 
            amount={getVal("kimi").toFixed(4)} 
            icon={TrendingUp} 
            color="purple" 
            balance={data.models.kimi_bal}
            subtext="K2.5 Intelligence"
          />
          <Card 
            title="DeepSeek" 
            amount={getVal("deepseek").toFixed(4)} 
            icon={TrendingUp} 
            color="cyan" 
            balance={data.models.deepseek_bal}
            subtext="V3 / R1 Reasoner"
          />
        </div>
        
        <div className="mt-8 p-6 rounded-3xl bg-slate-800/20 border border-slate-700/30 flex flex-wrap items-center justify-between gap-4">
          <div className="flex items-center gap-4 text-xs font-bold text-slate-500 uppercase tracking-widest">
            <span>External Providers:</span>
            <div className="flex gap-2">
              <span className="px-2 py-1 rounded bg-slate-800 border border-slate-700 text-slate-400">Grok</span>
              <span className="px-2 py-1 rounded bg-slate-800 border border-slate-700 text-slate-400">Perplexity</span>
            </div>
          </div>
          <div className="flex items-center gap-2 text-[10px] text-blue-400 font-black italic">
            <Activity size={12} /> SYSTEM STATUS: OPERATIONAL
          </div>
        </div>
      </main>
      
      <footer className="max-w-7xl mx-auto mt-20 pb-12 text-center">
        <div className="h-px w-full bg-gradient-to-r from-transparent via-slate-700 to-transparent mb-8"></div>
        <p className="text-slate-600 text-[10px] font-black tracking-[0.4em] uppercase">
          Autonomous Infrastructure Management • Chloe AI Engine 2026
        </p>
      </footer>
    </div>
  );
}
