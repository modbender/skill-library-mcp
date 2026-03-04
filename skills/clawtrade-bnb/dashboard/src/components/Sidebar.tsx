import React from 'react';
import { IconOperator, IconActivity, IconAnalytics, IconSettings } from '../icons';

interface SidebarProps {
  activeTab: string;
  onTabChange: (tab: string) => void;
}

export function Sidebar({ activeTab, onTabChange }: SidebarProps) {
  const navItems = [
    { id: 'operator', label: 'Operator', icon: IconOperator },
    { id: 'activity', label: 'Live Activity', icon: IconActivity },
    { id: 'analytics', label: 'Analytics', icon: IconAnalytics },
    { id: 'settings', label: 'Settings', icon: IconSettings }
  ];

  return (
    <div className="sidebar">
      <div className="sidebar-header">
        <img 
          src="/clawtrade-logo.jpg" 
          alt="ClawTrade" 
          style={{ width: '56px', height: '56px', marginBottom: '12px', borderRadius: 'var(--radius-md)' }}
        />
        <div className="sidebar-logo">ClawTrade</div>
        <div className="sidebar-tagline">AI DeFi Operator</div>
      </div>

      <nav className="sidebar-nav">
        {navItems.map(item => {
          const Icon = item.icon;
          return (
            <button
              key={item.id}
              className={`nav-item ${activeTab === item.id ? 'active' : ''}`}
              onClick={() => onTabChange(item.id)}
            >
              <span className="nav-icon"><Icon size={20} /></span>
              <span>{item.label}</span>
            </button>
          );
        })}
      </nav>

      <div style={{ padding: '24px 12px', borderTop: '1px solid var(--border)' }}>
        <div style={{ fontSize: '12px', color: 'var(--text-dark)', marginBottom: '8px' }}>
          SYSTEM STATUS
        </div>
        <div style={{ padding: '12px', backgroundColor: 'var(--bg-hover)', borderRadius: 'var(--radius-md)', fontSize: '11px' }}>
          <div style={{ marginBottom: '6px' }}>Uptime: 18h 32m</div>
          <div>Actions: 847</div>
        </div>
      </div>
    </div>
  );
}
