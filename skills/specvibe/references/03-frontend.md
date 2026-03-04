# SpecVibe Reference: Frontend Development

This guide provides standards for building modern, performant, and maintainable user interfaces.

## 1. Architecture: Component-Based

- **Componentization**: Break down the UI into small, reusable, and single-purpose components.
- **Container vs. Presentational Components**: 
    - **Container Components**: Are concerned with *how things work*. They manage state, fetch data, and pass data down to presentational components. They don't have many styles.
    - **Presentational Components**: Are concerned with *how things look*. They receive data and callbacks via props and render UI. They don't know where the data comes from.

## 2. State Management

- **Start Simple**: For most applications, React's built-in hooks (`useState`, `useReducer`, `useContext`) are sufficient. Don't introduce a complex state management library (like Redux) unless you have a clear need for it (e.g., complex, deeply nested state shared across many unrelated components).
- **Server State vs. UI State**: Separate state that comes from the server (e.g., user data, product lists) from state that is local to the UI (e.g., whether a modal is open, the value of a form input). Use a dedicated library like React Query or SWR to manage server state. These libraries handle caching, re-fetching, and optimistic updates automatically.

## 3. Data Fetching

- **Use a Generated Client**: As mentioned in `01-schema-and-types.md`, generate a type-safe API client from your OpenAPI spec. This is non-negotiable.
- **Centralize API Calls**: Create a dedicated `services` or `api` directory to house all data fetching logic. Components should not make direct `fetch` calls.
- **Handle All States**: Every data request has multiple states. Your UI must gracefully handle all of them:
    - **`isLoading`**: Show a loading spinner or skeleton screen.
    - **`isError`**: Show a user-friendly error message with an option to retry.
    - **`isSuccess` with data**: Render the data.
    - **`isSuccess` with no data**: Show an empty state message (e.g., "No projects found. Create your first one!").

## 4. User Experience (UX)

- **Optimistic Updates**: For actions that are likely to succeed (e.g., liking a post, deleting an item), update the UI immediately *before* the API call completes. If the API call fails, roll back the change and show an error message. This makes the application feel much faster.
- **Accessibility (a11y)**: Build for everyone. Use semantic HTML, ensure all interactive elements are keyboard-navigable, and provide `alt` text for images.
- **Performance**: 
    - **Code Splitting**: Use dynamic `import()` to lazy-load components that are not needed for the initial render (e.g., modals, routes).
    - **Memoization**: Use `React.memo`, `useMemo`, and `useCallback` to prevent unnecessary re-renders of expensive components.
    - **Image Optimization**: Serve images in modern formats (like WebP) and at the correct size.

## 5. Styling

- **Use a Framework**: Use a utility-first CSS framework like Tailwind CSS. This encourages consistency and avoids writing custom CSS.
- **Design System**: Establish a consistent design system for colors, typography, spacing, and shadows. Store these values in your `tailwind.config.js` file and reuse them.
