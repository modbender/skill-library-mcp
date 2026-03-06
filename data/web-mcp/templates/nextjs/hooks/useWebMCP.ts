// React Hook for WebMCP
// Simplifies tool registration and event handling in React components

import { useEffect, useState, useCallback } from "react";
import {
  WebMCPTool,
  registerTool,
  unregisterTool,
  dispatchAndWait,
  isWebMCPSupported,
} from "@/lib/webmcp";

interface UseWebMCPOptions {
  tools?: WebMCPTool[];
  timeout?: number;
}

interface UseWebMCPReturn {
  isSupported: boolean;
  completedRequestId: string | null;
  setCompletedRequestId: (id: string | null) => void;
  dispatchAction: (
    eventName: string,
    detail?: Record<string, unknown>,
    successMessage?: string,
  ) => Promise<string>;
  register: (tool: WebMCPTool) => void;
  unregister: (name: string) => void;
}

/**
 * React hook for WebMCP integration
 * Handles tool registration, event dispatching, and completion signaling
 */
export function useWebMCP(options: UseWebMCPOptions = {}): UseWebMCPReturn {
  const { tools = [], timeout = 5000 } = options;
  const [completedRequestId, setCompletedRequestId] = useState<string | null>(
    null,
  );
  const [isSupported, setIsSupported] = useState(false);

  // Check WebMCP support on mount
  useEffect(() => {
    setIsSupported(isWebMCPSupported());
  }, []);

  // Register tools on mount, unregister on cleanup
  useEffect(() => {
    if (!isSupported || tools.length === 0) return;

    tools.forEach(registerTool);

    return () => {
      tools.forEach((tool) => unregisterTool(tool.name));
    };
  }, [isSupported, tools]);

  // Signal completion after React re-renders
  useEffect(() => {
    if (completedRequestId) {
      window.dispatchEvent(
        new CustomEvent(`tool-completion-${completedRequestId}`),
      );
      setCompletedRequestId(null);
    }
  }, [completedRequestId]);

  // Dispatch action and wait for completion
  const dispatchAction = useCallback(
    async (
      eventName: string,
      detail: Record<string, unknown> = {},
      successMessage: string = "Action completed",
    ): Promise<string> => {
      return dispatchAndWait(eventName, detail, successMessage, timeout);
    },
    [timeout],
  );

  // Manual register/unregister
  const register = useCallback((tool: WebMCPTool) => {
    registerTool(tool);
  }, []);

  const unregister = useCallback((name: string) => {
    unregisterTool(name);
  }, []);

  return {
    isSupported,
    completedRequestId,
    setCompletedRequestId,
    dispatchAction,
    register,
    unregister,
  };
}

/**
 * Hook for listening to WebMCP events
 */
export function useWebMCPEvent(
  eventName: string,
  handler: (event: CustomEvent) => void,
  deps: React.DependencyList = [],
) {
  useEffect(() => {
    const wrappedHandler = (event: Event) => {
      handler(event as CustomEvent);
    };

    window.addEventListener(eventName, wrappedHandler);
    return () => {
      window.removeEventListener(eventName, wrappedHandler);
    };
  }, [eventName, ...deps]);
}

/**
 * Hook for creating a tool executor
 */
export function useToolExecutor(
  toolName: string,
  handler: (params: Record<string, unknown>) => void,
) {
  const [completedRequestId, setCompletedRequestId] = useState<string | null>(
    null,
  );

  // Signal completion after handler runs
  useEffect(() => {
    if (completedRequestId) {
      window.dispatchEvent(
        new CustomEvent(`tool-completion-${completedRequestId}`),
      );
      setCompletedRequestId(null);
    }
  }, [completedRequestId]);

  // Listen for tool execution events
  useEffect(() => {
    const handleExecute = (event: CustomEvent) => {
      const { requestId, ...params } = event.detail;
      handler(params);
      if (requestId) {
        setCompletedRequestId(requestId);
      }
    };

    window.addEventListener(toolName, handleExecute as EventListener);
    return () => {
      window.removeEventListener(toolName, handleExecute as EventListener);
    };
  }, [toolName, handler]);

  return { completedRequestId };
}
