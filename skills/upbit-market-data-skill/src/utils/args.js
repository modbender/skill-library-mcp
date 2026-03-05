function parseArgs(argv) {
  if (!argv || argv.length === 0) {
    return { command: undefined, subcommand: undefined, options: {} };
  }

  const command = argv[0];

  let subcommand;
  let restStartIndex = 1;

  // subcommand is only valid if it does NOT start with "--"
  if (argv[1] && !argv[1].startsWith("--")) {
    subcommand = argv[1];
    restStartIndex = 2;
  }

  const rest = argv.slice(restStartIndex);
  const options = { _: [] };

  for (let i = 0; i < rest.length; i++) {
    const item = rest[i];

    if (!item.startsWith("--")) {
      options._.push(item);
      continue;
    }

    const eq = item.indexOf("=");
    if (eq !== -1) {
      const key = item.slice(2, eq);
      const value = item.slice(eq + 1);
      options[key] = value;
      continue;
    }

    const key = item.slice(2);
    const next = rest[i + 1];

    if (next && !next.startsWith("--")) {
      options[key] = next;
      i++;
    } else {
      options[key] = true;
    }
  }

  return { command, subcommand, options };
}

module.exports = { parseArgs };

