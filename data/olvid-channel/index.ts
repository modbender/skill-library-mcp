import {
  type OpenClawPluginApi,
  emptyPluginConfigSchema,
} from "openclaw/plugin-sdk";
import {setOlvidRuntime} from "./src/runtime";
import {olvidPlugin} from "./src/channel";

const plugin: {id: string, name: string, description: string, configSchema: unknown, register: (api: OpenClawPluginApi) => void} = {
  id: "olvid",
  name: "Olvid",
  description: "Olvid channel plugin",
  configSchema: emptyPluginConfigSchema(),
  register(api: OpenClawPluginApi) {
    setOlvidRuntime(api.runtime);
    api.registerChannel(olvidPlugin);
  }
}

export default plugin;
