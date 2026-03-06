import { WebMCPTool, dispatchAndWait } from "@/lib/webmcp";

/**
 * Authentication tools
 * Handle login, logout, and user session management
 */
export const loginTool: WebMCPTool = {
  name: "login",
  description: "Authenticates a user with email and password",
  execute: async (params) => {
    return dispatchAndWait(
      "login",
      params,
      "User logged in successfully",
    );
  },
  inputSchema: {
    type: "object",
    properties: {
      email: {
        type: "string",
        format: "email",
        description: "User's email address",
      },
      password: {
        type: "string",
        description: "User's password",
      },
      rememberMe: {
        type: "boolean",
        description: "Whether to remember the login",
      },
    },
    required: ["email", "password"],
  },
  annotations: {
    readOnlyHint: "false",
  },
};

export const logoutTool: WebMCPTool = {
  name: "logout",
  description: "Logs out the current user",
  execute: async () => {
    return dispatchAndWait("logout", {}, "User logged out successfully");
  },
  inputSchema: {},
  annotations: {
    readOnlyHint: "false",
  },
};

export const registerUserTool: WebMCPTool = {
  name: "registerUser",
  description: "Registers a new user account",
  execute: async (params) => {
    return dispatchAndWait(
      "registerUser",
      params,
      "User registered successfully",
    );
  },
  inputSchema: {
    type: "object",
    properties: {
      email: {
        type: "string",
        format: "email",
        description: "User's email address",
      },
      password: {
        type: "string",
        minLength: 8,
        description: "User's password (min 8 characters)",
      },
      name: {
        type: "string",
        description: "User's full name",
      },
    },
    required: ["email", "password", "name"],
  },
  annotations: {
    readOnlyHint: "false",
  },
};

export const resetPasswordTool: WebMCPTool = {
  name: "resetPassword",
  description: "Initiates password reset for a user",
  execute: async (params) => {
    return dispatchAndWait(
      "resetPassword",
      params,
      "Password reset email sent",
    );
  },
  inputSchema: {
    type: "object",
    properties: {
      email: {
        type: "string",
        format: "email",
        description: "User's email address",
      },
    },
    required: ["email"],
  },
  annotations: {
    readOnlyHint: "false",
  },
};
