import type { StrapiClient } from '../client.js';
import { fetchJson } from '../client.js';

const READONLY_HINT =
  'Layout configuration is not available on this Strapi instance (HTTP 403). ' +
  'Two options: ' +
  '1) Configure form layout in the Strapi admin panel → Content-Type Builder → select the type → Configure the view. ' +
  '2) Switch Strapi to local/dev mode where the Content-Type Builder API allows write operations.';

async function layoutFetch<T = unknown>(
  client: StrapiClient,
  path: string,
  init?: RequestInit
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

interface FieldMetadata {
  edit?: {
    label?: string;
    description?: string;
    placeholder?: string;
    visible?: boolean;
    editable?: boolean;
    mainField?: string;
    size?: number;
  };
  list?: {
    label?: string;
    searchable?: boolean;
    sortable?: boolean;
  };
}

interface LayoutField {
  name: string;
  size: number;
}

interface LayoutRow {
  fields: LayoutField[];
}

interface LayoutConfiguration {
  uid: string;
  settings: Record<string, unknown>;
  metadatas: Record<string, FieldMetadata>;
  layouts: {
    edit: LayoutRow[];
    list: string[];
  };
}

interface ConfigurationResponse {
  data: LayoutConfiguration;
}

interface ConfigurationUpdatePayload {
  layouts?: {
    edit?: LayoutRow[];
    list?: string[];
  };
  metadatas?: Record<string, FieldMetadata>;
  settings?: Record<string, unknown>;
}

export async function handleLayout(
  client: StrapiClient,
  action: string,
  args: string[]
): Promise<unknown> {
  switch (action) {
    case 'get': {
      const uid = args[0];
      if (!uid) {
        throw new Error(
          'Usage: layout get <uid>\n' +
          'uid: full content type UID like "api::article.article"\n' +
          'Returns: edit form layout (field order, sizes, grouping), list view columns, and field metadata'
        );
      }

      const config = await layoutFetch<ConfigurationResponse>(
        client,
        `/content-type-builder/content-types/${uid}/configuration`
      );

      return {
        uid,
        editLayout: config.data.layouts.edit,
        listLayout: config.data.layouts.list,
        fieldMetadata: config.data.metadatas,
        settings: config.data.settings,
      };
    }

    case 'get-component': {
      const uid = args[0];
      if (!uid) {
        throw new Error(
          'Usage: layout get-component <uid>\n' +
          'uid: component UID like "shared.seo"'
        );
      }

      const config = await layoutFetch<ConfigurationResponse>(
        client,
        `/content-type-builder/components/${uid}/configuration`
      );

      return {
        uid,
        editLayout: config.data.layouts.edit,
        listLayout: config.data.layouts.list,
        fieldMetadata: config.data.metadatas,
        settings: config.data.settings,
      };
    }

    case 'update': {
      const uid = args[0];
      const raw = args[1];
      if (!uid || !raw) {
        throw new Error(
          'Usage: layout update <uid> <payload>\n' +
          'uid: full content type UID like "api::article.article"\n' +
          'Payload example:\n' +
          '{\n' +
          '  "layouts": {\n' +
          '    "edit": [\n' +
          '      [{"name":"title","size":6},{"name":"slug","size":6}],\n' +
          '      [{"name":"content","size":12}]\n' +
          '    ],\n' +
          '    "list": ["title","createdAt","updatedAt"]\n' +
          '  },\n' +
          '  "metadatas": {\n' +
          '    "title": {"edit":{"label":"Article Title","description":"Main heading","visible":true,"editable":true}}\n' +
          '  }\n' +
          '}'
        );
      }

      let payload: ConfigurationUpdatePayload;
      try {
        payload = JSON.parse(raw) as ConfigurationUpdatePayload;
      } catch {
        throw new Error('Invalid JSON payload. Must be a valid JSON string with layouts and/or metadatas.');
      }

      return {
        warning: 'This will change the edit form layout in Strapi admin panel. Only works on local/dev instances.',
        result: await layoutFetch(
          client,
          `/content-type-builder/content-types/${uid}/configuration`,
          {
            method: 'PUT',
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
          'Usage: layout update-component <uid> <payload>\n' +
          'uid: component UID like "shared.seo"\n' +
          'Payload: same format as "layout update"'
        );
      }

      let payload: ConfigurationUpdatePayload;
      try {
        payload = JSON.parse(raw) as ConfigurationUpdatePayload;
      } catch {
        throw new Error('Invalid JSON payload. Must be a valid JSON string with layouts and/or metadatas.');
      }

      return {
        warning: 'This will change the component form layout in Strapi admin panel. Only works on local/dev instances.',
        result: await layoutFetch(
          client,
          `/content-type-builder/components/${uid}/configuration`,
          {
            method: 'PUT',
            body: JSON.stringify(payload),
            headers: { 'Content-Type': 'application/json' },
          }
        ),
      };
    }

    case 'set-field': {
      const uid = args[0];
      const fieldName = args[1];
      const raw = args[2];
      if (!uid || !fieldName || !raw) {
        throw new Error(
          'Usage: layout set-field <uid> <fieldName> <metadata>\n' +
          'Example: layout set-field api::article.article title \'{"edit":{"label":"Article Title","description":"Enter the main heading","size":6}}\''
        );
      }

      let meta: FieldMetadata;
      try {
        meta = JSON.parse(raw) as FieldMetadata;
      } catch {
        throw new Error('Invalid JSON for field metadata.');
      }

      const current = await layoutFetch<ConfigurationResponse>(
        client,
        `/content-type-builder/content-types/${uid}/configuration`
      );

      const updatedMetadatas = {
        ...current.data.metadatas,
        [fieldName]: {
          ...current.data.metadatas[fieldName],
          ...meta,
          edit: {
            ...current.data.metadatas[fieldName]?.edit,
            ...meta.edit,
          },
          list: {
            ...current.data.metadatas[fieldName]?.list,
            ...meta.list,
          },
        },
      };

      return {
        warning: 'This will change field display settings. Only works on local/dev instances.',
        field: fieldName,
        metadata: meta,
        result: await layoutFetch(
          client,
          `/content-type-builder/content-types/${uid}/configuration`,
          {
            method: 'PUT',
            body: JSON.stringify({
              layouts: current.data.layouts,
              metadatas: updatedMetadatas,
              settings: current.data.settings,
            }),
            headers: { 'Content-Type': 'application/json' },
          }
        ),
      };
    }

    case 'reorder': {
      const uid = args[0];
      const raw = args[1];
      if (!uid || !raw) {
        throw new Error(
          'Usage: layout reorder <uid> <editLayout>\n' +
          'editLayout: array of rows, each row is an array of {name, size} objects\n' +
          'Example: layout reorder api::article.article \'[[{"name":"title","size":6},{"name":"slug","size":6}],[{"name":"content","size":12}]]\'\n' +
          'Field sizes must sum to 12 per row (12-column grid)'
        );
      }

      let editLayout: LayoutRow[];
      try {
        const parsed = JSON.parse(raw) as Array<Array<{ name: string; size: number }>>;
        editLayout = parsed.map((row) => ({ fields: row }));
      } catch {
        throw new Error('Invalid JSON for edit layout. Expected array of rows: [[{"name":"field","size":6},...],...]');
      }

      const current = await layoutFetch<ConfigurationResponse>(
        client,
        `/content-type-builder/content-types/${uid}/configuration`
      );

      return {
        warning: 'This will reorder fields in the edit form. Only works on local/dev instances.',
        result: await layoutFetch(
          client,
          `/content-type-builder/content-types/${uid}/configuration`,
          {
            method: 'PUT',
            body: JSON.stringify({
              layouts: {
                edit: editLayout,
                list: current.data.layouts.list,
              },
              metadatas: current.data.metadatas,
              settings: current.data.settings,
            }),
            headers: { 'Content-Type': 'application/json' },
          }
        ),
      };
    }

    default:
      throw new Error(
        `Unknown layout action: "${action}". ` +
        'Use: get, get-component, update, update-component, set-field, reorder'
      );
  }
}
