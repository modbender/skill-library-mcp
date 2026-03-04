const { run, getMyPosts } = require("./_common");

run(({ named }) => {
  const limit = named.limit ? Number(named.limit) : 10;
  return getMyPosts(limit);
});
