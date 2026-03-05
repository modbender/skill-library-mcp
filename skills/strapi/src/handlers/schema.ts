import type { StrapiClient } from '../client.js';
import { fetchJson } from '../client.js';

const WARNING =
  '⚠️  This is a DESTRUCTIVE operation that modifies the database schema. ' +
  'Strapi will restart after changes. ' +
  'This may not work on production/cloud deployments.';

const READONLY_HINT =
  'Schema write operations are not available on this Strapi instance (HTTP 403). ' +
  'Two options: ' +
  '1) Create the content type manually in the Strapi admin panel (Content-Type Builder), then use "collection create" to populate data. ' +
  '2) Switch Strapi to local/dev mode where the Content-Type Builder API allows write operations.';

async function schemaFetch<T = unknown>(
  client: StrapiClient,
  path: string,
  init: RequestInit
): Promise<T> {
  try {
    return await fetchJson<T>(client, path, init);
  } catch (err: unknown) {
    const msg = err instanceof Error ? err.message : String(err);
    if (/40[13]|forbidden|unauthorized/i.test(msg)) {
      throw new Error(READONLY_HINT);
    }
    throw err;
  }
}

interface ContentTypePayload {
  contentType: {
    displayName: string;
    singularName: string;
    pluralName: string;
    kind?: 'collectionType' | 'singleType';
    draftAndPublish?: boolean;
    description?: string;
    pluginOptions?: Record<string, unknown>;
    attributes: Record<string, unknown>;
  };
}

interface ComponentPayload {
  component: {
    category: string;
    displayName: string;
    icon?: string;
    attributes: Record<string, unknown>;
  };
}

interface ContentTypeResponse {
  data: {
    uid: string;
    [key: string]: unknown;
  };
}

interface ComponentResponse {
  data: {
    uid: string;
    [key: string]: unknown;
  };
}

function parsePayload<T>(raw: string, label: string): T {
  try {
    return JSON.parse(raw) as T;
  } catch {
    throw new Error(`Invalid JSON for ${label}. Must be a valid JSON string.`);
  }
}

