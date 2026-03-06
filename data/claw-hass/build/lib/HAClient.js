import EventEmitter from 'events';
import { existsSync, mkdirSync } from 'fs';
import { Auth, configColl, Connection, createConnection, createLongLivedTokenAuth, entitiesColl, servicesColl } from 'home-assistant-js-websocket';
import {} from 'json-schema';
import { join } from 'path';
import {} from '../types/HAActionDef.js';
import {} from '../types/HAActionResult.js';
import {} from '../types/HAArea.js';
import {} from '../types/HADevice.js';
import {} from '../types/HADisplayListResult.js';
import {} from '../types/HAEntityRecord.js';
import {} from '../types/HAManifest.js';
import {} from '../types/HASearchResult.js';
import {} from '../types/HATranslations.js';
import { ItemType } from '../types/ItemType.js';
import { wrapCollection } from '../util/collection.js';
import {} from '../util/field.js';
import { createJsonCache } from './JsonCache.js';
async function getAsyncAuth(options) {
    return createLongLivedTokenAuth(options.url, options.accessToken);
}
export class HAClient extends EventEmitter {
    options;
    static instance;
    connection$;
    configCollection;
    servicesCollection;
    entitiesCollection;
    static getInstance(options) {
        if (!this.instance) {
            this.instance = new HAClient(options);
        }
        return this.instance;
    }
    constructor(options) {
        super();
        this.options = options;
    }
    start() {
        this.connection$ = getAsyncAuth(this.options).then((auth) => createConnection({ auth }));
        this.configCollection = wrapCollection(this.connection$.then(configColl), (state) => this.emit('config', state), this.cache('config'));
        this.servicesCollection = wrapCollection(this.connection$.then(servicesColl), (state) => this.emit('services', state), this.cache('services'));
        this.entitiesCollection = wrapCollection(this.connection$.then(entitiesColl), (state) => this.emit('entities', state), this.cache('entities'));
        return Promise.all([
            this.configCollection.promise,
            this.servicesCollection.promise,
            this.entitiesCollection.promise
        ]).then(([config, services, entities]) => ({ config, services, entities }));
    }
    get config() { return this.configCollection.value; }
    get services() { return this.servicesCollection.value; }
    get entities() { return this.entitiesCollection.value; }
    async sendMessage(data) {
        if (!this.connection$) {
            throw new Error('Service not connected');
        }
        const connection = await this.connection$;
        return connection.sendMessagePromise(data);
    }
    async runSequence(sequence) {
        const { context, response } = await this.sendMessage({ type: 'execute_script', sequence });
        return { context, response };
    }
    async runAction(params) {
        return this.runSequence([params]);
    }
    getFrontendTranslations(category, language = 'en-GB') {
        return this.cacheFn(`frontend.get_translations.${category}`, () => {
            return this.sendMessage({ type: 'frontend/get_translations', category, language });
        });
    }
    getAreaRegistryList() {
        return this.cacheFn('config.area_registry.list', () => {
            return this.sendMessage({ type: 'config/area_registry/list' });
        });
    }
    getDeviceRegistryList() {
        return this.cacheFn('config.device_registry.list', () => {
            return this.sendMessage({ type: 'config/device_registry/list' });
        });
    }
    getEntityRegistryList() {
        return this.cacheFn('config.entity_registry.list', () => {
            return this.sendMessage({ type: 'config/entity_registry/list' });
        });
    }
    getEntityRegistryListForDisplay() {
        return this.cacheFn('config.entity_registry.list_for_display', () => {
            return this.sendMessage({ type: 'config/entity_registry/list_for_display' });
        });
    }
    getSearchRelated(itemType, itemId) {
        return this.cacheFn(`search.related.${itemType}.${itemId}`, () => {
            return this.sendMessage({ type: 'search/related', item_type: itemType, item_id: itemId });
        });
    }
    getManifestList() {
        return this.cacheFn('manifest.list', () => {
            return this.sendMessage({ type: 'manifest/list' });
        });
    }
    getManifest(integration) {
        return this.cacheFn(`manifest.list.${integration}`, () => {
            return this.sendMessage({ type: 'manifest/get', integration });
        });
    }
    async getSensors() {
        const devices = await this.getDeviceRegistryList();
        const deviceMap = Object.fromEntries(devices.map((device) => [device.id, device]));
        const records = await this.getEntityRegistryList();
        return records
            .filter(({ entity_id, disabled_by, entity_category }) => (entity_id.startsWith('sensor.') &&
            disabled_by == null &&
            entity_category !== 'diagnostic'))
            .map((record) => {
            const entity = this.entities[record.entity_id];
            const device = record.device_id ? deviceMap[record.device_id] : undefined;
            const name = entity.attributes.friendly_name ?? record.name ?? record.original_name ?? entity.entity_id;
            return {
                name,
                entity_id: entity.entity_id,
                state: entity.state,
                attributes: JSON.stringify(entity.attributes),
                areaId: record.area_id,
                platform: record.platform,
                model: device?.model,
                modelId: device?.model_id,
                manufacturer: device?.manufacturer
            };
        });
    }
    async getActions(serviceIds) {
        const { resources } = await this.getFrontendTranslations('services');
        const manifestList = await this.getManifestList();
        const devices = await this.getDeviceRegistryList();
        const deviceMap = Object.fromEntries(devices.map((device) => [device.id, device]));
        const entityRecords = await this.getEntityRegistryList();
        const entityRecordMap = Object.fromEntries(entityRecords.map((record) => [record.entity_id, record]));
        const serviceEntityIdMap = Object.values(this.entities).reduce((obj, entity) => {
            const [serviceId] = entity.entity_id.split('.');
            if (!obj[serviceId]) {
                obj[serviceId] = [];
            }
            obj[serviceId].push(entity.entity_id);
            return obj;
        }, {});
        const specifiedServiceIds = serviceIds ?? Object.keys(this.services);
        const actions = specifiedServiceIds.reduce((arr, serviceId) => {
            const serviceManifest = manifestList.find(({ domain }) => domain === serviceId);
            for (const actionId of Object.keys(this.services[serviceId])) {
                const entityIds = serviceEntityIdMap[serviceId];
                if (!entityIds) {
                    return arr;
                }
                arr.push({
                    actionId,
                    actionName: resources[`component.${serviceId}.services.${actionId}.name`] ?? actionId,
                    description: resources[`component.${serviceId}.services.${actionId}.description`],
                    serviceId,
                    serviceName: serviceManifest?.name ?? serviceId,
                    fields: this.generateActionSchema(serviceId, actionId, resources),
                    entities: entityIds.map((entityId) => {
                        const entity = this.entities[entityId];
                        const record = entityRecordMap[entityId];
                        const device = record.device_id ? deviceMap[record.device_id] : undefined;
                        const name = entity.attributes.friendly_name ?? record?.name ?? device?.name_by_user ?? device?.name;
                        return { entityId, name };
                    })
                });
            }
            return arr;
        }, []);
        return actions;
    }
    generateActionSchema(serviceId, actionId, resources = {}) {
        const action = this.services[serviceId][actionId];
        const properties = {};
        const required = [];
        for (const [fieldName, field] of Object.entries(action.fields)) {
            const prefix = `component.${serviceId}.services.${actionId}.fields.${fieldName}`;
            if (fieldName === 'advanced_fields') {
                continue;
            }
            if (field.required) {
                required.push(fieldName);
            }
            const fieldSchema = this.generateFieldSchema(field);
            fieldSchema.title = resources[`${prefix}.name`];
            fieldSchema.description = resources[`${prefix}.description`];
            properties[fieldName] = fieldSchema;
        }
        return { properties, required };
    }
    generateFieldSchema({ selector }) {
        if (!selector) {
            throw new Error('Missing selector');
        }
        const schema = {};
        if (selector.text) {
            schema.type = 'string';
        }
        else if (selector.number) {
            schema.type = 'number';
            schema.minimum = selector.number.min;
            schema.maximum = selector.number.max;
        }
        else if (selector.color_rgb) {
            schema.type = 'array';
            schema.items = { type: 'number', minimum: 0, maximum: 255 };
            schema.minItems = 3;
            schema.maxItems = 3;
        }
        else if (selector.constant) {
            schema.const = selector.constant.value;
            schema.title = selector.constant.label;
        }
        else if (selector.color_temp) {
            schema.type = 'number';
            schema.minimum = selector.color_temp.min;
            schema.maximum = selector.color_temp.max;
            schema.description = `(unit: ${selector.color_temp.unit})`;
        }
        else if (selector.select) {
            if (selector.select.multiple) {
                schema.type = 'array';
                schema.items = { type: 'string' };
            }
            else {
                schema.type = 'string';
            }
        }
        return schema;
    }
    async destroy() {
        this.configCollection?.unsubscribe();
        this.servicesCollection?.unsubscribe();
        this.entitiesCollection?.unsubscribe();
        if (this.connection$) {
            this.connection$.then((connection) => connection.close());
        }
    }
    cache(name) {
        if (!this.options.cacheDir) {
            return undefined;
        }
        if (!existsSync(this.options.cacheDir)) {
            mkdirSync(this.options.cacheDir, { recursive: true });
        }
        return createJsonCache(join(this.options.cacheDir, `${name}.json`));
    }
    async cacheFn(name, callback) {
        const cache = this.cache(name);
        if (!cache) {
            return callback();
        }
        const cachedValue = cache.read();
        if (cachedValue) {
            return cachedValue;
        }
        return callback().then((value) => {
            cache.write(value);
            return value;
        });
    }
}
