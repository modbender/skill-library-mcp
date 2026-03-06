# Strapi Skill — Conversation Examples

## 1. Discover content types

**User:** What content types do I have in Strapi?

```bash
cd {baseDir} && npx tsx src/index.ts content types
```

**Agent responds:** Your Strapi instance has 3 content types:
- **Article** (collection, localized, draft & publish) — title, slug, content, author, category, cover
- **Category** (collection) — name, slug, description
- **Homepage** (single, localized) — title, hero, seo

---

## 2. Understand data structure before editing

**User:** I need to create some articles. What fields do they have?

```bash
cd {baseDir} && npx tsx src/index.ts content schema article
```

**Agent responds:** Article has the following fields:
- **title** (string, required, maxLength: 255)
- **slug** (string, unique)
- **content** (richtext, localized)
- **excerpt** (text, maxLength: 500)
- **author** (relation: manyToOne → api::author.author)
- **category** (relation: manyToOne → api::category.category)
- **cover** (media)

Fields marked "required" must be provided when creating.

---

## 3. Explore relations and components

**User:** How are my content types connected?

```bash
cd {baseDir} && npx tsx src/index.ts content relations
```

**Agent responds:** Relation map:
- Article → Author (manyToOne)
- Article → Category (manyToOne)
- Article → Tag (manyToMany)
- Homepage → Featured Articles (oneToMany)

**User:** The homepage has a "seo" component. What fields does it have?

```bash
cd {baseDir} && npx tsx src/index.ts content component shared.seo
```

**Agent responds:** Component `shared.seo`:
- **metaTitle** (string, required, maxLength: 60)
- **metaDescription** (string, maxLength: 160)
- **keywords** (text)
- **canonicalURL** (string)

---

## 4. Inspect real data shape

**User:** Show me what an actual article looks like

```bash
cd {baseDir} && npx tsx src/index.ts content inspect articles
```

**Agent responds:** Sample article with populated relations:
```json
{
  "documentId": "abc123",
  "title": "Getting Started",
  "content": "...",
  "author": { "documentId": "auth1", "name": "John Doe" },
  "category": { "documentId": "cat1", "name": "Tutorials" },
  "cover": { "url": "/uploads/cover.jpg" },
  "publishedAt": "2026-01-15T10:00:00Z",
  "locale": "en"
}
```

---

## 5. Create and publish content

**User:** Create a draft article, then publish it

```bash
cd {baseDir} && npx tsx src/index.ts content create-draft articles '{"title":"Draft Post","content":"Work in progress..."}'
```

**Agent responds:** Created draft article (ID: xyz789, publishedAt: null).

**User:** Publish it now

```bash
cd {baseDir} && npx tsx src/index.ts content publish articles xyz789
```

**Agent responds:** Article "Draft Post" is now published.

---

## 6. Review drafts and published content

**User:** Show me all unpublished articles

```bash
cd {baseDir} && npx tsx src/index.ts content drafts articles '{"sort":"updatedAt:desc","populate":"author"}'
```

**Agent responds:** You have 4 draft articles: ...

---

## 7. CRUD on collection types

**User:** Create a new article titled "Getting Started"

```bash
cd {baseDir} && npx tsx src/index.ts collection create articles '{"title":"Getting Started","content":"Welcome to our blog"}'
```

**User:** Update its title

```bash
cd {baseDir} && npx tsx src/index.ts collection update articles xyz789 '{"title":"Quick Start Guide"}'
```

---

## 8. Single types

**User:** Update the homepage title

```bash
cd {baseDir} && npx tsx src/index.ts single update homepage '{"title":"Welcome to Our Site"}'
```

---

## 9. Media files

**User:** Show me all images in the media library

```bash
cd {baseDir} && npx tsx src/index.ts files find '{"filters":{"mime":{"$contains":"image"}}}'
```

**User:** Update alt text for file #5

```bash
cd {baseDir} && npx tsx src/index.ts files update 5 '{"alternativeText":"Team photo 2026"}'
```

---

## 10. Manage locales

**User:** What locales are configured?

```bash
cd {baseDir} && npx tsx src/index.ts locale list
```

**Agent responds:** 2 locales: English (en, default) and French (fr).

**User:** Add German

```bash
cd {baseDir} && npx tsx src/index.ts locale create '{"name":"German (Germany)","code":"de","isDefault":false}'
```

---

## 11. Check translation status

**User:** Which languages does article abc123 have?

```bash
cd {baseDir} && npx tsx src/index.ts localize status collection articles abc123
```

**Agent responds:** Translations for abc123:
- English (en) — exists, updated 2026-01-15
- French (fr) — exists, updated 2026-02-01
- German (de) — missing

