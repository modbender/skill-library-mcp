const {
  run,
  postImage,
  postLocalImage,
  postCarousel,
  postLocalCarousel,
} = require("./_common");

run(async ({ named, positional }) => {
  const caption = named.caption || "";
  const items = positional;

  if (items.length === 0) {
    throw new Error(
      "Usage: post-image.js --caption <caption> <image-url-or-path> [...]"
    );
  }
  if (items.length > 10) {
    throw new Error("Maximum 10 images allowed");
  }

  const isUrl = (s) => s.startsWith("http://") || s.startsWith("https://");
  const allUrls = items.every(isUrl);
  const allLocal = items.every((s) => !isUrl(s));

  if (!allUrls && !allLocal) {
    throw new Error("Cannot mix URLs and local file paths");
  }

  let result;
  if (allUrls) {
    result =
      items.length === 1
        ? await postImage(items[0], caption)
        : await postCarousel(items, caption);
  } else {
    result =
      items.length === 1
        ? await postLocalImage(items[0], caption)
        : await postLocalCarousel(items, caption);
  }

  return {
    id: result.id,
    permalink: result.permalink,
    type: items.length === 1 ? "IMAGE" : "CAROUSEL",
  };
});
