# MediaWiki Templates and Parser Functions

## Template Basics

### Calling Templates
```wikitext
{{TemplateName}}
{{TemplateName|positional arg}}
{{TemplateName|param1=value1|param2=value2}}
{{TemplateName
| param1 = value1
| param2 = value2
}}
```

### Template Parameters (Definition Side)
```wikitext
{{{1}}}                    First positional parameter
{{{paramName}}}            Named parameter
{{{1|default}}}            With default value
{{{paramName|}}}           Empty default (vs undefined)
```

### Transclusion
```wikitext
{{:Page Name}}             Transclude article (with colon)
{{Template Name}}          Transclude template
{{subst:Template Name}}    Substitute (one-time expansion)
{{safesubst:Template}}     Safe substitution
{{msgnw:Template}}         Show raw wikitext
```

## Parser Functions

### Conditionals

#### #if (empty test)
```wikitext
{{#if: {{{param|}}} | not empty | empty or undefined }}
{{#if: {{{param|}}} | has value }}
```

#### #ifeq (equality test)
```wikitext
{{#ifeq: {{{type}}} | book | It's a book | Not a book }}
{{#ifeq: {{{1}}} | {{{2}}} | same | different }}
```

#### #iferror
```wikitext
{{#iferror: {{#expr: 1/0}} | Division error | OK }}
```

#### #ifexist (page exists)
```wikitext
{{#ifexist: Page Name | [[Page Name]] | Page doesn't exist }}
```

#### #ifexpr (expression test)
```wikitext
{{#ifexpr: {{{count}}} > 10 | Many | Few }}
{{#ifexpr: {{{year}}} mod 4 = 0 | Leap year candidate }}
```

#### #switch
```wikitext
{{#switch: {{{type}}}
| book = 📚 Book
| article = 📄 Article
| website = 🌐 Website
| #default = 📋 Other
}}

{{#switch: {{{1}}}
| A | B | C = First three letters
| #default = Something else
}}
```

### String Functions

#### #len
```wikitext
{{#len: Hello }}           Returns: 5
```

#### #pos (find position)
```wikitext
{{#pos: Hello World | o }}      Returns: 4 (first 'o')
{{#pos: Hello World | o | 5 }}  Returns: 7 (after position 5)
```

#### #sub (substring)
```wikitext
{{#sub: Hello World | 0 | 5 }}   Returns: Hello
{{#sub: Hello World | 6 }}       Returns: World
{{#sub: Hello World | -5 }}      Returns: World (from end)
```

#### #replace
```wikitext
{{#replace: Hello World | World | Universe }}   Returns: Hello Universe
```

#### #explode (split)
```wikitext
{{#explode: a,b,c,d | , | 2 }}   Returns: c (third element)
```

#### #urlencode / #urldecode
```wikitext
{{#urlencode: Hello World }}     Returns: Hello%20World
{{#urldecode: Hello%20World }}   Returns: Hello World
```

### Math Functions

#### #expr
```wikitext
{{#expr: 1 + 2 * 3 }}           Returns: 7
{{#expr: (1 + 2) * 3 }}         Returns: 9
{{#expr: 2 ^ 10 }}              Returns: 1024
{{#expr: 17 mod 5 }}            Returns: 2
{{#expr: floor(3.7) }}          Returns: 3
{{#expr: ceil(3.2) }}           Returns: 4
{{#expr: round(3.567, 2) }}     Returns: 3.57
{{#expr: abs(-5) }}             Returns: 5
{{#expr: sqrt(16) }}            Returns: 4
{{#expr: ln(e) }}               Returns: 1
{{#expr: sin(pi/2) }}           Returns: 1
```

**Operators:** `+`, `-`, `*`, `/`, `^` (power), `mod`, `round`, `floor`, `ceil`, `abs`, `sqrt`, `ln`, `exp`, `sin`, `cos`, `tan`, `asin`, `acos`, `atan`, `pi`, `e`

**Comparison:** `=`, `<>`, `!=`, `<`, `>`, `<=`, `>=`

**Logical:** `and`, `or`, `not`

### Date/Time Functions

#### #time
```wikitext
{{#time: Y-m-d }}                     Current: 2024-01-15
{{#time: F j, Y | 2024-01-15 }}       January 15, 2024
{{#time: Y年n月j日 | 2024-01-15 }}     2024年1月15日
{{#time: l | 2024-01-15 }}            Monday
```

**Format codes:**
| Code | Output | Description |
|------|--------|-------------|
| Y | 2024 | 4-digit year |
| y | 24 | 2-digit year |
| n | 1 | Month (no leading zero) |
| m | 01 | Month (with leading zero) |
| F | January | Full month name |
| M | Jan | Abbreviated month |
| j | 5 | Day (no leading zero) |
| d | 05 | Day (with leading zero) |
| l | Monday | Full weekday |
| D | Mon | Abbreviated weekday |
| H | 14 | Hour (24h, leading zero) |
| i | 05 | Minutes (leading zero) |
| s | 09 | Seconds (leading zero) |

