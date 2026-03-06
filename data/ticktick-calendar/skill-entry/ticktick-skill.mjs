import { createTickTickRuntime, parseTickTickEnvFromRuntime } from "../dist/src/index.js";
import {
  DEFAULT_TOKEN_PATH,
  ReauthRequiredError,
  createWebhookReauthNotifierFromEnv,
  getAccessTokenWithAutoReauth,
} from "./token-manager.mjs";

/**
 * Build OpenClaw-ready TickTick skill actions.
 *
 * @param {object} [options]
 * @param {string} [options.tokenPath] - JSON file path containing `accessToken`
 * @param {() => Promise<string>} [options.getAccessToken] - custom token provider
 * @param {(payload: {reason:string,message:string,authUrl:string,state:string}) => Promise<void>} [options.onReauthRequired]
 * @param {import('../dist/src/config/ticktick-env.js').TickTickEnvSchema} [options.env]
 */
export function createTickTickOpenClawSkill(options = {}) {
  const tokenPath = options.tokenPath ?? process.env.TICKTICK_TOKEN_PATH ?? DEFAULT_TOKEN_PATH;

  const env = options.env ?? parseTickTickEnvFromRuntime();

  const onReauthRequired = options.onReauthRequired ?? createWebhookReauthNotifierFromEnv();

  const getAccessToken =
    options.getAccessToken ??
    (async () => {
      return getAccessTokenWithAutoReauth({ tokenPath, env, onReauthRequired });
    });

  const runtime = createTickTickRuntime({ env, getAccessToken });

  const withReauthHint = (fn) => async (input) => {
    try {
      return await fn(input);
    } catch (error) {
      if (error instanceof ReauthRequiredError) {
        throw new Error(
          `${error.message}\nReauthorize URL: ${error.authUrl}\nThen run auth-exchange and retry.`
        );
      }
      throw error;
    }
  };

  return {
    name: "ticktick",
    description: "TickTick task/project integration skill",
    actions: {
      create_task: withReauthHint((input) => runtime.useCases.createTask.execute(input)),
      list_tasks: withReauthHint((input) => runtime.useCases.listTasks.execute(input)),
      update_task: withReauthHint((input) => runtime.useCases.updateTask.execute(input)),
      complete_task: withReauthHint((input) => runtime.useCases.completeTask.execute(input)),
      list_projects: withReauthHint((input) => runtime.useCases.listProjects.execute(input)),
    },
  };
}

export default createTickTickOpenClawSkill;
