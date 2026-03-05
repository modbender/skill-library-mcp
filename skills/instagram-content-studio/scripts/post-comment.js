const { run, postComment } = require("./_common");

run(({ named, positional }) => {
  const mediaId = positional[0];
  const text = named.text;
  if (!mediaId || !text) {
    throw new Error('Usage: post-comment.js <media-id> --text "comment"');
  }
  return postComment(mediaId, text);
}, { refreshIg: true, refreshFb: true });
