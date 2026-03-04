# Skill Categories — Skill Finder

Reference for mapping user needs to search terms.

## Common Categories

| Category | User Might Say | Search Terms |
|----------|---------------|--------------|
| **Languages** | "help with Python", "write Rust" | python, py, rust, go, typescript, swift |
| **Frameworks** | "React app", "Django project" | react, nextjs, django, rails, flutter |
| **DevOps** | "deploy this", "CI/CD" | docker, kubernetes, deploy, ci-cd, terraform |
| **Testing** | "write tests", "QA" | testing, jest, playwright, e2e, unit-test |
| **Databases** | "SQL help", "store data" | postgres, mysql, redis, mongodb, sql |
| **APIs** | "call this API", "REST" | api, rest, graphql, http, curl |
| **Git** | "commit", "PR review" | git, github, gitlab, pr, code-review |
| **Docs** | "write readme", "documentation" | docs, readme, changelog, markdown |
| **Design** | "UI help", "make it pretty" | ui, ux, design, css, tailwind |
| **AI/ML** | "machine learning", "LLM" | ai, ml, openai, llm, embeddings |
| **Security** | "security audit", "vulnerabilities" | security, audit, owasp, secrets |
| **Productivity** | "automate this", "workflow" | automation, workflow, scripts |
| **Cloud** | "AWS", "cloud deploy" | aws, gcp, azure, cloud, serverless |
| **Mobile** | "iOS app", "Android" | ios, android, mobile, flutter, react-native |

## Search Strategy by Category

### Development (Code)
Start specific, broaden if needed:
1. `"python async"` (specific)
2. `"python"` (broader)
3. `"scripting"` (broadest)

### Infrastructure (DevOps)
Include the action:
1. `"docker deploy"` (action + tool)
2. `"kubernetes helm"` (tool + subtool)
3. `"ci-cd github"` (concept + platform)

### Tooling (CLI/Services)
Try the tool name directly:
1. `"stripe"` (service name)
2. `"payment"` (domain if name fails)

## Domain Combinations

Users often need cross-domain skills:

| Combined Need | Search Terms |
|--------------|--------------|
| "Deploy my React app" | `react deploy`, `nextjs vercel` |
| "Test my API" | `api testing`, `rest test` |
| "Python for data" | `python pandas`, `data analysis` |
| "Secure my app" | `security web`, `owasp` |

## When Category is Unclear

Ask clarifying question:
> "When you say 'help with data', do you mean:
> - Storing data (databases)?
> - Analyzing data (pandas, visualization)?
> - Moving data (ETL, pipelines)?"

Then search the specific subcategory.
