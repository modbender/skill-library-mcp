import { Type } from '@sinclair/typebox';
import { HAClient } from './lib/HAClient.js';
import { parseConfig } from './util/config.js';
import { toolResult } from './util/tool.js';
const plugin = {
    id: 'claw-hass',
    name: 'Home Assistant',
    description: 'OpenClaw Home Assistant Integration',
    configSchema: {
        parse(value) {
            const raw = value && typeof value === 'object' && !Array.isArray(value) ? value : {};
            return { url: raw.url, accessToken: raw.accessToken, services: raw.services };
        },
        uiHints: {
            url: {
                label: 'Home Assistant URL',
                help: 'URL to Home Assistant',
                placeholder: 'http://localhost:8123'
            },
            services: {
                label: 'Services',
                help: 'Home Assistant Service IDs'
            },
            accessToken: {
                label: 'Access Token',
                help: 'Home Assistant Long Lived Access Token',
                sensitive: true
            }
        }
    },
    register(api) {
        const config = parseConfig(api.config);
        if (!config) {
            return;
        }
        const client = HAClient.getInstance(config);
        api.registerService({
            id: 'hass-ws',
            async start(ctx) {
                ctx.logger.info('[claw-hass] starting service');
                await client.start();
            },
            async stop(ctx) {
                ctx.logger.info('[claw-hass] stopping service');
                await client.destroy();
            }
        });
        api.registerTool({
            name: 'ha:get_sensors',
            description: 'Get all available sensors',
            label: 'Get Sensors',
            parameters: Type.Object({}),
            async execute() {
                try {
                    const sensors = await client.getSensors();
                    return toolResult(sensors);
                }
                catch (error) {
                    return toolResult({ error });
                }
            }
        });
        api.registerTool({
            name: 'ha:get_actions',
            description: 'Get all available actions',
            label: 'Get Actions',
            parameters: Type.Object({}),
            async execute() {
                try {
                    const actions = await client.getActions(config.services);
                    return toolResult(actions);
                }
                catch (error) {
                    return toolResult({ error });
                }
            }
        });
        api.registerTool({
            name: 'ha:run_action',
            description: 'Run a specific home automation action',
            label: 'Run Action',
            parameters: Type.Object({
                actionId: Type.String({ description: 'The actionId to run' }),
                serviceId: Type.String({ description: 'The serviceId the action belongs to' }),
                entityId: Type.String({ description: 'The entityId to run the action for' }),
                data: Type.String({ description: 'Json stringified action data / parameters' })
            }),
            async execute(_, params) {
                try {
                    const { serviceId, actionId, data, entityId } = params;
                    const action = `${serviceId}.${actionId}`;
                    const target = { entity_id: entityId };
                    const result = await client.runSequence([{ action, data: JSON.parse(data), target }]);
                    return toolResult(result);
                }
                catch (error) {
                    return toolResult({ error });
                }
            }
        });
    }
};
export default plugin;
