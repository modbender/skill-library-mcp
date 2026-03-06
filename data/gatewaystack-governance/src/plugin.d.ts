/**
 * GatewayStack Governance — OpenClaw Plugin
 *
 * Registers a `before_tool_call` hook that automatically runs governance
 * checks on every tool invocation. The agent cannot bypass this — it runs
 * at the process level before any tool executes.
 *
 * Identity mapping uses OpenClaw agent IDs (e.g. "main", "ops", "dev")
 * rather than human users, since OpenClaw is a single-user personal AI.
 */
declare const plugin: {
    id: string;
    name: string;
    description: string;
    register(api: any): void;
};
export default plugin;
