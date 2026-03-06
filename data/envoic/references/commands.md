# envoic Commands Reference

## Scan

```bash
uvx envoic scan .
uvx envoic scan ~/projects --deep
uvx envoic scan . --json
uvx envoic scan . --stale-days 60
uvx envoic scan . --no-artifacts
npx envoic scan ~/projects --deep
```

## Manage

```bash
uvx envoic manage ~/projects --deep
uvx envoic manage . --stale-only
uvx envoic manage . --dry-run
npx envoic manage ~/projects --deep
```

## List

```bash
uvx envoic list ~/projects
npx envoic list ~/projects
```

## Info

```bash
uvx envoic info ~/projects/myapp/.venv
npx envoic info ~/projects/webapp/node_modules
```

## Clean

```bash
uvx envoic clean ~/projects --stale-days 90
uvx envoic clean ~/projects --dry-run
uvx envoic clean ~/projects --yes
```
