import type { StrapiClient } from '../client.js';
import { fetchJson } from '../client.js';

interface Attribute {
  type: string;
  required?: boolean;
  unique?: boolean;
  default?: unknown;
  minLength?: number;
  maxLength?: number;
  min?: number;
  max?: number;
  enum?: string[];
  private?: boolean;
  configurable?: boolean;
  relation?: string;
  target?: string;
  mappedBy?: string;
  inversedBy?: string;
  component?: string;
  components?: string[];
  repeatable?: boolean;
  pluginOptions?: Record<string, unknown>;
  [key: string]: unknown;
}

interface ContentType {
  uid: string;
  apiID: string;
  schema: {
    singularName: string;
    pluralName: string;
    displayName: string;
    kind: 'collectionType' | 'singleType';
    draftAndPublish: boolean;
    pluginOptions?: { i18n?: { localized?: boolean } };
    attributes: Record<string, Attribute>;
  };
}

interface ComponentType {
  uid: string;
  category: string;
  schema: {
    displayName: string;
    attributes: Record<string, Attribute>;
  };
}

interface ContentTypesResponse {
  data: ContentType[];
}

interface ComponentsResponse {
  data: ComponentType[];
}

function describeField(name: string, attr: Attribute) {
  const info: Record<string, unknown> = {
    name,
    type: attr.type,
  };

  if (attr.required) info.required = true;
  if (attr.unique) info.unique = true;
  if (attr.default !== undefined) info.default = attr.default;
  if (attr.private) info.private = true;

  if (attr.minLength !== undefined) info.minLength = attr.minLength;
  if (attr.maxLength !== undefined) info.maxLength = attr.maxLength;
  if (attr.min !== undefined) info.min = attr.min;
  if (attr.max !== undefined) info.max = attr.max;
  if (attr.enum) info.allowedValues = attr.enum;

  if (attr.type === 'relation') {
    info.relation = attr.relation;
    info.target = attr.target;
    if (attr.mappedBy) info.mappedBy = attr.mappedBy;
    if (attr.inversedBy) info.inversedBy = attr.inversedBy;
  }

  if (attr.type === 'component') {
    info.component = attr.component;
    info.repeatable = attr.repeatable ?? false;
  }

  if (attr.type === 'dynamiczone') {
    info.components = attr.components;
  }

  const i18n = attr.pluginOptions?.i18n as { localized?: boolean } | undefined;
  if (i18n?.localized) {
    info.localized = true;
  }

  return info;
}

async function fetchContentTypes(client: StrapiClient): Promise<ContentType[]> {
  const response = await fetchJson<ContentTypesResponse>(
    client,
    '/content-type-builder/content-types',
    { method: 'GET' }
  );
  return response.data;
}

async function findContentType(
  client: StrapiClient,
  apiID: string
): Promise<ContentType> {
  const allTypes = await fetchContentTypes(client);
  const ct = allTypes.find(
    (t) =>
      t.apiID === apiID ||
      t.schema.singularName === apiID ||
      t.schema.pluralName === apiID
  );
  if (!ct) {
    throw new Error(`Content type "${apiID}" not found`);
  }
  return ct;
}

