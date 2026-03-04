---
name: radon-ai
description: Use Radon IDE's AI tools for React Native development - query library docs, view logs and network traffic, take screenshots, inspect component trees, and interact with the user's app
license: MIT
metadata:
  ecosystem: react-native
  author: Software Mansion
---

## What this skill provides

Radon AI is an MCP server that provides a set of tools that enhances your agent. It provides up-to-date knowledge of the React Native ecosystem, access to a comprehensive set of debugging data that is otherwise unavailable, and the ability to interact directly with your app.

We index most React Native libraries along with their relevant documentation, versions, APIs, configuration details and usage patterns to provide additional and accurate context. The knowledge database is updated daily.

## Available tools

- `get_library_description` - Returns a detailed description of a library and its use-cases.
- `query_documentation` - Returns documentation snippets relevant to the provided query.
- `reload_application` - Triggers a reload of the app running in the development emulator. Use this tool whenever you are debugging the state and want to reset it, or when the app crashes or breaks due to an interaction. There are 3 reload methods:
  - `reloadJs`: Causes the JS bundle to be reloaded. Does not trigger any rebuild or restart of the native part of the app. Use this to restart the JS state of the app.
  - `restartProcess`: Restarts the native part of the app. Use this method for resetting state of bugged native libraries or components.
  - `rebuild`: Rebuilds both the JS and the native parts of the app. Use it whenever changes are made to the native part, as such changes require a full rebuild.
- `view_application_logs` - Returns all the build, bundling and runtime logs. Use this function whenever the user has any issue with the app, if builds are failing, or when there are errors in the console.
- `view_screenshot` - Displays a screenshot of the app development viewport. Use this function whenever it is necessary to inspect what the user sees on their mobile device.
- `view_component_tree` - Displays the component tree (view hierarchy) of the running app. This tool only displays mounted components, so some parts of the project might not be visible. Use this tool when a general overview of the UI is required, such as when resolving layout issues or looking for the relation between the project file structure and component structure.
- `view_network_logs` - View the contents of the network inspector. Returns a list of all network requests made by the app, including method, URL, status, duration, and size. Use this tool to debug networking issues, inspect API calls, or verify that the app is communicating correctly with backend services. Accepts a `pageIndex` parameter (0-based index or `"latest"`).
- `view_network_request_details` - Get all details of a specific network request. Returns headers, body, and other metadata for a given request. Use this tool after `view_network_logs` to inspect a specific request in detail. Accepts a `requestId` parameter.

## When to use these tools

- When working on a React Native or Expo project that has Radon IDE running in VS Code or Cursor.
- Use `query_documentation` and `get_library_description` to look up accurate, current information about libraries instead of relying on training data.
- Use `view_application_logs` and `view_screenshot` to debug runtime errors, build failures, or UI issues.
- Use `view_component_tree` to understand the app's component hierarchy before making structural changes.
- Use `reload_application` after making code changes to verify fixes or see updates reflected in the running app.
- Use `view_network_logs` and `view_network_request_details` to debug networking issues, inspect API calls, or verify backend communication.

## Prerequisites

- Radon IDE extension must be installed and active in VS Code or Cursor.
- A React Native or Expo project must be open with Radon IDE running.
- An active Radon IDE license.

## Limitations

- Responses augmented by Radon AI are still prone to LLM errors. Verify important information before acting on it!
- The knowledge base contains documentation files only - it does not index the full source code of the libraries.
