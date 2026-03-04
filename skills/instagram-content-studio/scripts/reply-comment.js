const { run, replyToComment } = require("./_common");

run(({ named, positional }) => {
  const commentId = positional[0];
  const text = named.text;
  if (!commentId || !text) {
    throw new Error('Usage: reply-comment.js <comment-id> --text "reply"');
  }
  return replyToComment(commentId, text);
}, { refreshIg: true, refreshFb: true });
