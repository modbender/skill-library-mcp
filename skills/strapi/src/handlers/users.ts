import type { StrapiClient } from '../client.js';
import { fetchJson } from '../client.js';

export async function handleUsers(
  client: StrapiClient,
  action: string,
  args: string[]
): Promise<unknown> {
  switch (action) {
    // ─── User CRUD ───

    case 'find': {
      const params = args[0] ? `?${new URLSearchParams(JSON.parse(args[0]) as Record<string, string>)}` : '';
      return fetchJson(client, `/users${params}`);
    }

    case 'findOne': {
      const id = args[0];
      if (!id) throw new Error('Usage: users findOne <userID>');
      return fetchJson(client, `/users/${id}`);
    }

    case 'me': {
      return fetchJson(client, '/users/me');
    }

    case 'create': {
      const raw = args[0];
      if (!raw) {
        throw new Error(
          'Usage: users create <data>\n' +
          'Required fields: username, email, password\n' +
          'Optional: role (role ID), confirmed, blocked\n' +
          'Example: \'{"username":"jane","email":"jane@example.com","password":"Str0ng!Pass","role":1}\''
        );
      }
      return fetchJson(client, '/users', {
        method: 'POST',
        body: raw,
        headers: { 'Content-Type': 'application/json' },
      });
    }

    case 'update': {
      const id = args[0];
      const raw = args[1];
      if (!id || !raw) {
        throw new Error(
          'Usage: users update <userID> <data>\n' +
          'Example: \'{"email":"new@example.com","blocked":false}\''
        );
      }
      return fetchJson(client, `/users/${id}`, {
        method: 'PUT',
        body: raw,
        headers: { 'Content-Type': 'application/json' },
      });
    }

    case 'delete': {
      const id = args[0];
      if (!id) throw new Error('Usage: users delete <userID>');
      return fetchJson(client, `/users/${id}`, { method: 'DELETE' });
    }

    // ─── Roles ───

    case 'roles': {
      return fetchJson(client, '/users-permissions/roles');
    }

    case 'role': {
      const id = args[0];
      if (!id) throw new Error('Usage: users role <roleID>');
      return fetchJson(client, `/users-permissions/roles/${id}`);
    }

    // ─── Authentication ───

    case 'login': {
      const raw = args[0];
      if (!raw) {
        throw new Error(
          'Usage: users login <credentials>\n' +
          'Example: \'{"identifier":"user@example.com","password":"password123"}\'\n' +
          'identifier can be email or username'
        );
      }
      return fetchJson(client, '/auth/local', {
        method: 'POST',
        body: raw,
        headers: { 'Content-Type': 'application/json' },
      });
    }

    case 'register': {
      const raw = args[0];
      if (!raw) {
        throw new Error(
          'Usage: users register <data>\n' +
          'Required: username, email, password\n' +
          'Example: \'{"username":"newuser","email":"new@example.com","password":"Str0ng!Pass"}\''
        );
      }
      return fetchJson(client, '/auth/local/register', {
        method: 'POST',
        body: raw,
        headers: { 'Content-Type': 'application/json' },
      });
    }

    case 'forgot-password': {
      const raw = args[0];
      if (!raw) {
        throw new Error(
          'Usage: users forgot-password <data>\n' +
          'Example: \'{"email":"user@example.com"}\''
        );
      }
      return fetchJson(client, '/auth/forgot-password', {
        method: 'POST',
        body: raw,
        headers: { 'Content-Type': 'application/json' },
      });
    }

    case 'reset-password': {
      const raw = args[0];
      if (!raw) {
        throw new Error(
          'Usage: users reset-password <data>\n' +
          'Example: \'{"code":"resetToken","password":"NewStr0ng!Pass","passwordConfirmation":"NewStr0ng!Pass"}\''
        );
      }
      return fetchJson(client, '/auth/reset-password', {
        method: 'POST',
        body: raw,
        headers: { 'Content-Type': 'application/json' },
      });
    }

    // ─── Count ───

    case 'count': {
      return fetchJson(client, '/users/count');
    }

    default:
      throw new Error(
        `Unknown users action: "${action}". Use: find, findOne, me, create, update, delete, roles, role, count, login, register, forgot-password, reset-password`
      );
  }
}
