import type { StrapiClient } from '../client.js';

export async function handleCollection(
  client: StrapiClient,
  action: string,
  args: string[]
): Promise<unknown> {
  const resource = args[0];
  if (!resource) {
    throw new Error('Collection resource name is required (e.g. "articles")');
  }

  const manager = client.collection(resource);

  switch (action) {
    case 'find': {
      const params = args[1] ? JSON.parse(args[1]) : undefined;
      return manager.find(params);
    }

    case 'findOne': {
      const documentID = args[1];
      if (!documentID) {
        throw new Error('Document ID is required for findOne');
      }
      const params = args[2] ? JSON.parse(args[2]) : undefined;
      return manager.findOne(documentID, params);
    }

    case 'create': {
      const data = args[1];
      if (!data) {
        throw new Error('Data JSON is required for create');
      }
      const params = args[2] ? JSON.parse(args[2]) : undefined;
      return manager.create(JSON.parse(data), params);
    }

    case 'update': {
      const documentID = args[1];
      const data = args[2];
      if (!documentID || !data) {
        throw new Error('Document ID and data JSON are required for update');
      }
      const params = args[3] ? JSON.parse(args[3]) : undefined;
      return manager.update(documentID, JSON.parse(data), params);
    }

    case 'delete': {
      const documentID = args[1];
      if (!documentID) {
        throw new Error('Document ID is required for delete');
      }
      const params = args[2] ? JSON.parse(args[2]) : undefined;
      return manager.delete(documentID, params);
    }

    default:
      throw new Error(
        `Unknown collection action: "${action}". Use: find, findOne, create, update, delete`
      );
  }
}