#### #timel (local time)
```wikitext
{{#timel: H:i }}                      Local time
```

### Formatting Functions

#### #formatnum
```wikitext
{{#formatnum: 1234567.89 }}          1,234,567.89
{{#formatnum: 1,234.56 | R }}        1234.56 (raw)
```

#### #padleft / #padright
```wikitext
{{#padleft: 7 | 3 | 0 }}             007
{{#padright: abc | 6 | . }}          abc...
```

#### #lc / #uc / #lcfirst / #ucfirst
```wikitext
{{#lc: HELLO }}                       hello
{{#uc: hello }}                       HELLO
{{#lcfirst: HELLO }}                  hELLO
{{#ucfirst: hello }}                  Hello
{{lc: HELLO }}                        hello (shortcut)
```

### Other Functions

#### #tag
```wikitext
{{#tag: ref | Citation text | name=smith }}
Equivalent to: <ref name="smith">Citation text</ref>
```

#### #invoke (Lua modules)
```wikitext
{{#invoke: ModuleName | functionName | arg1 | arg2 }}
```

## Magic Words

### Behavior Switches
```wikitext
__NOTOC__              No table of contents
__FORCETOC__           Force TOC even with <4 headings
__TOC__                Place TOC here
__NOEDITSECTION__      No section edit links
__NEWSECTIONLINK__     Add new section link
__NONEWSECTIONLINK__   Remove new section link
__NOGALLERY__          No gallery in category
__HIDDENCAT__          Hidden category
__INDEX__              Index by search engines
__NOINDEX__            Don't index
__STATICREDIRECT__     Don't update redirect
```

### Page Variables
```wikitext
{{PAGENAME}}           Page title without namespace
{{FULLPAGENAME}}       Full page title
{{BASEPAGENAME}}       Parent page name
{{SUBPAGENAME}}        Subpage name
{{ROOTPAGENAME}}       Root page name
{{TALKPAGENAME}}       Associated talk page
{{NAMESPACE}}          Current namespace
{{NAMESPACENUMBER}}    Namespace number
{{PAGEID}}             Page ID
{{REVISIONID}}         Revision ID
```

### Site Variables
```wikitext
{{SITENAME}}           Wiki name
{{SERVER}}             Server URL
{{SERVERNAME}}         Server hostname
{{SCRIPTPATH}}         Script path
```

### Date/Time Variables
```wikitext
{{CURRENTYEAR}}        4-digit year
{{CURRENTMONTH}}       Month (01-12)
{{CURRENTMONTHNAME}}   Month name
{{CURRENTDAY}}         Day (1-31)
{{CURRENTDAYNAME}}     Day name
{{CURRENTTIME}}        HH:MM
{{CURRENTTIMESTAMP}}   YYYYMMDDHHmmss
```

### Statistics
```wikitext
{{NUMBEROFPAGES}}      Total pages
{{NUMBEROFARTICLES}}   Content pages
{{NUMBEROFFILES}}      Files
{{NUMBEROFUSERS}}      Registered users
{{NUMBEROFACTIVEUSERS}} Active users
{{NUMBEROFEDITS}}      Total edits
{{PAGESINCATEGORY:Name}} Pages in category
```

## Template Examples

### Simple Infobox
```wikitext
<noinclude>{{Documentation}}</noinclude><includeonly>
{| class="infobox" style="width:22em"
|-
! colspan="2" style="background:#ccc" | {{{title|{{PAGENAME}}}}}
{{#if:{{{image|}}}|
{{!}}-
{{!}} colspan="2" {{!}} [[File:{{{image}}}|200px|center]]
}}
|-
| '''Type''' || {{{type|Unknown}}}
|-
| '''Date''' || {{{date|—}}}
|}
</includeonly>
```

### Navbox Template
```wikitext
<noinclude>{{Documentation}}</noinclude><includeonly>
{| class="navbox" style="width:100%"
|-
! style="background:#ccf" | {{{title|Navigation}}}
|-
| {{{content|}}}
|}
</includeonly>
```

### Citation Template
```wikitext
<includeonly>{{#if:{{{author|}}}|{{{author}}}. }}{{#if:{{{title|}}}|''{{{title}}}''. }}{{#if:{{{publisher|}}}|{{{publisher}}}{{#if:{{{year|}}}|, }}}}{{{year|}}}.{{#if:{{{url|}}}| [{{{url}}} Link]}}</includeonly>
```

## Tips

1. **Pipe trick**: `[[Help:Contents|]]` displays as "Contents"
2. **Escape pipes in templates**: Use `{{!}}` for literal `|`
3. **Trim whitespace**: Parameters automatically trim whitespace
4. **Check emptiness correctly**: `{{{param|}}}` vs `{{{param}}}` - the former has empty default, latter is undefined if not passed
5. **Subst for speed**: Use `{{subst:Template}}` for templates that don't need dynamic updates
