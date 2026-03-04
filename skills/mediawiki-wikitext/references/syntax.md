# MediaWiki Wikitext Syntax Reference

Complete syntax reference for MediaWiki wikitext markup.

## Text Formatting (Inline)

| Syntax | Result | Notes |
|--------|--------|-------|
| `''text''` | *italic* | Two single quotes |
| `'''text'''` | **bold** | Three single quotes |
| `'''''text'''''` | ***bold italic*** | Five single quotes |
| `<code>text</code>` | `monospace` | Inline code |
| `<var>x</var>` | Variable style | |
| `<kbd>Ctrl</kbd>` | Keyboard input | |
| `<samp>output</samp>` | Sample output | |
| `<sub>2</sub>` | Subscript | H₂O |
| `<sup>2</sup>` | Superscript | x² |
| `<s>text</s>` | ~~strikethrough~~ | |
| `<del>text</del>` | Deleted text | Semantic |
| `<ins>text</ins>` | Inserted text | Often underlined |
| `<u>text</u>` | Underline | |
| `<small>text</small>` | Small text | |
| `<big>text</big>` | Large text | Deprecated |

## Headings

```wikitext
= Level 1 =      (Don't use - reserved for page title)
== Level 2 ==
=== Level 3 ===
==== Level 4 ====
===== Level 5 =====
====== Level 6 ======
```

**Rules:**
- Must start at line beginning
- No text after closing equals on same line
- 4+ headings auto-generate TOC (unless `__NOTOC__`)
- Spaces around heading text are optional but recommended

## Lists

### Unordered (Bullet) Lists
```wikitext
* Item 1
* Item 2
** Nested item 2.1
** Nested item 2.2
*** Deeper nesting
* Item 3
```

### Ordered (Numbered) Lists
```wikitext
# First item
# Second item
## Sub-item 2.1
## Sub-item 2.2
### Sub-sub-item
# Third item
```

### Definition Lists
```wikitext
; Term 1
: Definition 1
; Term 2
: Definition 2a
: Definition 2b
```

### Mixed Lists
```wikitext
# Numbered item
#* Bullet under numbered
#* Another bullet
# Next numbered
#: Definition-style continuation
```

### Indentation
```wikitext
: Single indent
:: Double indent
::: Triple indent
```

**Note:** List markers must be at line start. Blank lines end the list.

## Links

### Internal Links
```wikitext
[[Page Name]]
[[Page Name|Display Text]]
[[Page Name#Section]]
[[Page Name#Section|Display Text]]
[[Namespace:Page Name]]
[[/Subpage]]
[[../Sibling Page]]
```

### External Links
```wikitext
[https://example.com]                  Numbered link [1]
[https://example.com Display Text]     Named link
https://example.com                    Auto-linked
```

### Special Links
```wikitext
[[File:Image.jpg]]                     Embed image
[[File:Image.jpg|thumb|Caption]]       Thumbnail with caption
[[File:Image.jpg|thumb|left|200px|Caption]]
[[Media:File.pdf]]                     Direct file link
[[Category:Category Name]]             Add to category
[[:Category:Category Name]]            Link to category (no add)
[[Special:RecentChanges]]              Special page
```

### Interwiki Links
```wikitext
[[en:English Article]]                 Language link
[[wikt:word]]                          Wiktionary
[[commons:File:Image.jpg]]             Wikimedia Commons
```

## Images

### Basic Syntax
```wikitext
[[File:Example.jpg|options|caption]]
```

### Image Options

| Option | Description |
|--------|-------------|
| `thumb` | Thumbnail (default right-aligned) |
| `frame` | Framed, no resize |
| `frameless` | Thumbnail without frame |
| `border` | Thin border |
| `right`, `left`, `center`, `none` | Alignment |
| `200px` | Width |
| `x100px` | Height |
| `200x100px` | Max dimensions |
| `upright` | Smart scaling for tall images |
| `upright=0.5` | Custom ratio |
| `link=Page` | Custom link target |
| `link=` | No link |
| `alt=Text` | Alt text for accessibility |

