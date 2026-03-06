/**
 * Job application tracking types
 */

export enum JobStatus {
  DISCOVERED = 'DISCOVERED',
  APPLIED = 'APPLIED',
  SCREENING = 'SCREENING',
  INTERVIEWING = 'INTERVIEWING',
  OFFER = 'OFFER',
  REJECTED = 'REJECTED',
  ACCEPTED = 'ACCEPTED',
  WITHDRAWN = 'WITHDRAWN',
}

export interface Job {
  id: string;
  title: string;
  company: string;
  url?: string;
  status: JobStatus;
  salary?: string;
  location?: string;
  notes?: string;
  appliedAt?: number;
  createdAt: number;
  updatedAt: number;
}

export interface CreateJobInput {
  title: string;
  company: string;
  url?: string;
  status?: JobStatus;
  salary?: string;
  location?: string;
  notes?: string;
  appliedAt?: number;
}

export interface UpdateJobInput {
  id: string;
  title?: string;
  company?: string;
  url?: string;
  status?: JobStatus;
  salary?: string;
  location?: string;
  notes?: string;
  appliedAt?: number;
}
