import type { StrapiClient } from '../client.js';
import { fetchJson } from '../client.js';
import type { StrapiLocale } from '../types.js';

interface StrapiEntry {
  documentId?: string;
  locale?: string;
  [key: string]: unknown;
}

interface StrapiResponse {
  data: StrapiEntry | StrapiEntry[];
  meta?: unknown;
}

async function getLocales(client: StrapiClient): Promise<StrapiLocale[]> {
  return fetchJson<StrapiLocale[]>(client, '/i18n/locales', { method: 'GET' });
}

async function fetchForLocale(
  client: StrapiClient,
  type: 'collection' | 'single',
  resource: string,
  locale: string,
  extraParams?: Record<string, unknown>,
  documentId?: string
): Promise<unknown> {
  const params = { locale, ...extraParams };

  if (type === 'collection') {
    const manager = client.collection(resource);
    if (documentId) {
      return manager.findOne(documentId, params);
    }
    return manager.find(params);
  }

  return client.single(resource).find(params);
}

export async function handleLocalize(
  client: StrapiClient,
  action: string,
  args: string[]
): Promise<unknown> {
  switch (action) {
    case 'get': {
      const type = args[0] as 'collection' | 'single';
      const resource = args[1];
      const locale = args[2];

      if (!type || !resource || !locale) {
        throw new Error(
          'Usage: localize get <collection|single> <resource> <locale> [documentID] [queryParams]'
        );
      }

      const documentId = type === 'collection' ? args[3] : undefined;
      const paramsArg = type === 'collection' ? args[4] : args[3];
      const extraParams = paramsArg ? JSON.parse(paramsArg) : undefined;

      return fetchForLocale(client, type, resource, locale, extraParams, documentId);
    }

    case 'get-all': {
      const type = args[0] as 'collection' | 'single';
      const resource = args[1];
      const documentId = type === 'collection' ? args[2] : undefined;
      const paramsArg = type === 'collection' ? args[3] : args[2];
      const extraParams = paramsArg ? JSON.parse(paramsArg) : undefined;

      if (!type || !resource) {
        throw new Error(
          'Usage: localize get-all <collection|single> <resource> [documentID] [queryParams]'
        );
      }

      const locales = await getLocales(client);
      const results: Record<string, unknown> = {};

      for (const loc of locales) {
        try {
          results[loc.code] = await fetchForLocale(
            client, type, resource, loc.code, extraParams, documentId
          );
        } catch {
          results[loc.code] = null;
        }
      }

      return { locales: locales.map((l) => l.code), content: results };
    }

    case 'create': {
      const type = args[0] as 'collection' | 'single';
      const resource = args[1];
      const locale = args[2];
      const data = args[3];

      if (!type || !resource || !locale || !data) {
        throw new Error(
          'Usage: localize create <collection|single> <resource> <locale> <data>'
        );
      }

      if (type === 'collection') {
        return client.collection(resource).create(JSON.parse(data), { locale });
      }

      return client.single(resource).update(JSON.parse(data), { locale });
    }

    case 'update': {
      const type = args[0] as 'collection' | 'single';
      const resource = args[1];
      const locale = args[2];

      if (type === 'collection') {
        const documentId = args[3];
        const data = args[4];
        if (!resource || !locale || !documentId || !data) {
          throw new Error(
            'Usage: localize update collection <resource> <locale> <documentID> <data>'
          );
        }
        return client.collection(resource).update(documentId, JSON.parse(data), { locale });
      }

      const data = args[3];
      if (!resource || !locale || !data) {
        throw new Error(
          'Usage: localize update single <resource> <locale> <data>'
        );
      }
      return client.single(resource).update(JSON.parse(data), { locale });
    }

    case 'delete': {
      const type = args[0] as 'collection' | 'single';
      const resource = args[1];
      const locale = args[2];

      if (!type || !resource || !locale) {
        throw new Error(
          'Usage: localize delete <collection|single> <resource> <locale> [documentID]'
        );
      }

      if (type === 'collection') {
        const documentId = args[3];
        if (!documentId) {
          throw new Error(
            'Usage: localize delete collection <resource> <locale> <documentID>'
          );
        }
        return client.collection(resource).delete(documentId, { locale });
      }

      return client.single(resource).delete({ locale });
    }

    case 'status': {
      const type = args[0] as 'collection' | 'single';
      const resource = args[1];
      const documentId = type === 'collection' ? args[2] : undefined;

      if (!type || !resource || (type === 'collection' && !documentId)) {
        throw new Error(
          'Usage: localize status <collection|single> <resource> [documentID]'
        );
      }

      const locales = await getLocales(client);
      const status: Record<string, { exists: boolean; updatedAt?: string }> = {};

      for (const loc of locales) {
        try {
          const result = await fetchForLocale(
            client, type, resource, loc.code, { fields: ['updatedAt'] }, documentId
          ) as StrapiResponse;

          const entry = Array.isArray(result.data) ? result.data[0] : result.data;
          status[loc.code] = {
            exists: !!entry,
            updatedAt: entry?.updatedAt as string | undefined,
          };
        } catch {
          status[loc.code] = { exists: false };
        }
      }

      return {
        resource,
        documentId: documentId ?? null,
        locales: locales.map((l) => ({
          code: l.code,
          name: l.name,
          isDefault: l.isDefault,
        })),
        translations: status,
      };
    }

    default:
      throw new Error(
        `Unknown localize action: "${action}". Use: get, get-all, create, update, delete, status`
      );
  }
}