### Gallery
```wikitext
<gallery>
File:Image1.jpg|Caption 1
File:Image2.jpg|Caption 2
</gallery>

<gallery mode="packed" heights="150">
File:Image1.jpg
File:Image2.jpg
</gallery>
```

## Tables

### Basic Structure
```wikitext
{| class="wikitable"
|+ Caption
|-
! Header 1 !! Header 2 !! Header 3
|-
| Cell 1 || Cell 2 || Cell 3
|-
| Cell 4 || Cell 5 || Cell 6
|}
```

### Table Elements

| Markup | Location | Meaning |
|--------|----------|---------|
| `{|` | Start | Table start |
| `|}` | End | Table end |
| `|+` | After `{|` | Caption |
| `|-` | Row | Row separator |
| `!` | Cell | Header cell |
| `!!` | Cell | Header cell separator (same row) |
| `|` | Cell | Data cell |
| `||` | Cell | Data cell separator (same row) |

### Cell Attributes
```wikitext
| style="background:#fcc" | Red background
| colspan="2" | Spans 2 columns
| rowspan="3" | Spans 3 rows
! scope="col" | Column header
! scope="row" | Row header
```

### Sortable Table
```wikitext
{| class="wikitable sortable"
|-
! Name !! Value
|-
| Alpha || 1
| Beta || 2
|}
```

## References

### Basic Citation
```wikitext
Statement<ref>Source information</ref>

== References ==
{{Reflist}}
```

### Named References
```wikitext
First use<ref name="smith2020">Smith, 2020, p. 42</ref>
Second use<ref name="smith2020" />
```

### Grouped References
```wikitext
Note<ref group="note">Explanatory note</ref>
Source<ref>Regular citation</ref>

== Notes ==
{{Reflist|group="note"}}

== References ==
{{Reflist}}
```

## Special Tags

### nowiki (Escape Markup)
```wikitext
<nowiki>[[Not a link]]</nowiki>
<<nowiki/>nowiki>   Outputs: <nowiki>
```

### pre (Preformatted)
```wikitext
<pre>
Preformatted text
  Whitespace preserved
  '''Markup not processed'''
</pre>
```

### syntaxhighlight (Code)
```wikitext
<syntaxhighlight lang="python">
def hello():
    print("Hello")
</syntaxhighlight>

<syntaxhighlight lang="python" line="1" start="10">
# Line numbers starting at 10
</syntaxhighlight>
```

Supported languages: python, javascript, php, java, c, cpp, csharp, ruby, perl, sql, xml, html, css, json, yaml, bash, etc.

### math (LaTeX)
```wikitext
Inline: <math>E = mc^2</math>
Block: <math display="block">\sum_{i=1}^n i = \frac{n(n+1)}{2}</math>
Chemistry: <chem>H2O</chem>
```

### Transclusion Control
```wikitext
<includeonly>Only when transcluded</includeonly>
<noinclude>Only on template page itself</noinclude>
<onlyinclude>Only this part is transcluded</onlyinclude>
```

## HTML Entities

| Entity | Character | Description |
|--------|-----------|-------------|
| `&amp;` | & | Ampersand |
| `&lt;` | < | Less than |
| `&gt;` | > | Greater than |
| `&nbsp;` | (space) | Non-breaking space |
| `&mdash;` | — | Em dash |
| `&ndash;` | – | En dash |
| `&rarr;` | → | Right arrow |
| `&larr;` | ← | Left arrow |
| `&copy;` | © | Copyright |
| `&euro;` | € | Euro |
| `&#58;` | : | Colon (in definition lists) |

## Miscellaneous

### Horizontal Rule
```wikitext
----
```

### Comments
```wikitext
<!-- This is a comment -->
<!-- 
Multi-line
comment
-->
```

### Line Breaks
```wikitext
Line 1<br />Line 2
```

### Redirect
```wikitext
#REDIRECT [[Target Page]]
#REDIRECT [[Target Page#Section]]
```
Must be first line of page.

### Signatures (Talk pages)
```wikitext
~~~     Username only
~~~~    Username and timestamp
~~~~~   Timestamp only
```

### Categories
```wikitext
[[Category:Category Name]]
[[Category:Category Name|Sort Key]]
{{DEFAULTSORT:Sort Key}}
```
Place at end of article.
