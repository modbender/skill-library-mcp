import { jsx as _jsx, jsxs as _jsxs } from "react/jsx-runtime";
import { IconOperator, IconActivity, IconAnalytics, IconSettings } from '../icons';
export function Sidebar({ activeTab, onTabChange }) {
    const navItems = [
        { id: 'operator', label: 'Operator', icon: IconOperator },
        { id: 'activity', label: 'Live Activity', icon: IconActivity },
        { id: 'analytics', label: 'Analytics', icon: IconAnalytics },
        { id: 'settings', label: 'Settings', icon: IconSettings }
    ];
    return (_jsxs("div", { className: "sidebar", children: [_jsxs("div", { className: "sidebar-header", children: [_jsx("img", { src: "/clawtrade-logo.jpg", alt: "ClawTrade", style: { width: '56px', height: '56px', marginBottom: '12px', borderRadius: 'var(--radius-md)' } }), _jsx("div", { className: "sidebar-logo", children: "ClawTrade" }), _jsx("div", { className: "sidebar-tagline", children: "AI DeFi Operator" })] }), _jsx("nav", { className: "sidebar-nav", children: navItems.map(item => {
                    const Icon = item.icon;
                    return (_jsxs("button", { className: `nav-item ${activeTab === item.id ? 'active' : ''}`, onClick: () => onTabChange(item.id), children: [_jsx("span", { className: "nav-icon", children: _jsx(Icon, { size: 20 }) }), _jsx("span", { children: item.label })] }, item.id));
                }) }), _jsxs("div", { style: { padding: '24px 12px', borderTop: '1px solid var(--border)' }, children: [_jsx("div", { style: { fontSize: '12px', color: 'var(--text-dark)', marginBottom: '8px' }, children: "SYSTEM STATUS" }), _jsxs("div", { style: { padding: '12px', backgroundColor: 'var(--bg-hover)', borderRadius: 'var(--radius-md)', fontSize: '11px' }, children: [_jsx("div", { style: { marginBottom: '6px' }, children: "Uptime: 18h 32m" }), _jsx("div", { children: "Actions: 847" })] })] })] }));
}
