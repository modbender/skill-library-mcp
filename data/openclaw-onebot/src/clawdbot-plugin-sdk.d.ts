declare module "clawdbot/plugin-sdk" {
  export interface PluginRuntime {
    emitInbound(event: any): void;
    [key: string]: any;
  }
  export interface MoltbotPluginApi {
    runtime: PluginRuntime;
    registerChannel(opts: { plugin: any }): void;
    [key: string]: any;
  }
  export interface ChannelPlugin<T = any> {
    [key: string]: any;
  }
}
