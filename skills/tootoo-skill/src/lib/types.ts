export interface CodexEntry {
  id: string;
  content: string;
  section: string;
}

export interface AlignmentConfig {
  axiomatic_entries: CodexEntry[];
  strong_entries: CodexEntry[];
  key_tensions: Array<{from_content: string, to_content: string, strength: number}>;
  priority_relations: Array<{subject: string, object: string, strength: number}>;
}

export interface OpenClawPayload {
  soul_md: string;
  user_md: string;
  metadata: {
    username: string;
    codex_version: string;
    exported_at: string;
    sync_url: string;
  };
  alignment_config: AlignmentConfig;
}

export interface AlignmentFingerprint {
  synced_at: string;
  codex_version: string;
  username: string;
  enforcement_level: 'advisory' | 'warn' | 'strict';
  keywords: {
    axiomatic: string[];
    shadow: string[];
  };
  violations_count: number;
}
