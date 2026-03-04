import { createContext, useContext, useState, useEffect } from 'react';
import type { ReactNode } from 'react';

const AGENT_API_KEY_STORAGE = 'moltfundme_agent_api_key';

interface AgentAuthContextType {
  agentApiKey: string | null;
  setAgentApiKey: (key: string | null) => void;
  isAgentAuthenticated: boolean;
}

const AgentAuthContext = createContext<AgentAuthContextType | undefined>(undefined);

export function AgentAuthProvider({ children }: { children: ReactNode }) {
  const [agentApiKey, setAgentApiKeyState] = useState<string | null>(null);

  useEffect(() => {
    const stored = localStorage.getItem(AGENT_API_KEY_STORAGE);
    if (stored) {
      setAgentApiKeyState(stored);
    }
  }, []);

  const setAgentApiKey = (key: string | null) => {
    if (key) {
      localStorage.setItem(AGENT_API_KEY_STORAGE, key);
      setAgentApiKeyState(key);
    } else {
      localStorage.removeItem(AGENT_API_KEY_STORAGE);
      setAgentApiKeyState(null);
    }
  };

  return (
    <AgentAuthContext.Provider
      value={{
        agentApiKey,
        setAgentApiKey,
        isAgentAuthenticated: !!agentApiKey,
      }}
    >
      {children}
    </AgentAuthContext.Provider>
  );
}

export function useAgentAuth() {
  const context = useContext(AgentAuthContext);
  if (context === undefined) {
    throw new Error('useAgentAuth must be used within an AgentAuthProvider');
  }
  return context;
}
