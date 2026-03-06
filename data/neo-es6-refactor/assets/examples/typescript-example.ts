// TypeScript Examples - ES6+ with Type Annotations
// These examples demonstrate TypeScript-specific refactorings

// ============================================
// EXAMPLE 1: TypeScript Interfaces and Classes
// ============================================
interface User {
  id: number;
  name: string;
  email: string;
  role: 'admin' | 'user' | 'guest';
  profile?: Profile;  // Optional property
}

interface Profile {
  avatar?: string;
  bio?: string;
  location?: string;
}

interface ApiResponse<T> {
  data: T;
  success: boolean;
  error?: string;
  timestamp: Date;
}

class ApiClient {
  private baseUrl: string;
  private timeout: number;
  private defaultHeaders: Record<string, string>;

  constructor(config: {baseUrl: string; timeout?: number; headers?: Record<string, string>}) {
    this.baseUrl = config.baseUrl;
    this.timeout = config.timeout ?? 30000;
    this.defaultHeaders = config.headers ?? {};
  }

  async get<T>(endpoint: string, options: RequestInit = {}): Promise<ApiResponse<T>> {
    const url = `${this.baseUrl}${endpoint}`;
    const response = await fetch(url, {
      ...options,
      headers: {
        ...this.defaultHeaders,
        ...options.headers
      },
      signal: AbortSignal.timeout(this.timeout)
    });

    if (!response.ok) {
      throw new Error(`HTTP ${response.status}: ${response.statusText}`);
    }

    const data = await response.json() as T;
    return {
      data,
      success: true,
      timestamp: new Date()
    };
  }

  post<T>(endpoint: string, body: unknown): Promise<ApiResponse<T>> {
    return this.get<T>(endpoint, {
      method: 'POST',
      body: JSON.stringify(body)
    });
  }
}

// ============================================
// EXAMPLE 2: Type Guards and Discriminated Unions
// ============================================
type Result<T, E> =
  | {type: 'success'; data: T}
  | {type: 'error'; error: E};

function isSuccess<T, E>(result: Result<T, E>): result is {type: 'success'; data: T} {
  return result.type === 'success';
}

type ApiError = {
  code: number;
  message: string;
  details?: unknown;
};

const fetchWithTypeSafety = async (url: string): Promise<Result<User, ApiError>> => {
  try {
    const client = new ApiClient({baseUrl: 'https://api.example.com'});
    const response = await client.get<User>(url);
    return {type: 'success', data: response.data};
  } catch (err) {
    return {
      type: 'error',
      error: {
        code: 500,
        message: err instanceof Error ? err.message : 'Unknown error'
      }
    };
  }
};

// ============================================
// EXAMPLE 3: Generic Functions and Constraints
// ============================================
function mergeAll<T>(...objects: Partial<T>[]): T {
  return objects.reduce((acc, obj) => ({...acc, ...obj}), {} as T);
}

interface Configuration {
  apiUrl: string;
  timeout: number;
  retries: number;
}

const config: Configuration = mergeAll(
  {apiUrl: 'https://default.example.com', timeout: 5000},
  {retries: 3, timeout: 10000}  // Override timeout
  // apiUrl is inherited from first object
);

// ============================================
// EXAMPLE 4: Utility Types and Mapped Types
// ============================================
type ReadonlyUser = Readonly<User>;

type PartialUser = Partial<User>;

type PickUser = Pick<User, 'id' | 'name'>;

type OmitUser = Omit<User, 'password'>;

// Mapped type for making all properties optional except required ones
type CreateDTO<T> = Omit<T, keyof T>;

// ============================================
// EXAMPLE 5: Type-Safe Event Emitters
// ============================================
type EventMap = {
  'user:created': {userId: number; timestamp: Date};
  'user:updated': {userId: number; changes: Partial<User>};
  'error': {message: string; code?: number};
};

class TypedEventEmitter {
  private listeners: Map<keyof EventMap, Array<(data: EventMap[keyof EventMap]) => void>> = new Map();

  on<K extends keyof EventMap>(event: K, callback: (data: EventMap[K]) => void): void {
    if (!this.listeners.has(event)) {
      this.listeners.set(event, []);
    }
    this.listeners.get(event)!.push(callback);
  }

  emit<K extends keyof EventMap>(event: K, data: EventMap[K]): void {
    this.listeners.get(event)?.forEach(callback => callback(data));
  }
}

const emitter = new TypedEventEmitter();
emitter.on('user:created', (data) => {
  console.log(`User ${data.userId} created at ${data.timestamp}`);
});
emitter.emit('user:created', {userId: 123, timestamp: new Date()});

