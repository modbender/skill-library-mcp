/**
 * Shared test helpers for openclaw-ops-elvatis command tests.
 *
 * Provides a mock API object that captures registerCommand() calls,
 * allowing tests to verify command registration and invoke handlers.
 */

export interface RegisteredCommand {
  name: string;
  description: string;
  requireAuth: boolean;
  acceptsArgs: boolean;
  handler: (...args: any[]) => Promise<{ text: string }>;
  usage?: string;
}

export interface MockApi {
  commands: Map<string, RegisteredCommand>;
  registerCommand: (cmd: RegisteredCommand) => void;
  pluginConfig: Record<string, any>;
  on?: (event: string, handler: (...args: any[]) => void) => void;
  logger?: { info: (...args: any[]) => void };
  eventHandlers: Map<string, Array<(...args: any[]) => void>>;
}

/** Create a mock API object that captures command registrations. */
export function createMockApi(config: Record<string, any> = {}): MockApi {
  const commands = new Map<string, RegisteredCommand>();
  const eventHandlers = new Map<string, Array<(...args: any[]) => void>>();

  return {
    commands,
    eventHandlers,
    pluginConfig: config,
    registerCommand(cmd: RegisteredCommand) {
      commands.set(cmd.name, cmd);
    },
    on(event: string, handler: (...args: any[]) => void) {
      if (!eventHandlers.has(event)) eventHandlers.set(event, []);
      eventHandlers.get(event)!.push(handler);
    },
    logger: { info: () => {} },
  };
}

/** Invoke a registered command handler and return the text output. */
export async function invokeCommand(
  api: MockApi,
  name: string,
  args?: any,
): Promise<string> {
  const cmd = api.commands.get(name);
  if (!cmd) throw new Error(`Command /${name} not registered`);
  const result = await cmd.handler(args);
  return result.text;
}
