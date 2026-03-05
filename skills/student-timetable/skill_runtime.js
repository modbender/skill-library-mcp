async function web_search(_args) {
  throw new Error('web_search runtime is not available in local node tests.');
}

async function web_fetch(_args) {
  throw new Error('web_fetch runtime is not available in local node tests.');
}

module.exports = { web_search, web_fetch };
