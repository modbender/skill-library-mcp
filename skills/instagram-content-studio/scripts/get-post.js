const { run, getPost } = require("./_common");

run(({ positional }) => {
  const mediaId = positional[0];
  if (!mediaId) throw new Error("Usage: get-post.js <media-id>");
  return getPost(mediaId);
});
