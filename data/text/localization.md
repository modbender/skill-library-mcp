# Translation & Localization

## False Friends

**Rule:** Maintain per-language-pair blocklist. Never auto-translate without context.

### Spanish ↔ English
| Word | ❌ Wrong | ✅ Correct |
|------|----------|------------|
| actual (ES) | actual | current, present |
| actual (EN) | actual | real, verdadero |
| embarazada | embarrassed | pregnant |
| constipado | constipated | has a cold |
| sensible (ES) | sensible | sensitive |
| éxito | exit | success |
| librería | library | bookstore |
| realizar | realize | carry out, perform |

---

## Idioms

**Rule:** Detect idioms BEFORE translation. Map to equivalent OR explain meaning.

| Source | ❌ Literal | ✅ Equivalent |
|--------|-----------|---------------|
| It's raining cats and dogs | Llueven gatos y perros | Llueve a cántaros |
| Costar un ojo de la cara | Cost an eye | Cost an arm and a leg |
| Break a leg | Rómpete una pierna | ¡Mucha suerte! |
| The coast is clear | La costa está clara | No hay moros en la costa |

**Key:** Meaning transfers, not imagery.

---

## Register Consistency

Determine register ONCE, enforce throughout.

### Spanish
| Register | Pronoun | Example |
|----------|---------|---------|
| Formal | usted | "Por favor, introduzca su contraseña" |
| Informal | tú | "Introduce tu contraseña" |
| Neutral (LATAM) | usted (softer) | "Ingrese su contraseña" |

**Critical:** NEVER mix tú/usted in same document.

```
❌ "Haz clic aquí para ver su cuenta" (mixed)
✅ "Haz clic aquí para ver tu cuenta" (tú)
✅ "Haga clic aquí para ver su cuenta" (usted)
```

---

## Date/Number/Currency Formatting

**Rule:** Use locale-aware formatting. Never hardcode.

### Dates
| Locale | Format | Example |
|--------|--------|---------|
| en-US | MM/DD/YYYY | 02/13/2026 |
| en-GB | DD/MM/YYYY | 13/02/2026 |
| es-ES | DD/MM/YYYY | 13/02/2026 |
| de-DE | DD.MM.YYYY | 13.02.2026 |
| ISO | YYYY-MM-DD | 2026-02-13 |

### Numbers
| Locale | Thousands | Decimal | Example |
|--------|-----------|---------|---------|
| en-US | , | . | 1,234.56 |
| es-ES | . | , | 1.234,56 |
| de-DE | . | , | 1.234,56 |
| fr-FR | (space) | , | 1 234,56 |

**Implementation:** Use `Intl.NumberFormat` or locale libraries.

---

## Do Not Translate (DNT) List

Categories to keep untranslated:
1. **Brand names:** iPhone, Google, Netflix
2. **Technical terms:** API, ISO, GDPR
3. **Product-specific terms:** Client-defined
4. **Cultural terms:** siesta, hygge, saudade

For cultural terms:
```
Option A: Keep + explanation
  "The Danish concept of 'hygge' (cozy contentment)..."

Option B: Keep, italicized
  "She missed the Spanish *sobremesa* after meals."
```

---

## Terminology Glossary

**Rule:** Same term = same translation, always.

```yaml
term: "dashboard"
translations:
  es-ES: "panel de control"
  es-MX: "tablero"
  de-DE: "Dashboard"
do_not_use: ["escritorio", "salpicadero"]
```

### Common Inconsistencies to Prevent
| EN Term | Pick ONE ES |
|---------|-------------|
| Settings | Ajustes |
| Log in | Iniciar sesión |
| Log out | Cerrar sesión |
| Upload | Subir |
| Download | Descargar |
| Delete | Eliminar |
| Cancel | Cancelar |

---

## Regional Variants

es-ES ≠ es-MX ≠ es-AR. Treat as separate targets.

| Concept | es-ES | es-MX | es-AR |
|---------|-------|-------|-------|
| Computer | Ordenador | Computadora | Computadora |
| Car | Coche | Carro | Auto |
| Phone | Móvil | Celular | Celular |
| You (plural) | Vosotros | Ustedes | Ustedes |

**If only one Spanish:** Default to "neutral" — avoid regional slang, use ustedes.

---

## Quality Checklist

```
□ Register consistent (no tú/usted mix)
□ All glossary terms match
□ No false friends errors
□ Dates/numbers use target locale format
□ DNT terms preserved
□ Idioms adapted (not literal)
□ Character limits respected (UI)
□ Placeholders preserved ({name}, %s, {{variable}})
□ Gender agreement correct
□ Plural forms correct
```

---

## Context Requirements

**Never translate in isolation.** Always require:

1. **Where it appears:** Button? Header? Error?
2. **Character limit**
3. **Variables:** What replaces {0}?
4. **Gender of subject**
5. **Singular/plural**

Example:
```
Source: "Save"
Without context: "Guardar" or "Ahorrar"?
- Button (file) → "Guardar"
- Banking app → "Ahorrar"
```
