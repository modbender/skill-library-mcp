import {} from '../types/PluginConfig.js';
export function parseConfig(rawConfig) {
    const config = (rawConfig.plugins?.entries?.['claw-hass']?.config ?? {});
    const url = config.url ?? 'http://127.0.0.1:8123';
    const services = config.services ?? [];
    const accessToken = config.accessToken;
    if (!accessToken) {
        return undefined;
    }
    return { url, accessToken, services };
}
