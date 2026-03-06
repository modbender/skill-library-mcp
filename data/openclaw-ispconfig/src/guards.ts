import { ISPConfigError } from "./errors";
import { ISPConfigPluginConfig } from "./types";

export const WRITE_TOOLS = new Set<string>([
  "isp_client_add",
  "isp_site_add",
  "isp_domain_add",
  "isp_dns_zone_add",
  "isp_dns_record_add",
  "isp_dns_record_delete",
  "isp_mail_domain_add",
  "isp_mail_user_add",
  "isp_mail_user_delete",
  "isp_db_add",
  "isp_db_user_add",
  "isp_shell_user_add",
  "isp_ftp_user_add",
  "isp_cron_add",
  "isp_provision_site",
]);

export function assertToolAllowed(config: ISPConfigPluginConfig, toolName: string): void {
  const allowed = config.allowedOperations ?? [];
  if (allowed.length > 0 && !allowed.includes(toolName)) {
    throw new ISPConfigError("permission_denied",
      `Tool ${toolName} is blocked by allowedOperations policy`,
      { statusCode: 403 },
    );
  }

  if ((config.readOnly ?? false) && WRITE_TOOLS.has(toolName)) {
    throw new ISPConfigError("permission_denied",
      `Tool ${toolName} is blocked because readOnly=true`,
      { statusCode: 403 },
    );
  }
}
