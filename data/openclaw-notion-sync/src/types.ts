export interface NotionSyncConfig {
  path: string;
  notion: {
    token: string;
    rootPageId: string;
  };
  ignore: string[];
  checksums: Record<string, string>; // filepath → md5
}
