// WebMCP Core Implementation
// Enables AI agents to interact with web apps through structured tools

declare global {
  interface Navigator {
    modelContext?: {
      registerTool: (tool: WebMCPTool) => void;
      unregisterTool: (name: string) => void;
    };
  }
}

export interface WebMCPTool {
  name: string;
  description: string;
  execute: (params: Record<string, unknown>) => Promise<string | object>;
  inputSchema: object;
  outputSchema?: object;
  annotations?: {
    readOnlyHint?: string;
    title?: string;
    openWorldHint?: string;
  };
}

// Track registered tools to prevent duplicates
const registeredTools: Record<string, boolean> = {};

/**
 * Dispatch a CustomEvent and wait for completion signal
 * This is the bridge between tool execution and React state updates
 */
export function dispatchAndWait(
  eventName: string,
  detail: Record<string, unknown> = {},
  successMessage: string = "Action completed successfully",
  timeoutMs: number = 5000,
): Promise<string> {
  return new Promise((resolve, reject) => {
    const requestId = Math.random().toString(36).substring(2, 15);
    const completionEventName = `tool-completion-${requestId}`;

    // Set up timeout
    const timeoutId = setTimeout(() => {
      window.removeEventListener(completionEventName, handleCompletion);
      reject(new Error(`Timed out waiting for UI to update (${timeoutMs}ms)`));
    }, timeoutMs);

    // Listen for completion signal
    const handleCompletion = () => {
      clearTimeout(timeoutId);
      window.removeEventListener(completionEventName, handleCompletion);
      resolve(successMessage);
    };

    window.addEventListener(completionEventName, handleCompletion);

    // Dispatch action event to React component
    window.dispatchEvent(
      new CustomEvent(eventName, {
        detail: { ...detail, requestId },
      }),
    );
  });
}

/**
 * Check if WebMCP is supported in this browser
 */
export function isWebMCPSupported(): boolean {
  return typeof navigator !== "undefined" && !!navigator.modelContext;
}

/**
 * Register a tool with WebMCP
 */
export function registerTool(tool: WebMCPTool): void {
  const mc = navigator.modelContext;
  if (!mc) {
    console.warn("WebMCP not supported in this browser");
    return;
  }

  if (registeredTools[tool.name]) {
    console.warn(`Tool "${tool.name}" already registered`);
    return;
  }

  mc.registerTool(tool);
  registeredTools[tool.name] = true;
  console.log(`WebMCP: Registered tool "${tool.name}"`);
}

/**
 * Unregister a tool from WebMCP
 */
export function unregisterTool(name: string): void {
  const mc = navigator.modelContext;
  if (!mc) return;

  mc.unregisterTool(name);
  registeredTools[name] = false;
  console.log(`WebMCP: Unregistered tool "${name}"`);
}

/**
 * Unregister all tools
 */
export function unregisterAllTools(): void {
  Object.keys(registeredTools).forEach((name) => {
    if (registeredTools[name]) {
      unregisterTool(name);
    }
  });
}

// ============================================================================
// EXAMPLE TOOLS
// ============================================================================

/**
 * Search products tool
 */
export const searchProductsTool: WebMCPTool = {
  name: "searchProducts",
  description:
    "Searches for products matching a query. Updates the product listing on the page with matching results.",
  execute: async (params) => {
    return dispatchAndWait(
      "searchProducts",
      params,
      "Product search completed. Results are now displayed on the page.",
    );
  },
  inputSchema: {
    type: "object",
    properties: {
      query: {
        type: "string",
        description: "The search query to find products by name or category.",
      },
      maxPrice: {
        type: "number",
        description: "Optional maximum price filter.",
      },
      category: {
        type: "string",
        enum: ["electronics", "clothing", "books", "home"],
        description: "Optional category filter.",
      },
    },
    required: ["query"],
  },
  outputSchema: {
    type: "string",
    description: "A confirmation message indicating search results are displayed.",
  },
  annotations: {
    readOnlyHint: "false",
  },
};

/**
 * View cart tool
 */
export const viewCartTool: WebMCPTool = {
  name: "viewCart",
  description:
    "Returns the current contents of the shopping cart, including item names, quantities, and prices.",
  execute: async () => {
    return dispatchAndWait("viewCart", {}, "Cart contents retrieved.", 3000);
  },
  inputSchema: {},
  outputSchema: {
    type: "string",
    description: "A confirmation that cart contents are displayed.",
  },
  annotations: {
    readOnlyHint: "true",
  },
};

/**
 * Remove from cart tool
 */
export const removeFromCartTool: WebMCPTool = {
  name: "removeFromCart",
  description:
    "Removes an item from the shopping cart by its product ID. The cart display updates automatically.",
  execute: async (params) => {
    return dispatchAndWait(
      "removeFromCart",
      params,
      `Item "${params.productId}" removed from cart.`,
    );
  },
  inputSchema: {
    type: "object",
    properties: {
      productId: {
        type: "string",
        description: "The unique identifier of the product to remove.",
      },
    },
    required: ["productId"],
  },
  outputSchema: {
    type: "string",
    description: "Confirmation that the item was removed.",
  },
  annotations: {
    readOnlyHint: "false",
  },
};

/**
 * Navigate to page tool
 */
export const navigateTool: WebMCPTool = {
  name: "navigateTo",
  description: "Navigates to a specific page in the application.",
  execute: async (params) => {
    return dispatchAndWait(
      "navigateTo",
      params,
      `Navigated to ${params.path}.`,
    );
  },
  inputSchema: {
    type: "object",
    properties: {
      path: {
        type: "string",
        description: "The path to navigate to (e.g., /products, /cart).",
      },
    },
    required: ["path"],
  },
  annotations: {
    readOnlyHint: "false",
  },
};

/**
 * Submit form tool
 */
export const submitFormTool: WebMCPTool = {
  name: "submitForm",
  description: "Submits a form with the provided data.",
  execute: async (params) => {
    return dispatchAndWait(
      "submitForm",
      params,
      "Form submitted successfully.",
    );
  },
  inputSchema: {
    type: "object",
    properties: {
      formId: {
        type: "string",
        description: "The ID of the form to submit.",
      },
      data: {
        type: "object",
        description: "The form data as key-value pairs.",
      },
    },
    required: ["formId", "data"],
  },
  annotations: {
    readOnlyHint: "false",
  },
};

// ============================================================================
// TOOL REGISTRATION HELPERS
// ============================================================================

export function registerProductTools(): void {
  registerTool(searchProductsTool);
}

export function unregisterProductTools(): void {
  unregisterTool(searchProductsTool.name);
}

export function registerCartTools(): void {
  registerTool(viewCartTool);
  registerTool(removeFromCartTool);
}

export function unregisterCartTools(): void {
  unregisterTool(viewCartTool.name);
  unregisterTool(removeFromCartTool.name);
}

export function registerNavigationTools(): void {
  registerTool(navigateTool);
}

export function unregisterNavigationTools(): void {
  unregisterTool(navigateTool.name);
}

export function registerFormTools(): void {
  registerTool(submitFormTool);
}

export function unregisterFormTools(): void {
  unregisterTool(submitFormTool.name);
}
