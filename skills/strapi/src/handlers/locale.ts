import type { StrapiClient } from '../client.js';
import { fetchJson } from '../client.js';
import type { StrapiLocale } from '../types.js';

export async function handleLocale(
  client: StrapiClient,
  action: string,
  args: string[]
): Promise<unknown> {
  switch (action) {
    case 'list': {
      return fetchJson<StrapiLocale[]>(client, '/i18n/locales', { method: 'GET' });
    }

    case 'get': {
      const localeId = args[0];
      if (!localeId) {
        throw new Error('Locale ID is required for get');
      }
      const locales = await fetchJson<StrapiLocale[]>(client, '/i18n/locales', { method: 'GET' });
      const found = locales.find(
        (l) => String(l.id) === localeId || l.code === localeId
      );
      if (!found) {
        throw new Error(`Locale "${localeId}" not found`);
      }
      return found;
    }

    case 'create': {
      const data = args[0];
      if (!data) {
        throw new Error(
          'Data JSON is required for create (e.g. {"name":"French","code":"fr","isDefault":false})'
        );
      }
      return fetchJson(client, '/i18n/locales', {
        method: 'POST',
        body: data,
        headers: { 'Content-Type': 'application/json' },
      });
    }

    case 'delete': {
      const localeId = args[0];
      if (!localeId) {
        throw new Error('Locale ID is required for delete');
      }
      return fetchJson(client, `/i18n/locales/${localeId}`, { method: 'DELETE' });
    }

    default:
      throw new Error(
        `Unknown locale action: "${action}". Use: list, get, create, delete`
      );
  }
}