---

## 12. Translate content

**User:** Create a French version of article abc123

```bash
cd {baseDir} && npx tsx src/index.ts localize get collection articles en abc123
cd {baseDir} && npx tsx src/index.ts localize create collection articles fr '{"title":"Pour commencer","content":"Bienvenue"}'
```

---

## 13. Get all translations

**User:** Show the homepage in all languages

```bash
cd {baseDir} && npx tsx src/index.ts localize get-all single homepage
```

**Agent responds:** Homepage across 3 locales:
- **en**: "Welcome to Our Site"
- **fr**: "Bienvenue sur notre site"
- **de**: (not translated)

---

## 14. Complex filters

**User:** Find articles by "John" containing "typescript" in the title

```bash
cd {baseDir} && npx tsx src/index.ts collection find articles '{"filters":{"$and":[{"author":{"name":{"$eq":"John"}}},{"title":{"$containsi":"typescript"}}]},"locale":"en","populate":["author","category"]}'
```

---

## 15. Upload files

**User:** Upload a hero image for the homepage

```bash
cd {baseDir} && npx tsx src/index.ts files upload /tmp/hero.jpg '{"name":"homepage-hero","alternativeText":"Hero banner image"}'
```

**Agent responds:** Uploaded file "homepage-hero" (ID: 42, URL: /uploads/hero_abc123.jpg).

**User:** Download this image from the web and upload it to Strapi: https://example.com/banner.jpg

```bash
cd {baseDir} && npx tsx src/index.ts files upload https://example.com/banner.jpg '{"alternativeText":"Banner from web"}'
```

**Agent responds:** Downloaded and uploaded "banner.jpg" (ID: 43, URL: /uploads/banner_def456.jpg).

**User:** Attach it as the cover of article xyz789

```bash
cd {baseDir} && npx tsx src/index.ts files upload /tmp/cover.png '{"alternativeText":"Article cover"}' '{"ref":"api::article.article","refId":"xyz789","field":"cover"}'
```

---

## 16. Manage end users

**User:** Show me all registered users

```bash
cd {baseDir} && npx tsx src/index.ts users find
```

**Agent responds:** 12 end users found. 10 confirmed, 2 pending confirmation.

**User:** Create a new user for the newsletter team

```bash
cd {baseDir} && npx tsx src/index.ts users create '{"username":"newsletter-editor","email":"editor@example.com","password":"Str0ng!Pass123","role":1,"confirmed":true}'
```

**User:** Block user #5

```bash
cd {baseDir} && npx tsx src/index.ts users update 5 '{"blocked":true}'
```

---

## 17. Roles and permissions

**User:** What roles are available for end users?

```bash
cd {baseDir} && npx tsx src/index.ts users roles
```

**Agent responds:** 3 end-user roles:
- **Public** (ID: 2) — unauthenticated access
- **Authenticated** (ID: 1) — default for logged-in users
- **Editor** (ID: 3) — custom role with article editing permissions

**User:** What can the Editor role do?

```bash
cd {baseDir} && npx tsx src/index.ts users role 3
```

---

## 18. Schema management (dev mode)

**User:** Create a "Review" collection type with title, rating, and body

```bash
cd {baseDir} && npx tsx src/index.ts schema create-type '{"contentType":{"displayName":"Review","singularName":"review","pluralName":"reviews","kind":"collectionType","attributes":{"title":{"type":"string","required":true},"rating":{"type":"integer","min":1,"max":5},"body":{"type":"richtext"}}}}'
```

**Agent responds:** ⚠️ This modifies the database schema. Strapi will restart.
Created content type "Review" (api::review.review).

**User:** Add a "summary" field to articles

```bash
cd {baseDir} && npx tsx src/index.ts schema add-field api::article.article summary '{"type":"text","maxLength":500}'
```

---

## 19. Configure form layout (dev mode)

**User:** Show me how the article edit form is laid out

```bash
cd {baseDir} && npx tsx src/index.ts layout get api::article.article
```

**User:** Put title and slug on one row, content full-width below

```bash
cd {baseDir} && npx tsx src/index.ts layout reorder api::article.article '[[{"name":"title","size":6},{"name":"slug","size":6}],[{"name":"content","size":12}],[{"name":"cover","size":6},{"name":"category","size":6}]]'
```

**User:** Change the label of the title field to "Article Title"

```bash
cd {baseDir} && npx tsx src/index.ts layout set-field api::article.article title '{"edit":{"label":"Article Title","description":"Main heading of the article"}}'
```

---

## 20. Raw API call

**User:** List all content types via raw API

```bash
cd {baseDir} && npx tsx src/index.ts fetch GET /content-type-builder/content-types
```
