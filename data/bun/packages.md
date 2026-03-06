# Package Manager Traps

## Lockfile Issues

- `bun.lockb` is binary — can't read, can't diff, can't merge
- Git conflict — delete lockfile, run `bun install`, commit new one
- Mixed teams — if some use npm/yarn, maintain both lockfiles OR standardize
- CI/CD — must use `bun install --frozen-lockfile` to catch drift

## Dependency Resolution

- Resolution differs from npm — different versions picked for same package.json
- "Works on my machine" — teammate using npm gets different tree
- `bun install` auto-installs peer deps — npm doesn't, surprise extra packages
- Hoisting differs — deep dependencies may resolve to different versions

## Version Mismatches

- `^1.0.0` in Bun may resolve differently than npm for same registry state
- Peer dep conflicts — Bun picks one version, may not be what you expect
- Optional deps — handled differently, may or may not install
- Platform-specific deps — `os` and `cpu` filters may behave differently

## Workspace Traps

- `link:` protocol — resolves differently than npm workspaces
- Imports from workspace packages — may fail if not explicitly linked
- Root package scripts — `bun run` behavior in monorepo differs
- Hoisting in workspaces — dependencies may not be where expected

## Scripts

- `bun run` faster than `npm run` — but script compatibility issues
- Pre/post hooks — supported but timing may differ
- `npx` equivalent — `bunx`, but some packages incompatible
- Script environment — some env vars set differently

## Cache

- Cache location — `~/.bun/install/cache` different from npm
- `bun install --force` — clears cache and reinstalls
- Corrupted cache — delete `~/.bun` to reset
- Cache size — grows unbounded, prune manually

## Migration from npm/yarn

```bash
# Clean start
rm -rf node_modules package-lock.json yarn.lock
bun install

# Verify deps
bun pm ls

# Check for issues
bun install --dry-run
```

## Compatibility Checklist

- [ ] Delete old lockfile — start fresh
- [ ] Run `bun install` — check for errors
- [ ] Test all scripts — `bun run test`, etc.
- [ ] Verify native addons — may need rebuild
- [ ] Check peer deps — versions may differ
- [ ] Run full test suite — catch resolution bugs
- [ ] Compare node_modules — `diff` against npm install
