import { ListUsersParams, Paginated, UpsertUserInput, User } from './types';

function uuid() {
  return `u_${Math.random().toString(16).slice(2)}_${Date.now()}`;
}

const db: User[] = Array.from({ length: 57 }).map((_, i) => {
  const role: User['role'] = i % 9 === 0 ? 'admin' : 'user';
  return {
    id: uuid(),
    name: `User ${i + 1}`,
    email: `user${i + 1}@example.com`,
    role,
    active: i % 7 !== 0,
    createdAt: new Date(Date.now() - i * 86400000).toISOString(),
  };
});

function delay(ms: number) {
  return new Promise((r) => setTimeout(r, ms));
}

export async function listUsers(params: ListUsersParams): Promise<Paginated<User>> {
  await delay(350);
  const { page, pageSize, filters } = params;

  let items = [...db];

  if (filters.q) {
    const q = filters.q.toLowerCase();
    items = items.filter((u) => u.name.toLowerCase().includes(q) || u.email.toLowerCase().includes(q));
  }

  if (filters.role) {
    items = items.filter((u) => u.role === filters.role);
  }

  if (filters.active !== undefined && filters.active !== 'all') {
    items = items.filter((u) => u.active === filters.active);
  }

  const total = items.length;

  // sort newest first
  items.sort((a, b) => b.createdAt.localeCompare(a.createdAt));

  const start = (page - 1) * pageSize;
  const paged = items.slice(start, start + pageSize);

  return { items: paged, total };
}

export async function createUser(input: UpsertUserInput): Promise<User> {
  await delay(250);
  const user: User = {
    id: uuid(),
    createdAt: new Date().toISOString(),
    ...input,
  };
  db.unshift(user);
  return user;
}

export async function updateUser(id: string, input: UpsertUserInput): Promise<User> {
  await delay(250);
  const idx = db.findIndex((u) => u.id === id);
  if (idx === -1) throw new Error('User not found');
  db[idx] = { ...db[idx], ...input };
  return db[idx];
}

export async function deleteUser(id: string): Promise<void> {
  await delay(200);
  const idx = db.findIndex((u) => u.id === id);
  if (idx === -1) throw new Error('User not found');
  db.splice(idx, 1);
}
