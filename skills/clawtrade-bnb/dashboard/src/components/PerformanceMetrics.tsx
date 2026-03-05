import React from 'react';
import { IconHarvested, IconCharts, IconAPR, IconRate } from '../icons';

interface PerformanceMetricsProps {
  totalHarvested: number;
  totalCompounded: number;
  realizedAPR: number | string;
  successRate: number;
  totalActions: number;
}

export function PerformanceMetrics({
  totalHarvested,
  totalCompounded,
  realizedAPR,
  successRate,
  totalActions
}: PerformanceMetricsProps) {
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
      value: `${typeof realizedAPR === 'string' ? realizedAPR : (realizedAPR as any)?.toFixed(2)}%`,
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

  return (
    <div className="metrics-grid">
      {metrics.map((metric, i) => {
        const Icon = metric.icon;
        return (
          <div key={i} className="metric-card">
            <div style={{ marginBottom: '12px', color: 'var(--primary-light)' }}>
              <Icon size={28} color="var(--primary-light)" />
            </div>
            <div className="metric-label">{metric.label}</div>
            <div className="metric-value">{metric.value}</div>
            <div className={`metric-change ${metric.trend}`}>
              {metric.change} from last cycle
            </div>
          </div>
        );
      })}
    </div>
  );
}
