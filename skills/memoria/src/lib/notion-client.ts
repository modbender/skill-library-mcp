import { Client } from '@notionhq/client';
import type {
  QueryDatabaseResponse,
  CreateDatabaseResponse,
  BlockObjectRequest,
} from '@notionhq/client/build/src/api-endpoints.js';

export interface NotionPage {
  id: string;
  title: string;
  properties: Record<string, unknown>;
  lastEditedTime: string;
}

export function createNotionClient(token: string): Client {
  return new Client({ auth: token });
}

export async function createCategoryDatabase(
  client: Client,
  parentPageId: string,
  categoryName: string,
): Promise<CreateDatabaseResponse> {
  return client.databases.create({
    parent: { type: 'page_id', page_id: parentPageId },
    title: [{ type: 'text', text: { content: categoryName } }],
    properties: {
      Title: { title: {} },
      Type: { select: { options: [] } },
      Tags: { multi_select: { options: [] } },
      Created: { date: {} },
      Updated: { date: {} },
    },
  });
}

export async function createNotionPage(
  client: Client,
  databaseId: string,
  title: string,
  properties: {
    type?: string;
    tags?: string[];
    created?: string;
    updated?: string;
  },
  children?: BlockObjectRequest[],
): Promise<{ id: string }> {
  const props: Record<string, unknown> = {
    Title: { title: [{ text: { content: title } }] },
  };

  if (properties.type) {
    props.Type = { select: { name: properties.type } };
  }
  if (properties.tags && properties.tags.length > 0) {
    props.Tags = {
      multi_select: properties.tags.map((t) => ({ name: t })),
    };
  }
  if (properties.created) {
    props.Created = { date: { start: properties.created } };
  }
  if (properties.updated) {
    props.Updated = { date: { start: properties.updated } };
  }

  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  const result = await client.pages.create({
    parent: { database_id: databaseId },
    properties: props as any,
    children: children || [],
  });
  return { id: result.id };
}

export async function updateNotionPage(
  client: Client,
  pageId: string,
  properties: {
    title?: string;
    type?: string;
    tags?: string[];
    updated?: string;
  },
): Promise<void> {
  const props: Record<string, unknown> = {};

  if (properties.title) {
    props.Title = { title: [{ text: { content: properties.title } }] };
  }
  if (properties.type) {
    props.Type = { select: { name: properties.type } };
  }
  if (properties.tags) {
    props.Tags = {
      multi_select: properties.tags.map((t) => ({ name: t })),
    };
  }
  if (properties.updated) {
    props.Updated = { date: { start: properties.updated } };
  }

  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  await client.pages.update({
    page_id: pageId,
    properties: props as any,
  });
}

export async function replacePageContent(
  client: Client,
  pageId: string,
  children: BlockObjectRequest[],
): Promise<void> {
  const existing = await client.blocks.children.list({ block_id: pageId });
  for (const block of existing.results) {
    await client.blocks.delete({ block_id: block.id });
  }

  if (children.length > 0) {
    await client.blocks.children.append({
      block_id: pageId,
      children,
    });
  }
}

export async function queryDatabase(
  client: Client,
  databaseId: string,
  lastSyncAt?: string,
): Promise<QueryDatabaseResponse> {
  const filter = lastSyncAt
    ? {
        timestamp: 'last_edited_time' as const,
        last_edited_time: { after: lastSyncAt },
      }
    : undefined;

  return client.databases.query({
    database_id: databaseId,
    filter,
  });
}

export async function getPageBlocks(
  client: Client,
  pageId: string,
): Promise<unknown[]> {
  const blocks: unknown[] = [];
  let cursor: string | undefined;

  do {
    const response = await client.blocks.children.list({
      block_id: pageId,
      start_cursor: cursor,
    });
    blocks.push(...response.results);
    cursor = response.has_more ? response.next_cursor ?? undefined : undefined;
  } while (cursor);

  return blocks;
}