export async function handleContent(
  client: StrapiClient,
  action: string,
  args: string[]
): Promise<unknown> {
  switch (action) {
    case 'types': {
      const allTypes = await fetchContentTypes(client);
      return allTypes
        .filter((ct) => ct.uid.startsWith('api::'))
        .map((ct) => {
          const i18n = ct.schema.pluginOptions?.i18n;
          return {
            uid: ct.uid,
            apiID: ct.apiID,
            displayName: ct.schema.displayName,
            kind: ct.schema.kind,
            pluralName: ct.schema.pluralName,
            singularName: ct.schema.singularName,
            draftAndPublish: ct.schema.draftAndPublish,
            localized: !!i18n?.localized,
            fields: Object.entries(ct.schema.attributes).map(([name, attr]) =>
              describeField(name, attr)
            ),
          };
        });
    }

    case 'schema': {
      const apiID = args[0];
      if (!apiID) {
        throw new Error('API ID is required (e.g. "article", "restaurant")');
      }

      const ct = await findContentType(client, apiID);
      const i18n = ct.schema.pluginOptions?.i18n;

      return {
        uid: ct.uid,
        apiID: ct.apiID,
        displayName: ct.schema.displayName,
        kind: ct.schema.kind,
        draftAndPublish: ct.schema.draftAndPublish,
        localized: !!i18n?.localized,
        fields: Object.entries(ct.schema.attributes).map(([name, attr]) =>
          describeField(name, attr)
        ),
      };
    }

    case 'components': {
      const response = await fetchJson<ComponentsResponse>(
        client,
        '/content-type-builder/components',
        { method: 'GET' }
      );

      return response.data.map((comp) => ({
        uid: comp.uid,
        category: comp.category,
        displayName: comp.schema.displayName,
        fields: Object.entries(comp.schema.attributes).map(([name, attr]) =>
          describeField(name, attr)
        ),
      }));
    }

    case 'component': {
      const compUid = args[0];
      if (!compUid) {
        throw new Error('Component UID is required (e.g. "shared.seo")');
      }

      const response = await fetchJson<ComponentsResponse>(
        client,
        '/content-type-builder/components',
        { method: 'GET' }
      );

      const comp = response.data.find((c) => c.uid === compUid);
      if (!comp) {
        throw new Error(`Component "${compUid}" not found`);
      }

      return {
        uid: comp.uid,
        category: comp.category,
        displayName: comp.schema.displayName,
        fields: Object.entries(comp.schema.attributes).map(([name, attr]) =>
          describeField(name, attr)
        ),
      };
    }

    case 'relations': {
      const allTypes = await fetchContentTypes(client);
      const apiTypes = allTypes.filter((ct) => ct.uid.startsWith('api::'));

      const relations: Array<{
        from: string;
        field: string;
        relation: string;
        to: string;
      }> = [];

      for (const ct of apiTypes) {
        for (const [fieldName, attr] of Object.entries(ct.schema.attributes)) {
          if (attr.type === 'relation' && attr.target) {
            relations.push({
              from: ct.schema.displayName,
              field: fieldName,
              relation: attr.relation ?? 'unknown',
              to: attr.target,
            });
          }
        }
      }

      return relations;
    }

    case 'inspect': {
      const resource = args[0];
      if (!resource) {
        throw new Error('Resource name is required (e.g. "articles")');
      }

      const ct = await findContentType(client, resource);
      const isSingle = ct.schema.kind === 'singleType';
      const documentId = args[1];

      if (isSingle) {
        return client.single(resource).find({ populate: '*' });
      }

      if (documentId) {
        return client.collection(resource).findOne(documentId, { populate: '*' });
      }

      return client.collection(resource).find({
        populate: '*',
        pagination: { page: 1, pageSize: 1 },
      });
    }

    case 'drafts': {
      const resource = args[0];
      if (!resource) {
        throw new Error('Resource name is required (e.g. "articles")');
      }
      const extraParams = args[1] ? JSON.parse(args[1]) : {};
      return client
        .collection(resource)
        .find({ ...extraParams, status: 'draft' });
    }

    case 'published': {
      const resource = args[0];
      if (!resource) {
        throw new Error('Resource name is required (e.g. "articles")');
      }
      const extraParams = args[1] ? JSON.parse(args[1]) : {};
      return client
        .collection(resource)
        .find({ ...extraParams, status: 'published' });
    }

    case 'publish': {
      const resource = args[0];
      const documentId = args[1];
      if (!resource || !documentId) {
        throw new Error('Resource and document ID are required');
      }
      const extraParams = args[2] ? JSON.parse(args[2]) : {};
      return client
        .collection(resource)
        .update(documentId, {}, { ...extraParams, status: 'published' });
    }

    case 'unpublish': {
      const resource = args[0];
      const documentId = args[1];
      if (!resource || !documentId) {
        throw new Error('Resource and document ID are required');
      }
      const extraParams = args[2] ? JSON.parse(args[2]) : {};
      return client
        .collection(resource)
        .update(documentId, {}, { ...extraParams, status: 'draft' });
    }

    case 'create-draft': {
      const resource = args[0];
      const data = args[1];
      if (!resource || !data) {
        throw new Error('Resource and data JSON are required');
      }
      return client.collection(resource).create(JSON.parse(data));
    }

    case 'create-published': {
      const resource = args[0];
      const data = args[1];
      if (!resource || !data) {
        throw new Error('Resource and data JSON are required');
      }
      return client
        .collection(resource)
        .create(JSON.parse(data), { status: 'published' });
    }

    default:
      throw new Error(
        `Unknown content action: "${action}". Use: types, schema, components, component, relations, inspect, drafts, published, publish, unpublish, create-draft, create-published`
      );
  }
}
