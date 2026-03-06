import { WebMCPTool, dispatchAndWait } from "@/lib/webmcp";

/**
 * Dashboard widget tool
 * Allows agents to interact with dashboard widgets
 */
export const updateWidgetTool: WebMCPTool = {
  name: "updateWidget",
  description: "Updates a dashboard widget with new data or configuration",
  execute: async (params) => {
    return dispatchAndWait(
      "updateWidget",
      params,
      `Widget "${params.widgetId}" updated successfully`,
    );
  },
  inputSchema: {
    type: "object",
    properties: {
      widgetId: {
        type: "string",
        description: "Unique identifier of the widget to update",
      },
      data: {
        type: "object",
        description: "New data to display in the widget",
      },
      config: {
        type: "object",
        description: "Optional configuration changes",
      },
    },
    required: ["widgetId"],
  },
  annotations: {
    readOnlyHint: "false",
  },
};

export const refreshWidgetTool: WebMCPTool = {
  name: "refreshWidget",
  description: "Refreshes a widget to fetch latest data",
  execute: async (params) => {
    return dispatchAndWait(
      "refreshWidget",
      params,
      `Widget "${params.widgetId}" refreshed`,
    );
  },
  inputSchema: {
    type: "object",
    properties: {
      widgetId: {
        type: "string",
        description: "Unique identifier of the widget to refresh",
      },
    },
    required: ["widgetId"],
  },
  annotations: {
    readOnlyHint: "false",
  },
};

export const addWidgetTool: WebMCPTool = {
  name: "addWidget",
  description: "Adds a new widget to the dashboard",
  execute: async (params) => {
    return dispatchAndWait(
      "addWidget",
      params,
      `Widget "${params.type}" added to dashboard`,
    );
  },
  inputSchema: {
    type: "object",
    properties: {
      type: {
        type: "string",
        enum: ["chart", "stats", "list", "calendar", "weather", "clock"],
        description: "Type of widget to add",
      },
      position: {
        type: "object",
        properties: {
          x: { type: "number" },
          y: { type: "number" },
          w: { type: "number" },
          h: { type: "number" },
        },
        description: "Position and size on the dashboard",
      },
      config: {
        type: "object",
        description: "Widget-specific configuration",
      },
    },
    required: ["type"],
  },
  annotations: {
    readOnlyHint: "false",
  },
};

export const removeWidgetTool: WebMCPTool = {
  name: "removeWidget",
  description: "Removes a widget from the dashboard",
  execute: async (params) => {
    return dispatchAndWait(
      "removeWidget",
      params,
      `Widget "${params.widgetId}" removed`,
    );
  },
  inputSchema: {
    type: "object",
    properties: {
      widgetId: {
        type: "string",
        description: "Unique identifier of the widget to remove",
      },
    },
    required: ["widgetId"],
  },
  annotations: {
    readOnlyHint: "false",
  },
};
