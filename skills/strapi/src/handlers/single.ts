import type { StrapiClient } from '../client.js';

export async function handleSingle(
  client: StrapiClient,
  action: string,
  args: string[]
): Promise<unknown> {
  const resource = args[0];
  if (!resource) {
    throw new Error('Single type resource name is required (e.g. "homepage")');
  }

  const manager = client.single(resource);

  switch (action) {
    case 'find': {
      const params = args[1] ? JSON.parse(args[1]) : undefined;
      return manager.find(params);
    }

    case 'update': {
      const data = args[1];
      if (!data) {
        throw new Error('Data JSON is required for update');
      }
      const params = args[2] ? JSON.parse(args[2]) : undefined;
      return manager.update(JSON.parse(data), params);
    }

    case 'delete': {
      const params = args[1] ? JSON.parse(args[1]) : undefined;
      return manager.delete(params);
    }

    default:
      throw new Error(
        `Unknown single type action: "${action}". Use: find, update, delete`
      );
  }
}
