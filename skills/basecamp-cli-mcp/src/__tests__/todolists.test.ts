import { describe, it, expect, beforeEach } from 'vitest';
import { http, HttpResponse } from 'msw';
import { server } from './setup';
import {
  listTodolists,
  getTodolist,
  createTodolist,
  deleteTodolist,
} from '../lib/api.js';

const PROJECT_ID = 1;

const mockTodolist = {
  id: 100,
  status: 'active',
  visible_to_clients: false,
  created_at: '2024-01-15T10:00:00.000Z',
  updated_at: '2024-01-15T10:00:00.000Z',
  title: 'Test Todolist',
  inherits_status: true,
  type: 'Todolist',
  name: 'Test Todolist',
  description: 'A test todolist',
  completed: false,
  completed_ratio: '2/5',
  todos_url: 'https://3.basecampapi.com/99999999/buckets/1/todolists/100/todos.json',
  groups_url: 'https://3.basecampapi.com/99999999/buckets/1/todolists/100/groups.json',
  app_todos_url: 'https://3.basecamp.com/99999999/buckets/1/todolists/100/todos',
  bucket: {
    id: PROJECT_ID,
    name: 'Test Project',
    type: 'Project',
  },
  creator: {
    id: 1,
    name: 'Test User',
    email_address: 'test@example.com',
  },
  parent: {
    id: 50,
    title: 'Todos',
    type: 'Todoset',
  },
};

const mockTodolists = [
  mockTodolist,
  {
    ...mockTodolist,
    id: 101,
    name: 'Expérience client 🥰',
    title: 'Expérience client 🥰',
    completed_ratio: '5/10',
  },
  {
    ...mockTodolist,
    id: 102,
    name: 'Admin & Process ⚙️',
    title: 'Admin & Process ⚙️',
    completed_ratio: '0/3',
  },
];

