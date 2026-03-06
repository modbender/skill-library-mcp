---
name: supernal-interface
description: Universal AI Interface framework for making applications AI-controllable. Use when adding AI tool decorators, setting up chat adapters, creating AI-callable functions, or integrating CopilotKit.
---

# Supernal Interface - AI Controllability Framework

## Installation

```bash
npm install @supernal/interface
```

## Core Concept

Decorate functions → AI can call them with full type safety.

## Quick Start

### 1. Decorate Functions

```typescript
import { Tool } from '@supernal/interface';

class TodoApp {
  @Tool({
    name: 'add_todo',
    description: 'Add a new todo item',
    category: 'productivity'
  })
  async addTodo(text: string): Promise<Todo> {
    return this.db.create({ text, done: false });
  }

  @Tool({
    name: 'complete_todo',
    description: 'Mark a todo as complete'
  })
  async completeTodo(id: string): Promise<void> {
    await this.db.update(id, { done: true });
  }
}
```

### 2. Set Up Adapter

```typescript
import { createCopilotKitAdapter, ChatUIProvider } from '@supernal/interface';

const adapter = createCopilotKitAdapter({
  autoRegisterTools: true,
  autoRegisterReadables: true
});

function App() {
  return (
    <ChatUIProvider adapter={adapter}>
      <YourApp />
    </ChatUIProvider>
  );
}
```

### 3. Done

AI assistants can now discover and call your decorated functions.

## Decorators

| Decorator | Purpose |
|-----------|---------|
| `@Tool` | Expose function as AI-callable tool |
| `@ToolProvider` | Class containing multiple tools |
| `@Component` | React component with AI context |

## Adapters

### CopilotKit (recommended)
```typescript
import { createCopilotKitAdapter } from '@supernal/interface';

const adapter = createCopilotKitAdapter({
  autoRegisterTools: true
});
```

### Custom Adapter
```typescript
import { ChatUIAdapter } from '@supernal/interface';

class MyAdapter implements ChatUIAdapter {
  name = 'my-adapter';
  registerTools(tools) { /* convert to your format */ }
  render(props) { return <MyChat {...props} />; }
}
```

## React Hooks

```typescript
import { useToolBinding, usePersistedState, useChatWithContext } from '@supernal/interface';

// Bind a tool to component state
const [todos, setTodos] = useToolBinding('todos', []);

// Persist state across sessions
const [prefs, setPrefs] = usePersistedState('user-prefs', defaults);

// Chat with app context
const { messages, send } = useChatWithContext();
```

## Storage Adapters

```typescript
import { StateManager, LocalStorageAdapter } from '@supernal/interface/storage';

const storage = StateManager.getInstance('myapp', new LocalStorageAdapter());
await storage.setState('user', { name: 'Alice' });
```

## Testing

```typescript
import { GherkinParser, TestRunner } from '@supernal/interface/testing';

const feature = GherkinParser.parseFeature(gherkinText);
const tests = await TestRunner.generateTests({ framework: 'jest' });
```

## Enterprise Features

Available at supernal.ai/enterprise:
- Auto test generation from decorators
- Story system (50-80% performance boost)
- Architecture visualization
- Multi-model routing
- Audit & compliance logging
