import { execSync } from "child_process";

interface ToolContext {
  action: string;
}

export function register(api: any) {
  api.registerTool({
    id: "sparkle_vpn_start",
    description: "Start Sparkle VPN core only (without system proxy)",
    handler: async () => {
      try {
        const result = execSync(
          "bash /home/admin/.openclaw/workspace/skills/sparkle-vpn/scripts/start-vpn.sh",
          { encoding: "utf8", timeout: 30000 }
        );
        return { ok: true, result };
      } catch (error: any) {
        return { ok: false, error: error.message, stderr: error.stderr };
      }
    },
  });

  api.registerTool({
    id: "sparkle_vpn_start_with_proxy",
    description: "Start Sparkle VPN and enable system-wide proxy",
    handler: async () => {
      try {
        const result = execSync(
          "bash /home/admin/.openclaw/workspace/skills/sparkle-vpn/scripts/start-vpn.sh --with-proxy",
          { encoding: "utf8", timeout: 30000 }
        );
        return { ok: true, result };
      } catch (error: any) {
        return { ok: false, error: error.message, stderr: error.stderr };
      }
    },
  });

  api.registerTool({
    id: "sparkle_vpn_stop",
    description: "Stop Sparkle VPN and disable system proxy",
    handler: async () => {
      try {
        const result = execSync(
          "bash /home/admin/.openclaw/workspace/skills/sparkle-vpn/scripts/stop-vpn.sh",
          { encoding: "utf8", timeout: 30000 }
        );
        return { ok: true, result };
      } catch (error: any) {
        return { ok: false, error: error.message, stderr: error.stderr };
      }
    },
  });

  api.registerTool({
    id: "sparkle_vpn_enable_proxy",
    description: "Enable system-wide proxy settings (VPN must be running)",
    handler: async () => {
      try {
        const result = execSync(
          "bash /home/admin/.openclaw/workspace/skills/sparkle-vpn/scripts/enable-system-proxy.sh",
          { encoding: "utf8", timeout: 30000 }
        );
        return { ok: true, result };
      } catch (error: any) {
        return { ok: false, error: error.message, stderr: error.stderr };
      }
    },
  });

  api.registerTool({
    id: "sparkle_vpn_disable_proxy",
    description: "Disable system-wide proxy settings",
    handler: async () => {
      try {
        const result = execSync(
          "bash /home/admin/.openclaw/workspace/skills/sparkle-vpn/scripts/disable-system-proxy.sh",
          { encoding: "utf8", timeout: 30000 }
        );
        return { ok: true, result };
      } catch (error: any) {
        return { ok: false, error: error.message, stderr: error.stderr };
      }
    },
  });

  api.registerTool({
    id: "sparkle_vpn_status",
    description: "Query VPN status - Show current node and available nodes list",
    handler: async () => {
      try {
        const result = execSync(
          "bash /home/admin/.openclaw/workspace/skills/sparkle-vpn/scripts/status-vpn.sh",
          { encoding: "utf8", timeout: 30000 }
        );
        return { ok: true, result };
      } catch (error: any) {
        return { ok: false, error: error.message, stderr: error.stderr };
      }
    },
  });

  api.registerTool({
    id: "sparkle_vpn_switch",
    description: "Switch VPN node - Change to a different proxy node",
    parameters: {
      node: {
        type: "string",
        description: "Node name to switch to (e.g., '自动选择', '香港-HKG-01-VL')",
        required: true,
      },
    },
    handler: async (params: { node: string }) => {
      try {
        const result = execSync(
          `bash /home/admin/.openclaw/workspace/skills/sparkle-vpn/scripts/switch-node.sh "${params.node}"`,
          { encoding: "utf8", timeout: 30000 }
        );
        return { ok: true, result };
      } catch (error: any) {
        return { ok: false, error: error.message, stderr: error.stderr };
      }
    },
  });
}