export async function handleSchema(
  client: StrapiClient,
  action: string,
  args: string[]
): Promise<unknown> {
  switch (action) {
    // ─── Content Types ───

    case 'create-type': {
      const raw = args[0];
      if (!raw) {
        throw new Error(
          'Usage: schema create-type <payload>\n' +
          'Payload: {"contentType":{"displayName":"Review","singularName":"review","pluralName":"reviews","attributes":{"title":{"type":"string","required":true},"rating":{"type":"integer","min":1,"max":5}}}}'
        );
      }
      const payload = parsePayload<ContentTypePayload>(raw, 'content type');
      if (!payload.contentType?.displayName || !payload.contentType?.attributes) {
        throw new Error('Payload must include contentType.displayName and contentType.attributes');
      }

      return {
        warning: WARNING,
        result: await schemaFetch<ContentTypeResponse>(
          client,
          '/content-type-builder/content-types',
          {
            method: 'POST',
            body: JSON.stringify(payload),
            headers: { 'Content-Type': 'application/json' },
          }
        ),
      };
    }

    case 'update-type': {
      const uid = args[0];
      const raw = args[1];
      if (!uid || !raw) {
        throw new Error(
          'Usage: schema update-type <uid> <payload>\n' +
          'uid: full UID like "api::review.review"\n' +
          'Payload: {"contentType":{"displayName":"Review","singularName":"review","pluralName":"reviews","attributes":{...}}}'
        );
      }
      const payload = parsePayload<ContentTypePayload>(raw, 'content type');

      return {
        warning: WARNING,
        result: await schemaFetch(
          client,
          `/content-type-builder/content-types/${uid}`,
          {
            method: 'PUT',
            body: JSON.stringify(payload),
            headers: { 'Content-Type': 'application/json' },
          }
        ),
      };
    }

    case 'delete-type': {
      const uid = args[0];
      if (!uid) {
        throw new Error('Usage: schema delete-type <uid>  (e.g. "api::review.review")');
      }
      if (!uid.startsWith('api::')) {
        throw new Error('Only user-defined types (api::*) can be deleted');
      }

      return {
        warning: WARNING + ' Content type and ALL its data will be permanently deleted.',
        result: await schemaFetch(
          client,
          `/content-type-builder/content-types/${uid}`,
          { method: 'DELETE' }
        ),
      };
    }

    // ─── Components ───

    case 'create-component': {
      const raw = args[0];
      if (!raw) {
        throw new Error(
          'Usage: schema create-component <payload>\n' +
          'Payload: {"component":{"category":"shared","displayName":"FAQ","attributes":{"question":{"type":"string","required":true},"answer":{"type":"richtext"}}}}'
        );
      }
      const payload = parsePayload<ComponentPayload>(raw, 'component');
      if (!payload.component?.category || !payload.component?.displayName) {
        throw new Error('Payload must include component.category and component.displayName');
      }

      return {
        warning: WARNING,
        result: await schemaFetch<ComponentResponse>(
          client,
          '/content-type-builder/components',
          {
            method: 'POST',
            body: JSON.stringify(payload),
            headers: { 'Content-Type': 'application/json' },
          }
        ),
      };
    }

    case 'update-component': {
      const uid = args[0];
      const raw = args[1];
      if (!uid || !raw) {
        throw new Error(
          'Usage: schema update-component <uid> <payload>\n' +
          'uid: component UID like "shared.faq"\n' +
          'Payload: {"component":{"category":"shared","displayName":"FAQ","attributes":{...}}}'
        );
      }
      const payload = parsePayload<ComponentPayload>(raw, 'component');

      return {
        warning: WARNING,
        result: await schemaFetch(
          client,
          `/content-type-builder/components/${uid}`,
          {
            method: 'PUT',
            body: JSON.stringify(payload),
            headers: { 'Content-Type': 'application/json' },
          }
        ),
      };
    }

    case 'delete-component': {
      const uid = args[0];
      if (!uid) {
        throw new Error('Usage: schema delete-component <uid>  (e.g. "shared.faq")');
      }

      return {
        warning: WARNING + ' Component and all its usages will be removed.',
        result: await schemaFetch(
          client,
          `/content-type-builder/components/${uid}`,
          { method: 'DELETE' }
        ),
      };
    }

    // ─── Field-level helpers ───

    case 'add-field': {
      const uid = args[0];
      const fieldName = args[1];
      const fieldDef = args[2];
      if (!uid || !fieldName || !fieldDef) {
        throw new Error(
          'Usage: schema add-field <uid> <fieldName> <fieldDefinition>\n' +
          'Example: schema add-field api::article.article summary \'{"type":"text","maxLength":500}\''
        );
      }

      const currentTypes = await fetchJson<{ data: Array<{ uid: string; schema: { attributes: Record<string, unknown>; [key: string]: unknown } }> }>(
        client,
        '/content-type-builder/content-types',
        { method: 'GET' }
      );

      const ct = currentTypes.data.find((t) => t.uid === uid);
      if (!ct) {
        throw new Error(`Content type "${uid}" not found`);
      }

      const field = parsePayload<Record<string, unknown>>(fieldDef, 'field definition');
      const updatedAttributes = { ...ct.schema.attributes, [fieldName]: field };

      const { attributes: _, ...schemaRest } = ct.schema;
      const payload = {
        contentType: {
          ...schemaRest,
          attributes: updatedAttributes,
        },
      };

      return {
        warning: WARNING,
        field: { name: fieldName, definition: field },
        result: await schemaFetch(
          client,
          `/content-type-builder/content-types/${uid}`,
          {
            method: 'PUT',
            body: JSON.stringify(payload),
            headers: { 'Content-Type': 'application/json' },
          }
        ),
      };
    }

    case 'remove-field': {
      const uid = args[0];
      const fieldName = args[1];
      if (!uid || !fieldName) {
        throw new Error('Usage: schema remove-field <uid> <fieldName>');
      }

      const currentTypes = await fetchJson<{ data: Array<{ uid: string; schema: { attributes: Record<string, unknown>; [key: string]: unknown } }> }>(
        client,
        '/content-type-builder/content-types',
        { method: 'GET' }
      );

      const ct = currentTypes.data.find((t) => t.uid === uid);
      if (!ct) {
        throw new Error(`Content type "${uid}" not found`);
      }

      if (!(fieldName in ct.schema.attributes)) {
        throw new Error(`Field "${fieldName}" not found in ${uid}`);
      }

      const { [fieldName]: removed, ...remainingAttributes } = ct.schema.attributes;
      void removed;

      const { attributes: _, ...schemaRest } = ct.schema;
      const payload = {
        contentType: {
          ...schemaRest,
          attributes: remainingAttributes,
        },
      };

      return {
        warning: WARNING + ` Field "${fieldName}" and its data will be permanently deleted.`,
        result: await schemaFetch(
          client,
          `/content-type-builder/content-types/${uid}`,
          {
            method: 'PUT',
            body: JSON.stringify(payload),
            headers: { 'Content-Type': 'application/json' },
          }
        ),
      };
    }

    default:
      throw new Error(
        `Unknown schema action: "${action}". Use: create-type, update-type, delete-type, create-component, update-component, delete-component, add-field, remove-field`
      );
  }
}
