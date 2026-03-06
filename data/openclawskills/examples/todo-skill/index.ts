/**
 * Todo Skill
 * Simple todo list with persistent storage
 */

interface TodoConfig {
  storagePath?: string;
}

interface SkillContext {
  userId: string;
  memory: MemoryStore;
  logger: Logger;
}

interface MemoryStore {
  get(key: string): Promise<any>;
  set(key: string, value: any): Promise<void>;
}

interface Logger {
  debug(msg: string): void;
  info(msg: string): void;
}

interface Todo {
  id: string;
  text: string;
  completed: boolean;
  createdAt: string;
  completedAt?: string;
  priority: 'low' | 'medium' | 'high';
}

interface TodoList {
  todos: Todo[];
  lastModified: string;
}

export class TodoSkill {
  private context: SkillContext;
  private storageKey: string;

  constructor(config: TodoConfig, context: SkillContext) {
    this.context = context;
    this.storageKey = `todos:${context.userId}`;
  }

  private async getTodos(): Promise<Todo[]> {
    const data = await this.context.memory.get(this.storageKey);
    return data?.todos || [];
  }

  private async saveTodos(todos: Todo[]): Promise<void> {
    const list: TodoList = {
      todos,
      lastModified: new Date().toISOString()
    };
    await this.context.memory.set(this.storageKey, list);
  }

  /**
   * Add a new todo
   */
  async addTodo(text: string, priority: 'low' | 'medium' | 'high' = 'medium'): Promise<Todo> {
    this.context.logger.info(`Adding todo: ${text}`);

    const todo: Todo = {
      id: Date.now().toString(),
      text,
      completed: false,
      createdAt: new Date().toISOString(),
      priority
    };

    const todos = await this.getTodos();
    todos.push(todo);
    await this.saveTodos(todos);

    return todo;
  }

  /**
   * List all todos
   */
  async listTodos(filter?: 'all' | 'active' | 'completed'): Promise<Todo[]> {
    const todos = await this.getTodos();
    
    switch (filter) {
      case 'active':
        return todos.filter(t => !t.completed);
      case 'completed':
        return todos.filter(t => t.completed);
      default:
        return todos;
    }
  }

  /**
   * Mark a todo as complete
   */
  async completeTodo(id: string): Promise<Todo | null> {
    const todos = await this.getTodos();
    const todo = todos.find(t => t.id === id);
    
    if (!todo) return null;

    todo.completed = true;
    todo.completedAt = new Date().toISOString();
    
    await this.saveTodos(todos);
    this.context.logger.info(`Completed todo: ${todo.text}`);
    
    return todo;
  }

  /**
   * Delete a todo
   */
  async deleteTodo(id: string): Promise<boolean> {
    const todos = await this.getTodos();
    const index = todos.findIndex(t => t.id === id);
    
    if (index === -1) return false;

    todos.splice(index, 1);
    await this.saveTodos(todos);
    
    return true;
  }

  /**
   * Get stats
   */
  async getStats(): Promise<{ total: number; active: number; completed: number }> {
    const todos = await this.getTodos();
    return {
      total: todos.length,
      active: todos.filter(t => !t.completed).length,
      completed: todos.filter(t => t.completed).length
    };
  }
}

export default function createSkill(config: TodoConfig, context: SkillContext) {
  return new TodoSkill(config, context);
}

export type { Todo, TodoConfig };
