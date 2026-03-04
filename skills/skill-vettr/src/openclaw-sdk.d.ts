declare module '@openclaw/sdk' {
  export interface OpenClawSkill {
    name: string;
    version: string;
    description: string;
    onLoad(ctx: SkillContext): Promise<void>;
  }

  export interface SkillContext {
    config: SkillConfig;
    commands: SkillCommands;
    hooks: SkillHooks;
    ui: SkillUI;
    tools: SkillTools;
  }

  export interface SkillConfig {
    get<T>(key: string, defaultValue: T): T;
  }

  export interface SkillCommands {
    register(
      name: string,
      callback: (args: Record<string, unknown>) => Promise<string>,
    ): void;
  }

  export interface SkillHooks {
    on(
      event: string,
      callback: (event: SkillInstallEvent) => Promise<void>,
    ): void;
  }

  export interface SkillInstallEvent {
    skillPath: string;
    preventDefault(): void;
  }

  export interface SkillUI {
    showProgress(message: string): void;
    notify(message: string): void;
    confirm(message: string): Promise<boolean>;
  }

  export interface SkillTools {
    readFile(path: string): Promise<string>;
    writeFile(path: string, content: string): Promise<void>;
    stat(
      path: string,
    ): Promise<{ isDirectory(): boolean; isFile(): boolean; isSymbolicLink(): boolean }>;
    lstat(
      path: string,
    ): Promise<{ isDirectory(): boolean; isFile(): boolean; isSymbolicLink(): boolean }>;
    realpath(path: string): Promise<string>;
    readdir(path: string): Promise<string[]>;
    mkdtemp(prefix: string): Promise<string>;
    rm(
      path: string,
      opts?: { recursive?: boolean; force?: boolean },
    ): Promise<void>;
    exists(path: string): Promise<boolean>;
  }
}
