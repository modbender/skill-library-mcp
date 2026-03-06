# Package Traps

- `^1.2.3` allows minor updates — can break, use exact versions for apps
- `npm install` may update lockfile — use `npm ci` in CI/production
- `devDependencies` in production — `npm install --production` or `npm ci --omit=dev`
- `peerDependencies` not auto-installed — npm 7+ installs them, can conflict
- Lockfile not committed — different installs across machines
- `npm audit fix --force` — may do major version bumps, breaks things
- `node_modules` in Docker — use multi-stage build, don't copy from host
