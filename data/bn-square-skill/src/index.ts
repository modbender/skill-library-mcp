import { BinanceHttpClient } from "./api/client";
import { BrowserClient } from "./api/browser-client";
import type { GetPostStatusInput, GetPostStatusResult, PublishPostInput, PublishPostResult, ValidateSessionResult } from "./api/types";
import { loadConfig, type LoadConfigOptions } from "./config/loader";
import type { BinanceConfig } from "./config/schema";
import { getPostStatus } from "./tools/get-post-status";
import { publishPost } from "./tools/publish-post";
import { validateSession } from "./tools/validate-session";
import { toSafeErrorMessage } from "./utils/errors";

export type { BinanceConfig } from "./config/schema";
export type { LoadConfigOptions } from "./config/loader";
export type {
  ValidateSessionResult,
  PublishPostInput,
  PublishPostResult,
  GetPostStatusInput,
  GetPostStatusResult,
} from "./api/types";

export type SkillTools = {
  validate_session: () => Promise<ValidateSessionResult>;
  publish_post: (input: PublishPostInput) => Promise<PublishPostResult>;
  get_post_status: (input: GetPostStatusInput) => Promise<GetPostStatusResult>;
};

export type SkillInstance = SkillTools & {
  connect: () => Promise<void>;
  disconnect: () => void;
};

export type CreateSkillOptions = {
  config?: BinanceConfig;
  loadConfigOptions?: LoadConfigOptions;
};

type ToolClient = {
  getJson: <T>(path: string, requestOptions?: { query?: Record<string, string> }) => Promise<T>;
  postJson: <T>(path: string, body: unknown) => Promise<T>;
  postFormData: <T>(path: string, formData: FormData) => Promise<T>;
};

const createHttpToolClient = (config: BinanceConfig): { toolClient: ToolClient; connect: () => Promise<void>; disconnect: () => void } => {
  const httpClient = new BinanceHttpClient(config);

  return {
    toolClient: {
      getJson: <T>(path: string, requestOptions?: { query?: Record<string, string> }) =>
        httpClient.getJson<T>(path, requestOptions),
      postJson: <T>(path: string, body: unknown) => httpClient.postJson<T>(path, body),
      postFormData: <T>(path: string, formData: FormData) => httpClient.postFormData<T>(path, formData)
    },
    connect: async () => {},
    disconnect: () => {}
  };
};

const createCdpToolClient = (config: BinanceConfig): { toolClient: ToolClient; connect: () => Promise<void>; disconnect: () => void } => {
  const browserClient = new BrowserClient(config);

  return {
    toolClient: {
      getJson: <T>(path: string, requestOptions?: { query?: Record<string, string> }) =>
        browserClient.getJson<T>(path, requestOptions),
      postJson: <T>(path: string, body: unknown) => browserClient.postJson<T>(path, body),
      postFormData: <T>(path: string, formData: FormData) => browserClient.postFormData<T>(path, formData)
    },
    connect: () => browserClient.connect(),
    disconnect: () => browserClient.disconnect()
  };
};

export const createSkill = (options: CreateSkillOptions = {}): SkillInstance => {
  const config = options.config ?? loadConfig(options.loadConfigOptions);
  const { toolClient, connect, disconnect } = config.cdpUrl
    ? createCdpToolClient(config)
    : createHttpToolClient(config);

  return {
    connect,
    disconnect,
    validate_session: () =>
      validateSession({
        config,
        client: {
          getJson: (path: string) => toolClient.getJson(path)
        }
      }),
    publish_post: (input: PublishPostInput) =>
      publishPost(input, {
        config,
        client: toolClient
      }),
    get_post_status: (input: GetPostStatusInput) =>
      getPostStatus(input, {
        config,
        client: {
          getJson: toolClient.getJson
        }
      })
  };
};

const parsePayload = (rawValue: string | undefined): unknown => {
  if (!rawValue) {
    return {};
  }

  try {
    return JSON.parse(rawValue) as unknown;
  } catch (error) {
    throw new Error(`Failed to parse JSON payload: ${toSafeErrorMessage(error)}`);
  }
};

const writeJson = (value: unknown): void => {
  process.stdout.write(`${JSON.stringify(value, null, 2)}\n`);
};

const runCli = async (): Promise<void> => {
  const [, , command, rawPayload] = process.argv;
  if (!command) {
    throw new Error(
      "Usage: node scripts/bn-square.mjs <validate_session|publish_post|get_post_status> [json_payload]"
    );
  }

  const skill = createSkill();

  try {
    await skill.connect();

    if (command === "validate_session") {
      writeJson(await skill.validate_session());
      return;
    }

    if (command === "publish_post") {
      writeJson(await skill.publish_post(parsePayload(rawPayload) as PublishPostInput));
      return;
    }

    if (command === "get_post_status") {
      writeJson(await skill.get_post_status(parsePayload(rawPayload) as GetPostStatusInput));
      return;
    }

    throw new Error(`Unknown command "${command}"`);
  } finally {
    skill.disconnect();
  }
};

const isMainModule = (): boolean => {
  // Bun-specific check
  if ("main" in import.meta && (import.meta as { main?: boolean }).main) {
    return true;
  }
  // Node.js: compare import.meta.url with process.argv[1]
  if (typeof process !== "undefined" && process.argv[1]) {
    const scriptPath = process.argv[1].replace(/\\/g, "/");
    const moduleUrl = import.meta.url.replace(/^file:\/\/\//, "");
    return moduleUrl.endsWith(scriptPath) || scriptPath.endsWith("bn-square.mjs");
  }
  return false;
};

if (isMainModule()) {
  runCli().catch((error: unknown) => {
    process.stderr.write(`${toSafeErrorMessage(error, "CLI execution failed")}\n`);
    process.exitCode = 1;
  });
}
