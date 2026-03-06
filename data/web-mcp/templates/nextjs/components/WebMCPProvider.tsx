// WebMCP Provider Component
// Wrap your app with this to enable WebMCP throughout

"use client";

import React, { createContext, useContext, ReactNode } from "react";
import { WebMCPTool } from "@/lib/webmcp";

interface WebMCPContextValue {
  isSupported: boolean;
  tools: WebMCPTool[];
}

const WebMCPContext = createContext<WebMCPContextValue | null>(null);

interface WebMCPProviderProps {
  children: ReactNode;
  tools?: WebMCPTool[];
}

export function WebMCPProvider({ children, tools = [] }: WebMCPProviderProps) {
  // Check if WebMCP is supported
  const isSupported =
    typeof navigator !== "undefined" && !!navigator.modelContext;

  return (
    <WebMCPContext.Provider value={{ isSupported, tools }}>
      {children}
    </WebMCPContext.Provider>
  );
}

export function useWebMCPContext() {
  const context = useContext(WebMCPContext);
  if (!context) {
    throw new Error(
      "useWebMCPContext must be used within a WebMCPProvider",
    );
  }
  return context;
}
