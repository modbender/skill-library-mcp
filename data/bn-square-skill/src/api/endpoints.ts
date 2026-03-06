import type { BinanceConfig } from "../config/schema";

export type EndpointKey = "validateSession" | "publishPost" | "getPostStatus" | "imageUpload";

const ensureLeadingSlash = (value: string): string => (value.startsWith("/") ? value : `/${value}`);

export const getEndpointPath = (config: BinanceConfig, key: EndpointKey): string => {
  switch (key) {
    case "validateSession":
      return ensureLeadingSlash(config.endpoints.validateSessionPath);
    case "publishPost":
      return ensureLeadingSlash(config.endpoints.publishPostPath);
    case "getPostStatus":
      return ensureLeadingSlash(config.endpoints.getPostStatusPath);
    case "imageUpload":
      return ensureLeadingSlash(config.endpoints.imageUploadPath);
    default: {
      const unknown: never = key;
      return unknown;
    }
  }
};

export const buildPostStatusQuery = (config: BinanceConfig, postId: string): Record<string, string> => ({
  [config.endpoints.statusQueryParam]: postId
});

export const resolvePostUrl = (config: BinanceConfig, postId: string): string =>
  config.postUrlTemplate.replace("{postId}", encodeURIComponent(postId));
