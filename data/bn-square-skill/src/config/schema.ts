import { z } from "zod";

const nonEmptyString = z.string().trim().min(1);

const COOKIE_SEGMENT_PATTERN = /^[^=\s;]+=[^;]+$/;

const DEFAULT_REFERER = "https://www.binance.com/en/square";
const DEFAULT_USER_AGENT =
  "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/133.0.0.0 Safari/537.36";
const DEFAULT_POST_URL_TEMPLATE = "https://www.binance.com/en/square/post/{postId}";

export const endpointConfigSchema = z.object({
  validateSessionPath: nonEmptyString.default("/bapi/accounts/v1/private/account/user/userInfo"),
  publishPostPath: nonEmptyString.default("/bapi/composite/v1/private/pgc/content/short/create"),
  getPostStatusPath: nonEmptyString.default("/bapi/composite/v1/public/pgc/content/detail"),
  imageUploadPath: nonEmptyString.default("/bapi/composite/v1/private/pgc/content/image/upload"),
  statusQueryParam: nonEmptyString.default("postId")
});

export const imageConfigSchema = z.object({
  uploadFieldName: nonEmptyString.default("file"),
  maxBytes: z.number().int().positive().default(5 * 1024 * 1024),
  allowedMimeTypes: z.array(nonEmptyString).min(1).default(["image/jpeg", "image/png", "image/webp"])
});

export const binanceConfigSchema = z
  .object({
    cdpUrl: z.string().url().optional(),
    apiBaseUrl: z.string().url().default("https://www.binance.com"),
    cookieHeader: nonEmptyString,
    csrfToken: nonEmptyString.optional(),
    sessionToken: nonEmptyString.optional(),
    userAgent: nonEmptyString.default(DEFAULT_USER_AGENT),
    referer: z.string().url().default(DEFAULT_REFERER),
    requestTimeoutMs: z.number().int().positive().default(10_000),
    postUrlTemplate: nonEmptyString.default(DEFAULT_POST_URL_TEMPLATE),
    endpoints: endpointConfigSchema,
    image: imageConfigSchema.default({})
  })
  .superRefine((value, ctx) => {
    const segments = value.cookieHeader
      .split(";")
      .map((segment) => segment.trim())
      .filter((segment) => segment.length > 0);

    if (segments.length === 0) {
      ctx.addIssue({
        code: z.ZodIssueCode.custom,
        message: "cookieHeader is empty"
      });
      return;
    }

    for (const segment of segments) {
      if (!COOKIE_SEGMENT_PATTERN.test(segment)) {
        ctx.addIssue({
          code: z.ZodIssueCode.custom,
          message: "cookieHeader must use the format key=value; key2=value2"
        });
        break;
      }
    }
  });

export type BinanceConfig = z.infer<typeof binanceConfigSchema>;
export type EndpointConfig = z.infer<typeof endpointConfigSchema>;
export type ImageConfig = z.infer<typeof imageConfigSchema>;
