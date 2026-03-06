import type { StageKey } from '../stage.js';

export type Actor = {
  id?: string;
  name?: string;
  username?: string;
};

export type WorkItemLink = {
  id: string;
  title: string;
  url?: string;
  relation?: string;
};

export type WorkItemAttachment = {
  filename: string;
  url: string;
};

export type WorkItemDetails = {
  id: string;
  title: string;
  url?: string;
  stage: StageKey;
  body?: string;
  labels: string[];
  assignees?: Actor[];
  updatedAt?: Date;
  attachments?: WorkItemAttachment[];
  linked?: WorkItemLink[];
};

export type WorkItemComment = {
  id: string;
  author?: Actor;
  body: string;
  createdAt?: Date;
  /** Internal/private comment when the platform supports it. */
  isInternal?: boolean;
};

export type ShowPayload = {
  adapter: string;
  item: WorkItemDetails;
  comments: WorkItemComment[];
};

export type CreateInput = {
  title: string;
  body: string;
};

export type IdentityPort = {
  whoami(): Promise<Actor>;
};

export type WorkItemReadPort = {
  name(): string;

  listIdsByStage(stage: StageKey): Promise<string[]>;
  listBacklogIdsInOrder(): Promise<string[]>;
  getWorkItem(id: string): Promise<WorkItemDetails>;

  listComments(
    id: string,
    opts: { limit: number; newestFirst: boolean; includeInternal: boolean },
  ): Promise<WorkItemComment[]>;
  listAttachments(id: string): Promise<WorkItemAttachment[]>;
  listLinkedWorkItems(id: string): Promise<WorkItemLink[]>;
};

export type WorkItemWritePort = {
  setStage(id: string, stage: StageKey): Promise<void>;
  addComment(id: string, body: string): Promise<void>;
  createInBacklogAndAssignToSelf(input: CreateInput): Promise<{ id: string; url?: string }>;
};

/**
 * Back-compat convenience type: the verb layer expects a single object.
 * Recommended: depend on smaller ports per use-case.
 */
export type VerbAdapter = IdentityPort & WorkItemReadPort & WorkItemWritePort;
