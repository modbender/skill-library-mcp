const { run, getComments } = require("./_common");

run(({ positional }) => {
  const mediaId = positional[0];
  if (!mediaId) throw new Error("Usage: get-comments.js <media-id>");
  return getComments(mediaId);
}, { refreshIg: true, refreshFb: true });