describe('Todolists API', () => {
  beforeEach(() => {
    server.resetHandlers();
  });

  describe('listTodolists', () => {
    it('should list all todolists in a project', async () => {
      server.use(
        http.get(
          `https://3.basecampapi.com/:accountId/buckets/:projectId/todosets/:todosetId/todolists.json`,
          () => {
            return HttpResponse.json(mockTodolists);
          }
        )
      );

      const todolists = await listTodolists(PROJECT_ID);

      expect(todolists).toHaveLength(3);
      expect(todolists[0].name).toBe('Test Todolist');
      expect(todolists[1].name).toBe('Expérience client 🥰');
    });

    it('should handle project with no todolists', async () => {
      server.use(
        http.get(
          `https://3.basecampapi.com/:accountId/buckets/:projectId/todosets/:todosetId/todolists.json`,
          () => {
            return HttpResponse.json([]);
          }
        )
      );

      const todolists = await listTodolists(PROJECT_ID);

      expect(todolists).toHaveLength(0);
    });

    it('should include completed_ratio for each list', async () => {
      server.use(
        http.get(
          `https://3.basecampapi.com/:accountId/buckets/:projectId/todosets/:todosetId/todolists.json`,
          () => {
            return HttpResponse.json(mockTodolists);
          }
        )
      );

      const todolists = await listTodolists(PROJECT_ID);

      expect(todolists[0].completed_ratio).toBe('2/5');
      expect(todolists[1].completed_ratio).toBe('5/10');
      expect(todolists[2].completed_ratio).toBe('0/3');
    });
  });

  describe('getTodolist', () => {
    it('should get a single todolist', async () => {
      server.use(
        http.get(
          `https://3.basecampapi.com/:accountId/buckets/:projectId/todolists/:todolistId.json`,
          () => {
            return HttpResponse.json(mockTodolist);
          }
        )
      );

      const todolist = await getTodolist(PROJECT_ID, mockTodolist.id);

      expect(todolist.id).toBe(mockTodolist.id);
      expect(todolist.name).toBe('Test Todolist');
      expect(todolist.description).toBe('A test todolist');
    });

    it('should handle todolist not found', async () => {
      server.use(
        http.get(
          `https://3.basecampapi.com/:accountId/buckets/:projectId/todolists/:todolistId.json`,
          () => {
            return new HttpResponse(null, { status: 404 });
          }
        )
      );

      await expect(getTodolist(PROJECT_ID, 9999)).rejects.toThrow();
    });
  });

  describe('createTodolist', () => {
    it('should create a new todolist', async () => {
      const newTodolist = {
        name: 'New Todolist',
        description: 'A brand new list',
      };

      server.use(
        http.post(
          `https://3.basecampapi.com/:accountId/buckets/:projectId/todosets/:todosetId/todolists.json`,
          async ({ request }) => {
            const body = (await request.json()) as Record<string, unknown>;
            return HttpResponse.json(
              {
                ...mockTodolist,
                id: 200,
                name: body.name,
                title: body.name,
                description: body.description,
              },
              { status: 201 }
            );
          }
        )
      );

      const todolist = await createTodolist(PROJECT_ID, newTodolist);

      expect(todolist.id).toBe(200);
      expect(todolist.name).toBe('New Todolist');
      expect(todolist.description).toBe('A brand new list');
    });

    it('should create todolist without description', async () => {
      server.use(
        http.post(
          `https://3.basecampapi.com/:accountId/buckets/:projectId/todosets/:todosetId/todolists.json`,
          async ({ request }) => {
            const body = (await request.json()) as Record<string, unknown>;
            return HttpResponse.json(
              {
                ...mockTodolist,
                id: 201,
                name: body.name,
                title: body.name,
                description: '',
              },
              { status: 201 }
            );
          }
        )
      );

      const todolist = await createTodolist(PROJECT_ID, {
        name: 'Minimal List',
      });

      expect(todolist.id).toBe(201);
      expect(todolist.name).toBe('Minimal List');
    });

    it('should handle emojis in todolist name', async () => {
      const nameWithEmoji = 'Expérience client 🥰';

      server.use(
        http.post(
          `https://3.basecampapi.com/:accountId/buckets/:projectId/todosets/:todosetId/todolists.json`,
          async ({ request }) => {
            const body = (await request.json()) as Record<string, unknown>;
            return HttpResponse.json(
              {
                ...mockTodolist,
                id: 202,
                name: body.name,
                title: body.name,
              },
              { status: 201 }
            );
          }
        )
      );

      const todolist = await createTodolist(PROJECT_ID, {
        name: nameWithEmoji,
      });

      expect(todolist.name).toBe(nameWithEmoji);
    });
  });

  describe('deleteTodolist', () => {
    it('should trash a todolist', async () => {
      server.use(
        http.put(
          `https://3.basecampapi.com/:accountId/buckets/:projectId/recordings/:recordingId/status/trashed.json`,
          () => {
            return new HttpResponse(null, { status: 204 });
          }
        )
      );

      await expect(deleteTodolist(PROJECT_ID, mockTodolist.id)).resolves.not.toThrow();
    });

    it('should handle deleting non-existent todolist', async () => {
      server.use(
        http.put(
          `https://3.basecampapi.com/:accountId/buckets/:projectId/recordings/:recordingId/status/trashed.json`,
          () => {
            return new HttpResponse(null, { status: 404 });
          }
        )
      );

      await expect(deleteTodolist(PROJECT_ID, 9999)).rejects.toThrow();
    });
  });
});

describe('Todolists Edge Cases', () => {
  it('should handle special characters in name and description', async () => {
    const specialName = 'List with "quotes" & <html>';
    const specialDesc = 'Description avec accénts éèà';

    server.use(
      http.post(
        `https://3.basecampapi.com/:accountId/buckets/:projectId/todosets/:todosetId/todolists.json`,
        async ({ request }) => {
          const body = (await request.json()) as Record<string, unknown>;
          return HttpResponse.json(
            {
              ...mockTodolist,
              id: 300,
              name: body.name,
              title: body.name,
              description: body.description,
            },
            { status: 201 }
          );
        }
      )
    );

    const todolist = await createTodolist(PROJECT_ID, {
      name: specialName,
      description: specialDesc,
    });

    expect(todolist.name).toBe(specialName);
    expect(todolist.description).toBe(specialDesc);
  });
});
