import { jsx as _jsx, Fragment as _Fragment, jsxs as _jsxs } from "react/jsx-runtime";
import { useState, useEffect } from 'react';
import { Sidebar } from './components/Sidebar';
import { Topbar } from './components/Topbar';
import { Operator } from './components/Operator';
import { AgentTeam } from './components/AgentTeam';
import { ActivityFeed } from './components/ActivityFeed';
import { PerformanceMetrics } from './components/PerformanceMetrics';
import { Explainability } from './components/Explainability';
import './design-system.css';
export default function App() {
    const [records, setRecords] = useState([]);
    const [metrics, setMetrics] = useState(null);
    const [status, setStatus] = useState('Connecting...');
    const [isActive, setIsActive] = useState(false);
    const [selectedAction, setSelectedAction] = useState(null);
    const [activeTab, setActiveTab] = useState('operator');
    useEffect(() => {
        const fetchRecords = async () => {
            try {
                const apiBase = typeof window !== 'undefined' ? window.location.origin : 'http://localhost:3001';
                const res = await fetch(`${apiBase}/api/logs`);
                const data = await res.json();
                const validData = Array.isArray(data) ? data.filter((r) => r && r.action) : [];
                setRecords(validData.slice(-20));
                if (validData.length > 0) {
                    const harvested = validData
                        .filter((r) => r.action?.includes('HARVEST'))
                        .reduce((sum, r) => sum + (parseFloat(String(r.rewards_usd)) || 0), 0);
                    const compounded = validData
                        .filter((r) => r.action?.includes('COMPOUND'))
                        .reduce((sum, r) => sum + (parseFloat(String(r.rewards_usd)) || 0), 0);
                    setMetrics({
                        totalHarvested: harvested,
                        totalCompounded: compounded,
                        realizedAPR: compounded > 0 ? ((compounded / 1000) * 365 * 100).toFixed(2) : '0',
                        vaults: validData.reduce((acc, r) => {
                            const id = r.vault_id || r.vault || 'unknown';
                            if (!acc[id])
                                acc[id] = { actions: 0, rewards: 0 };
                            acc[id].actions += 1;
                            acc[id].rewards += parseFloat(String(r.rewards_usd)) || 0;
                            return acc;
                        }, {})
                    });
                }
                setStatus('Live');
            }
            catch (err) {
                console.error('Error:', err);
                setStatus('Error');
            }
        };
        fetchRecords();
        const interval = setInterval(fetchRecords, 30000);
        return () => clearInterval(interval);
    }, []);
    const getLastDecisionTime = () => {
        if (records.length > 0) {
            return records[records.length - 1].timestamp;
        }
        return undefined;
    };
    const successCount = records.filter(r => r.status === 'success').length;
    const successRate = records.length > 0 ? (successCount / records.length) * 100 : 0;
    return (_jsxs("div", { className: "app-container", children: [_jsx(Sidebar, { activeTab: activeTab, onTabChange: setActiveTab }), _jsxs("div", { className: "main-content", children: [_jsx(Topbar, { status: status, isActive: isActive, lastDecisionTime: getLastDecisionTime() }), _jsxs("div", { className: "main-panel", children: [activeTab === 'operator' && (_jsxs(_Fragment, { children: [_jsx(Operator, { onActivate: (profile) => {
                                            setIsActive(true);
                                            console.log(`Agent activated with ${profile} profile`);
                                        }, isActive: isActive }), _jsx(AgentTeam, { isActive: isActive, lastCycle: records[records.length - 1] })] })), activeTab === 'activity' && (_jsxs(_Fragment, { children: [_jsx("div", { className: "card", children: _jsxs("div", { className: "card-header", children: [_jsx("h3", { className: "card-title", children: "Live Activity Stream" }), _jsxs("span", { style: { fontSize: '12px', color: 'var(--text-muted)' }, children: [records.length, " total actions"] })] }) }), _jsx(ActivityFeed, { records: records, onSelectAction: setSelectedAction })] })), activeTab === 'analytics' && (_jsxs(_Fragment, { children: [_jsx("div", { style: { marginBottom: '24px' }, children: _jsx("h2", { style: { color: 'var(--text-primary)', marginBottom: '16px' }, children: "Analytics Dashboard" }) }), metrics && (_jsx(PerformanceMetrics, { totalHarvested: metrics.totalHarvested, totalCompounded: metrics.totalCompounded, realizedAPR: metrics.realizedAPR, successRate: successRate, totalActions: records.length })), _jsx(ActivityFeed, { records: records, onSelectAction: setSelectedAction })] })), activeTab === 'settings' && (_jsxs("div", { className: "card", children: [_jsx("div", { className: "card-header", children: _jsx("h3", { className: "card-title", children: "Settings" }) }), _jsxs("div", { style: { padding: '24px' }, children: [_jsxs("div", { style: { marginBottom: '20px' }, children: [_jsx("h4", { style: { color: 'var(--text-muted)', marginBottom: '12px' }, children: "Network" }), _jsx("div", { style: { padding: '12px', backgroundColor: 'var(--bg-hover)', borderRadius: 'var(--radius-md)', fontSize: '14px' }, children: "BNB Testnet (0xae13d989daC2f0dEFF460025B5D3d3054f687FB4)" })] }), _jsxs("div", { style: { marginBottom: '20px' }, children: [_jsx("h4", { style: { color: 'var(--text-muted)', marginBottom: '12px' }, children: "Execution Settings" }), _jsxs("div", { style: { padding: '12px', backgroundColor: 'var(--bg-hover)', borderRadius: 'var(--radius-md)', fontSize: '14px' }, children: [_jsx("div", { style: { marginBottom: '8px' }, children: "\u2022 Cycle Interval: 60 seconds" }), _jsx("div", { style: { marginBottom: '8px' }, children: "\u2022 Min Gas Balance: $0.05" }), _jsx("div", { children: "\u2022 Auto-Reinvest: Enabled" })] })] }), _jsxs("div", { children: [_jsx("h4", { style: { color: 'var(--text-muted)', marginBottom: '12px' }, children: "System Info" }), _jsxs("div", { style: { padding: '12px', backgroundColor: 'var(--bg-hover)', borderRadius: 'var(--radius-md)', fontSize: '12px', color: 'var(--text-muted)' }, children: [_jsxs("div", { style: { marginBottom: '6px' }, children: ["Status: ", status] }), _jsxs("div", { style: { marginBottom: '6px' }, children: ["Total Cycles: ", records.length] }), _jsxs("div", { children: ["Success Rate: ", successRate.toFixed(1), "%"] })] })] })] })] })), !['operator', 'activity', 'analytics', 'settings'].includes(activeTab) && (_jsxs(_Fragment, { children: [_jsx(Operator, { onActivate: (profile) => {
                                            setIsActive(true);
                                            console.log(`Agent activated with ${profile} profile`);
                                        }, isActive: isActive }), _jsx(AgentTeam, { isActive: isActive, lastCycle: records[records.length - 1] }), metrics && (_jsx(PerformanceMetrics, { totalHarvested: metrics.totalHarvested, totalCompounded: metrics.totalCompounded, realizedAPR: metrics.realizedAPR, successRate: successRate, totalActions: records.length })), _jsx(ActivityFeed, { records: records, onSelectAction: setSelectedAction })] }))] })] }), selectedAction && (_jsxs("div", { children: [_jsx("div", { style: {
                            position: 'fixed',
                            left: 0,
                            top: 0,
                            right: 0,
                            bottom: 0,
                            backgroundColor: 'rgba(0, 0, 0, 0.6)',
                            zIndex: 999
                        }, onClick: () => setSelectedAction(null) }), _jsx(Explainability, { action: selectedAction, onClose: () => setSelectedAction(null) })] }))] }));
}
