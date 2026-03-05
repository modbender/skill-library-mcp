export type User = {
  id: string;
  name: string;
  email: string;
  role: 'admin' | 'user';
  active: boolean;
  createdAt: string; // ISO
};

export type UserListFilters = {
  q?: string;
  role?: User['role'];
  active?: boolean | 'all';
};

export type Paginated<T> = {
  items: T[];
  total: number;
};

export type ListUsersParams = {
  page: number;
  pageSize: number;
  filters: UserListFilters;
};

export type UpsertUserInput = {
  name: string;
  email: string;
  role: User['role'];
  active: boolean;
};
