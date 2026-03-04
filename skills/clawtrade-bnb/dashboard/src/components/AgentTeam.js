import { jsx as _jsx, jsxs as _jsxs, Fragment as _Fragment } from "react/jsx-runtime";
import { IconStrategy, IconRisk, IconExecution, IconLearning, IconNarrator, IconActive } from '../icons';
export function AgentTeam({ isActive, lastCycle }) {
    const agents = [
        {
            name: 'Strategy',
            icon: IconStrategy,
            role: 'Vault Monitor',
            message: 'Analyzing APR deltas...',
            status: 'active' // Always active now
        },
        {
            name: 'Risk',
            icon: IconRisk,
            role: 'Risk Manager',
            message: 'Validating risk profile...',
            status: 'active' // Always active now
        },
        {
            name: 'Execution',
            icon: IconExecution,
            role: 'TX Processor',
            message: lastCycle ? 'Transaction sent...' : 'Waiting for cycle...',
            status: lastCycle ? 'executing' : 'active'
        },
        {
            name: 'Learning',
            icon: IconLearning,
            role: 'Optimizer',
            message: 'Training models...',
            status: 'learning'
        },
        {
            name: 'Narrator',
            icon: IconNarrator,
            role: 'Explainer',
            message: 'Generating insights...',
            status: 'active' // Always active now
        }
    ];
    return (_jsxs("div", { className: "card", children: [_jsxs("div", { className: "card-header", children: [_jsx("h3", { className: "card-title", children: "Agent Team" }), _jsxs("span", { style: { fontSize: '12px', color: 'var(--text-muted)' }, children: [agents.filter(a => a.status === 'active').length, " Active"] })] }), _jsx("div", { className: "agent-team-grid", children: agents.map((agent, i) => {
                    const Icon = agent.icon;
                    return (_jsxs("div", { className: `agent-card status-${agent.status}`, children: [_jsxs("div", { className: "agent-header", children: [_jsx("div", { className: "agent-icon", children: _jsx(Icon, { size: 24, color: "var(--primary-light)" }) }), _jsxs("div", { children: [_jsx("div", { className: "agent-name", children: agent.name }), _jsx("div", { className: "agent-role", children: agent.role })] })] }), _jsx("div", { className: "agent-message", children: agent.message }), _jsxs("div", { className: `agent-status ${agent.status}`, children: [agent.status === 'active' && (_jsxs(_Fragment, { children: [_jsx(IconActive, { size: 8, color: "var(--success)", style: { marginRight: '4px' } }), " Active"] })), agent.status === 'idle' && 'Idle', agent.status === 'executing' && 'Executing', agent.status === 'learning' && 'Learning'] })] }, i));
                }) })] }));
}
