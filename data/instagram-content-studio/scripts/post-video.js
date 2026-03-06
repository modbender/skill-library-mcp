const {
  run,
  postVideo,
  postLocalVideo,
  postVideoCarousel,
  postLocalVideoCarousel,
} = require("./_common");

run(async ({ named, positional }) => {
  const caption = named.caption || "";
  const items = positional;

  if (items.length === 0) {
    throw new Error(
      "Usage: post-video.js --caption <caption> [--cover <url-or-path>] [--thumb-offset <ms>] [--share-to-feed <true|false>] <video-url-or-path> [...]"
    );
  }
  if (items.length > 10) {
    throw new Error("Maximum 10 videos allowed");
  }

  const isUrl = (s) => s.startsWith("http://") || s.startsWith("https://");
  const allUrls = items.every(isUrl);
  const allLocal = items.every((s) => !isUrl(s));

  if (!allUrls && !allLocal) {
    throw new Error("Cannot mix URLs and local file paths");
  }

  // Build options for single video (not applicable to carousel)
  const options = {};
  if (named.cover) options.coverUrl = named.cover;
  if (named["thumb-offset"] != null)
    options.thumbOffset = Number(named["thumb-offset"]);
  if (named["share-to-feed"] != null)
    options.shareToFeed = named["share-to-feed"] === "true";

  const hasOptions =
    options.coverUrl != null ||
    options.thumbOffset != null ||
    options.shareToFeed != null;

  if (items.length > 1 && hasOptions) {
    throw new Error(
      "--cover, --thumb-offset, and --share-to-feed are only supported for single video posts, not carousels"
    );
  }

  let result;
  if (allUrls) {
    result =
      items.length === 1
        ? await postVideo(items[0], caption, options)
        : await postVideoCarousel(items, caption);
  } else {
    result =
      items.length === 1
        ? await postLocalVideo(items[0], caption, options)
        : await postLocalVideoCarousel(items, caption);
  }

  return {
    id: result.id,
    permalink: result.permalink,
    type: items.length === 1 ? "REELS" : "CAROUSEL",
  };
});
