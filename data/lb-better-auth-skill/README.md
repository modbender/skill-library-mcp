# Better Auth Documentation Skill

Complete Better Auth documentation packaged as an OpenClaw AgentSkill.

## Contents

- **Authentication Methods** (OAuth providers, email/password, passkeys, magic links)
- **Database Adapters** (Prisma, Drizzle, MongoDB, PostgreSQL, etc.)
- **Plugins** (2FA, organizations, multi-session, email verification)
- **Framework Integrations** (Next.js, SvelteKit, Astro, Nuxt, etc.)
- **Migration Guides** (from NextAuth, Clerk, Auth0, Supabase, WorkOS)

## Structure

```
references/
├── authentication/   # OAuth providers (Google, GitHub, etc.)
├── adapters/         # Database adapters
├── concepts/         # Session management, cookies, OAuth
├── plugins/          # 2FA, passkeys, organizations, etc.
├── integrations/     # Framework-specific guides
├── examples/         # Working examples
└── guides/           # Migration guides & how-tos
```

## Installation

Via ClawHub:
```bash
clawhub install lb-better-auth-skill
```

Or manually: Download and extract into your OpenClaw workspace `skills/` folder.

## Usage

This skill triggers automatically when you ask questions about authentication, OAuth setup, database configuration, session management, or framework integration.

## Source

Documentation extracted from [better-auth/better-auth](https://github.com/better-auth/better-auth) (latest commit: 2026-02-06).

## License

Documentation content: MIT (from Better Auth project)