// ============================================
// EXAMPLE 6: Async Iterators and Generators
// ============================================
async function* fetchPaginated<T>(url: string, pageSize: number = 50): AsyncIterator<T[]> {
  let page = 1;
  let hasMore = true;

  while (hasMore) {
    const response = await fetch(`${url}?page=${page}&limit=${pageSize}`);
    const data = await response.json() as {items: T[]; total: number};
    yield data.items;
    hasMore = page * pageSize < data.total;
    page++;
  }
}

// Usage:
// for await (const items of fetchPaginated<User>('/api/users')) {
//   items.forEach(user => console.log(user.name));
// }

// ============================================
// EXAMPLE 7: Conditional Types and Inference
// ============================================
type ExtractId<T> = T extends {id: infer I} ? I : never;

type UserId = ExtractId<User>;  // number

function withId<T extends {id: unknown}>(item: T): T & {createdAt: Date} {
  return {...item, createdAt: new Date()};
}

const userWithTimestamp = withId({id: 1, name: 'Alice', email: 'alice@example.com'});

// ============================================
// EXAMPLE 8: Template String Types (TS 4.1+)
// ============================================
type EventName<E extends string> = `on${E[0].toUpperCase()}${E.slice(1)}`;

type ClickHandler = EventName<'click'>;  // "onClick"
type MouseOverHandler = EventName<'mouseover'>;  // "onMouseOver"

// ============================================
// EXAMPLE 9: Discriminated Unions for State Machines
// ============================================
type State =
  | {status: 'idle'}
  | {status: 'loading'; startedAt: Date}
  | {status: 'success'; data: unknown}
  | {status: 'error'; error: Error; retryCount: number};

function handleState(state: State): string {
  switch (state.status) {
    case 'idle':
      return 'Ready to start';
    case 'loading':
      return `Loading... (started at ${state.startedAt.toISOString()})`;
    case 'success':
      return `Success! Data: ${JSON.stringify(state.data)}`;
    case 'error':
      return `Error: ${state.error.message} (retries: ${state.retryCount})`;
  }
}

// ============================================
// EXAMPLE 10: Module Augmentation
// ============================================
// Extending existing types
declare module 'http' {
  interface IncomingMessage {
    userId?: string;  // Custom header injection
  }
}

// Express-style request handler with typed request/response
interface Request {
  params: Record<string, string>;
  query: Record<string, string>;
  body: unknown;
  headers: Record<string, string>;
}

interface Response {
  status(code: number): this;
  json(data: unknown): this;
  send(data: string): this;
}

function createHandler(
  handler: (req: Request, res: Response) => Promise<void> | void
): (req: Request, res: Response) => void {
  return async (req, res) => {
    try {
      await handler(req, res);
    } catch (err) {
      res.status(500).json({error: err instanceof Error ? err.message : 'Unknown error'});
    }
  };
}

// ============================================
// EXAMPLE 11: Namespaces vs Modules
// ============================================
namespace Validation {
  export function isEmail(str: string): boolean {
    return /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(str);
  }

  export function isUrl(str: string): boolean {
    try {
      new URL(str);
      return true;
    } catch {
      return false;
    }
  }

  export type Validator = (input: unknown) => boolean;
}

// ============================================
// EXAMPLE 12: Mixins with TypeScript
// ============================================
type Constructor<T = {}> = new (...args: unknown[]) => T;

function Timestamped<TBase extends Constructor>(Base: TBase) {
  return class extends Base {
    createdAt = new Date();
    updatedAt = new Date();

    touch() {
      this.updatedAt = new Date();
    }
  };
}

function WithId<TBase extends Constructor>(Base: TBase) {
  return class extends Base {
    id = crypto.randomUUID();
  };
}

class Entity {}
const TimestampedEntity = Timestamped(WithId(Entity));

const entity = new TimestampedEntity();
console.log(entity.id, entity.createdAt);

export {
  // Interfaces
  User,
  Profile,
  ApiResponse,
  Result,
  ApiError,
  EventMap,

  // Classes
  ApiClient,
  TypedEventEmitter,

  // Functions
  isSuccess,
  mergeAll,
  withId,
  createHandler,

  // Types
  ReadonlyUser,
  PartialUser,
  PickUser,
  OmitUser,
  ExtractId,
  EventName,
  State,
  Validation,

  // Example usage
  fetchWithTypeSafety,
  config,
  userWithTimestamp,
  emitter,
  entity
};
