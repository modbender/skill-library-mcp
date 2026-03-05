import { useState, useEffect } from "react";
import { useDeckInit } from "./hooks";
import { useDeckStore } from "./lib/store";
import { AgentColumn } from "./components/AgentColumn";
import { TopBar } from "./components/TopBar";
import { StatusBar } from "./components/StatusBar";
import { AddAgentModal } from "./components/AddAgentModal";
import type { AgentConfig } from "./types";
import "./App.css";

/**
 * Agent column configuration.
 *
 * You're running default single-agent mode, so there's one agent: "main".
 * The Gateway routes all messages to the default workspace at:
 *   /Users/austenallred/.openclaw/workspace
 *
 * To add more columns later, set up multi-agent in openclaw.json:
 *   { "agents": { "list": [
 *     { "id": "research", "workspace": "~/.openclaw/workspace-research" },
 *     { "id": "codegen",  "workspace": "~/.openclaw/workspace-codegen" },
 *   ]}}
 *
 * Then add matching entries here.
 */
const DEFAULT_AGENTS: AgentConfig[] = [
  {
    id: "main",
    name: "Molty",
    icon: "🦞",
    accent: "#22d3ee",
    context: "Primary assistant",
    model: "claude-sonnet-4-5",
  },
  // ─── Add more columns when you set up multi-agent routing ───
  // {
  //   id: "research",
  //   name: "Research Agent",
  //   icon: "◎",
  //   accent: "#a78bfa",
  //   context: "Deep web research & synthesis",
  //   model: "claude-opus-4-6",
  // },
  // {
  //   id: "codegen",
  //   name: "Code Generator",
  //   icon: "⟐",
  //   accent: "#34d399",
  //   context: "Full-stack code generation",
  //   model: "claude-sonnet-4-5",
  // },
];

function getGatewayConfig() {
  const params = new URLSearchParams(window.location.search);
  let gatewayUrl =
    params.get("gateway") ||
    import.meta.env.VITE_GATEWAY_URL ||
    "ws://127.0.0.1:18789";

  // Resolve relative paths (e.g. "/ws") to full WebSocket URLs
  if (gatewayUrl.startsWith("/")) {
    const proto = window.location.protocol === "https:" ? "wss:" : "ws:";
    gatewayUrl = `${proto}//${window.location.host}${gatewayUrl}`;
  }

  return {
    gatewayUrl,
    token:
      params.get("token") ||
      import.meta.env.VITE_GATEWAY_TOKEN ||
      undefined,
  };
}

export default function App() {
  const [activeTab, setActiveTab] = useState("All Agents");
  const [showAddModal, setShowAddModal] = useState(false);
  const columnOrder = useDeckStore((s) => s.columnOrder);
  const addAgent = useDeckStore((s) => s.addAgent);

  const { gatewayUrl, token } = getGatewayConfig();

  useDeckInit({
    gatewayUrl,
    token,
    agents: DEFAULT_AGENTS,
  });

  // Cmd+1-9 to focus column inputs
  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if (e.metaKey && e.key >= "1" && e.key <= "9") {
        const index = parseInt(e.key, 10) - 1;
        const input = document.querySelector<HTMLInputElement>(
          `[data-deck-input="${index}"]`
        );
        if (input) {
          e.preventDefault();
          input.focus();
        }
      } else if (e.metaKey && e.key === "k") {
        e.preventDefault();
        setShowAddModal((prev) => !prev);
      }
    };
    window.addEventListener("keydown", handleKeyDown);
    return () => window.removeEventListener("keydown", handleKeyDown);
  }, []);

  return (
    <div className="deck-root">
      <TopBar
        activeTab={activeTab}
        onTabChange={setActiveTab}
        onAddAgent={() => setShowAddModal(true)}
      />

      <div className="deck-columns">
        {columnOrder.map((agentId, index) => (
          <AgentColumn key={agentId} agentId={agentId} columnIndex={index} />
        ))}
      </div>

      <StatusBar />

      {showAddModal && (
        <AddAgentModal
          onClose={() => setShowAddModal(false)}
          onCreate={addAgent}
        />
      )}
    </div>
  );
}
