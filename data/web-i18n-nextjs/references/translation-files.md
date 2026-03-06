# Translation Files Reference

## JSON Key Hierarchy

Keys are organized by page/feature then section:

```json
{
  "common": {
    "loading": "Loading...",
    "error": "An error occurred",
    "success": "Success",
    "cancel": "Cancel",
    "confirm": "Confirm"
  },
  "home": {
    "metadata": {
      "title": "My App — Tagline",
      "description": "What this app does...",
      "keywords": ["keyword one", "keyword two"],
      "ogTitle": "...",
      "ogDescription": "..."
    },
    "hero": {
      "headline": "Welcome headline",
      "cta": "Get started free"
    }
  },
  "dashboard": {
    "someDialog": {
      "title": "Dialog Title",
      "description": "You have {count} items remaining.",
      "submitButton": "Submit",
      "errors": {
        "fileTooLarge": "File must be smaller than 2MB",
        "invalidFormat": "Only PNG, JPG, or WebP images are allowed"
      }
    }
  },
  "blog": {
    "metadata": {
      "title": "Blog",
      "description": "Tips and articles"
    },
    "breadcrumb": {
      "home": "Home",
      "blog": "Blog"
    }
  }
}
```

**Naming conventions:**
- `page.metadata.*` — SEO metadata fields for that page
- `page.section.*` — UI content by section
- `page.dialog.*` or `page.toast.*` — modal/notification text
- `common.*` — shared across multiple pages

## Adding Translation Keys

1. Add key to `en.json` first
2. Add the same key to **every other locale file** with a natural translation
3. Never leave a key missing in a locale — always provide either a real translation or note for the translator

## Server-Side Usage (`getDictionary`)

```typescript
// src/app/[lang]/dictionaries.ts
const dictionaries: Record<Locale, () => Promise<any>> = {
  en: () => import('./dictionaries/en.json').then((m) => m.default),
  es: () => import('./dictionaries/es.json').then((m) => m.default),
  // ... all locales
}

export const getDictionary = async (locale: Locale) => dictionaries[locale]()
```

```typescript
// In a Server Component or page.tsx:
import { getDictionary } from '../dictionaries'

export default async function Page({ params }: { params: { lang: string } }) {
  const locale = params.lang as Locale
  const dict = await getDictionary(locale)

  const t = dict?.home?.hero || {}
  return <h1>{t.headline || 'Welcome'}</h1>
}
```

## Client-Side Usage (`useDictionary`)

```typescript
// src/hooks/use-dictionary.ts
export function useDictionary() {
  const locale = useLocale()
  const [dict, setDict] = useState<any>({})

  useEffect(() => {
    if (dictionaryCache.has(locale)) {
      setDict(dictionaryCache.get(locale))
      return
    }
    dictionaries[locale]().then((loaded) => {
      dictionaryCache.set(locale, loaded)
      setDict(loaded)
    })
  }, [locale])

  return dict
}
```

```typescript
// In a Client Component:
'use client'
import { useDictionary } from '@/hooks/use-dictionary'

export function ItemCountModal({ count }: { count: number }) {
  const dict = useDictionary()
  const t = dict?.dashboard?.someDialog || {}

  return (
    <Dialog>
      <DialogTitle>{t.title || 'Dialog Title'}</DialogTitle>
      <p>
        {(t.description || 'You have {count} items.')
          .replace('{count}', String(count))}
      </p>
    </Dialog>
  )
}
```

## Fallback Pattern

Always provide a fallback string so the UI never breaks if a key is missing:

```typescript
// Good — explicit fallback
const title = dict?.home?.metadata?.title || 'My App — Tagline'

// Good — destructured with fallback object
const t = dict?.dashboard?.feedbackDialog || {}
const label = t.submit || 'Submit'
```

## Template Variable Substitution

Use `{variableName}` placeholders in translation values:

```json
{ "description": "You need {requiredCredits} credits to continue." }
```

```typescript
const message = (t.description || 'You need {requiredCredits} credits.')
  .replace('{requiredCredits}', String(requiredCredits))
```

For pluralization, use separate keys:

```json
{
  "slides_one": "1 slide",
  "slides_other": "{count} slides"
}
```
