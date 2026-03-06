import { jsx as _jsx, jsxs as _jsxs } from "react/jsx-runtime";
import { IconHarvested, IconCharts, IconAPR, IconRate } from '../icons';
export function PerformanceMetrics({ totalHarvested, totalCompounded, realizedAPR, successRate, totalActions }) {
    const aprValue = typeof realizedAPR === 'string' ? parseFloat(realizedAPR) : realizedAPR;
    const metrics = [
        {
            label: 'Total Harvested',
            value: `$${totalHarvested.toFixed(2)}`,
            change: '+12.5%',
            trend: 'positive',
            icon: IconHarvested
        },
        {
            label: 'Total Compounded',
            value: `$${totalCompounded.toFixed(2)}`,
            change: '+8.3%',
            trend: 'positive',
            icon: IconCharts
        },
        {
            label: 'Realized APR',
            value: `${typeof realizedAPR === 'string' ? realizedAPR : realizedAPR?.toFixed(2)}%`,
            change: aprValue > 50 ? '+2.1%' : '+0.5%',
            trend: 'positive',
            icon: IconAPR
        },
        {
            label: 'Success Rate',
            value: `${successRate.toFixed(1)}%`,
            change: totalActions > 0 ? '+0.2%' : 'N/A',
            trend: successRate > 95 ? 'positive' : 'neutral',
            icon: IconRate
        }
    ];
    return (_jsx("div", { className: "metrics-grid", children: metrics.map((metric, i) => {
            const Icon = metric.icon;
            return (_jsxs("div", { className: "metric-card", children: [_jsx("div", { style: { marginBottom: '12px', color: 'var(--primary-light)' }, children: _jsx(Icon, { size: 28, color: "var(--primary-light)" }) }), _jsx("div", { className: "metric-label", children: metric.label }), _jsx("div", { className: "metric-value", children: metric.value }), _jsxs("div", { className: `metric-change ${metric.trend}`, children: [metric.change, " from last cycle"] })] }, i));
        }) }));
}
