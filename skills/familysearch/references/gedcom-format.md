# GEDCOM Format Reference

GEDCOM (Genealogical Data Communication) is a plain-text format for genealogy data, developed by The Church of Jesus Christ of Latter-day Saints. GEDCOM 5.5 (1996) and 5.5.1 (2019) are the most common versions in the wild.

## Line Structure

Every line follows this format:

```
<level> [<@ID@>] <TAG> [<value>]
```

- **level**: integer (0–99). Level 0 = top-level record. Higher levels are children of the nearest lower-level line.
- **@ID@**: Optional cross-reference identifier (only on level 0 lines that define a record).
- **TAG**: 4-letter alphanumeric code (e.g., `NAME`, `BIRT`, `DEAT`).
- **value**: Optional text after the tag.

## Key Tags

### Record Types (Level 0)

| Tag | Meaning |
|-----|---------|
| `INDI` | Individual person record |
| `FAM` | Family record |
| `HEAD` | File header |
| `TRLR` | File trailer (end of file) |

### Individual Tags (Level 1 under INDI)

| Tag | Meaning |
|-----|---------|
| `NAME` | Full name: `Given /Surname/` format |
| `SEX` | Sex: M, F, or U |
| `BIRT` | Birth event block (DATE, PLAC at level 2) |
| `DEAT` | Death event block |
| `FAMC` | Family ID where this person is a child |
| `FAMS` | Family ID where this person is a spouse |

### Family Tags (Level 1 under FAM)

| Tag | Meaning |
|-----|---------|
| `HUSB` | Reference to husband (`@ID@`) |
| `WIFE` | Reference to wife (`@ID@`) |
| `CHIL` | Reference to child (`@ID@`) |
| `MARR` | Marriage event block |

## Name Format

Slashes delimit surname: `John /Smith/` → Given: John, Surname: Smith

## Date Format

`15 JAN 1850` (exact), `ABT 1850` (about), `BEF 1850` (before), `AFT 1850` (after), `BET 1840 AND 1850` (range)

## Encoding

Try UTF-8 with BOM first (`utf-8-sig`), then plain UTF-8, then `latin-1`. Don't rely on declared charset.
