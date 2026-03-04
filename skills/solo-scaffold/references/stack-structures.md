# /scaffold — Stack-Specific File Structures

Referenced by SKILL.md step 8.

## nextjs-supabase / nextjs-ai-agents

- `package.json`, `tsconfig.json`, `next.config.ts`, `tailwind.config.ts`
- `eslint.config.mjs` (flat config v9), `.prettierrc`, `components.json` (shadcn)
- `drizzle.config.ts`, `db/schema.ts`
- `vitest.config.ts`, `.env.local.example`
- `app/layout.tsx`, `app/page.tsx`, `app/globals.css`
- `lib/supabase/client.ts`, `lib/supabase/server.ts`, `lib/utils.ts`

## ios-swift

- `project.yml` (XcodeGen) — **MUST include** App Store requirements:
  - `info.properties`: `UISupportedInterfaceOrientations` (all 4), `UILaunchScreen`, `UIApplicationSceneManifest`
  - `settings.base`: `PRODUCT_BUNDLE_IDENTIFIER: <org_domain>.<name>`, `MARKETING_VERSION: "1.0.0"`, `CURRENT_PROJECT_VERSION: "1"`, `DEVELOPMENT_TEAM: <apple_dev_team>`, `CODE_SIGN_STYLE: Automatic`
- `<Name>/` with MVVM: `Models/`, `Views/`, `ViewModels/`, `Services/`
- `<Name>Tests/`, `Package.swift`, `.swiftlint.yml`
- Makefile must include `archive` target: `xcodegen generate && xcodebuild archive -scheme <Name> ...`

## kotlin-android

- `build.gradle.kts` — **MUST include** Play Store requirements:
  - `applicationId = "<org_domain>.<name>"`, `namespace = "<org_domain>.<name>"`
  - `compileSdk = 35`, `targetSdk = 35`, `minSdk = 26`
  - `versionCode = 1`, `versionName = "1.0.0"`
  - `signingConfigs` block loading from `keystore.properties` (gitignored)
- `gradle/libs.versions.toml`
- `app/src/main/kotlin/<org_domain_path>/<name>/` with `ui/`, `data/`, `domain/`
- `detekt.yml`, `keystore.properties.example`
- Makefile must include `release` target: `./gradlew bundleRelease`

## cloudflare-workers

- `package.json`, `wrangler.toml`, `tsconfig.json`
- `src/index.ts`, `test/index.test.ts`

## astro-static

- `package.json`, `astro.config.mjs`
- `src/pages/index.astro`, `src/layouts/Layout.astro`, `src/content/config.ts`

## astro-hybrid (SSG + SSR)

- `package.json`, `astro.config.mjs` (output: `"server"`, adapter: `@astrojs/cloudflare`)
- `wrangler.toml` (R2 bucket binding, custom domain)
- `src/pages/index.astro` (SSG, `prerender = true`)
- `src/pages/[slug].astro` (SSR, `prerender = false` — fetches data from R2 at request time)
- `src/layouts/Layout.astro`, `src/content/config.ts`
- `src/lib/` — shared TypeScript (parsers, search indexes, data loaders)
- `scripts/upload-r2.sh` — parallel upload to R2 bucket
- Pattern: static pages for content (SSG), SSR for pages needing external data (R2/API).
  SSR pages fetch from R2 CDN with aggressive edge caching (`cacheTtl: 604800`).
  Page responses cached 24h (`s-maxage=86400`). Dev mode reads local files.
  Content Collections for markdown. Orama for client-side fulltext search.

## python-api

- `pyproject.toml`, `src/<name>/main.py`, `src/<name>/schemas/`, `src/<name>/models/`
- `alembic/`, `docker-compose.yml`, `tests/test_main.py`

## python-ml

- `pyproject.toml`, `src/<name>/main.py`, `src/<name>/models.py`
- `tests/test_main.py`
