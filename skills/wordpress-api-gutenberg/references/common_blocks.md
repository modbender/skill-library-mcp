# Gutenberg Block Examples

This reference provides ready-to-use Gutenberg block HTML for common content elements. Use these templates when constructing post content for WordPress REST API.

## Block Format Basics

Each block is wrapped in HTML comments:

```
<!-- wp:block-name {json_attributes} -->
Block content (HTML)
<!-- /wp:block-name -->
```

Attributes are optional JSON. For blocks with inner blocks, nest them accordingly.

## Core Blocks

### Paragraph

Simple text paragraph:

```html
<!-- wp:paragraph -->
<p>This is a paragraph of text. It can contain <strong>bold</strong>, <em>italic</em>, and <a href="https://example.com">links</a>.</p>
<!-- /wp:paragraph -->
```

With alignment and text color:

```html
<!-- wp:paragraph {"align":"center","textColor":"vivid-red"} -->
<p class="has-text-align-center has-vivid-red-color">Centered red text</p>
<!-- /wp:paragraph -->
```

### Heading

```html
<!-- wp:heading -->
<h2>Level 2 Heading</h2>
<!-- /wp:heading -->
```

```html
<!-- wp:heading {"level":3} -->
<h3>Level 3 Heading</h3>
<!-- /wp:heading -->
```

With anchor for table of contents:

```html
<!-- wp:heading {"anchor":"section-1"} -->
<h2 id="section-1">Section with Anchor</h2>
<!-- /wp:heading -->
```

### Image

Basic image (media ID must exist):

```html
<!-- wp:image {"id":123,"sizeSlug":"large"} -->
<figure class="wp-block-image size-large"><img src="https://example.com/wp-content/uploads/2025/01/image.jpg" alt="Description" class="wp-image-123"/></figure>
<!-- /wp:image -->
```

With caption and alignment:

```html
<!-- wp:image {"id":123,"align":"center","className":"is-style-rounded"} -->
<figure class="wp-block-image aligncenter is-style-rounded"><img src="https://example.com/wp-content/uploads/2025/01/image.jpg" alt="Alt text" class="wp-image-123"/><figcaption class="wp-element-caption">Image caption text</figcaption></figure>
<!-- /wp:image -->
```

### List

Unordered list:

```html
<!-- wp:list -->
<ul>
<li>First item</li>
<li>Second item</li>
<li>Third item</li>
</ul>
<!-- /wp:list -->
```

Ordered list:

```html
<!-- wp:list {"ordered":true} -->
<ol>
<li>Step one</li>
<li>Step two</li>
<li>Step three</li>
</ol>
<!-- /wp:list -->
```

### Quote

```html
<!-- wp:quote -->
<blockquote class="wp-block-quote">
<p>This is a quote from someone important.</p>
<cite>— Source Name</cite>
</blockquote>
<!-- /wp:quote -->
```

Pullquote style:

```html
<!-- wp:quote {"className":"is-style-large"} -->
<blockquote class="wp-block-quote is-style-large">
<p>Large style quote for emphasis.</p>
</blockquote>
<!-- /wp:quote -->
```

### Code

```html
<!-- wp:code -->
<pre class="wp-block-code"><code>def hello_world():
    print("Hello, World!")</code></pre>
<!-- /wp:code -->
```

With language specification:

```html
<!-- wp:code {"language":"python"} -->
<pre class="wp-block-code language-python"><code>import requests

response = requests.get("https://api.example.com")</code></pre>
<!-- /wp:code -->
```

### Preformatted

```html
<!-- wp:preformatted -->
<pre class="wp-block-preformatted">This text
   preserves
      whitespace
exactly.</pre>
<!-- /wp:preformatted -->
```

### Table

```html
<!-- wp:table -->
<figure class="wp-block-table">
<table>
<thead>
<tr>
<th>Header 1</th>
<th>Header 2</th>
</tr>
</thead>
<tbody>
<tr>
<td>Row 1, Col 1</td>
<td>Row 1, Col 2</td>
</tr>
<tr>
<td>Row 2, Col 1</td>
<td>Row 2, Col 2</td>
</tr>
</tbody>
</table>
</figure>
<!-- /wp:table -->
```

### Buttons

```html
<!-- wp:buttons -->
<div class="wp-block-buttons">
<!-- wp:button -->
<div class="wp-block-button"><a class="wp-block-button__link wp-element-button" href="https://example.com">Click Me</a></div>
<!-- /wp:button -->
</div>
<!-- /wp:buttons -->
```

Multiple buttons:

```html
<!-- wp:buttons -->
<div class="wp-block-buttons">
<!-- wp:button {"textColor":"background","backgroundColor":"vivid-cyan-blue"} -->
<div class="wp-block-button"><a class="wp-block-button__link has-background-color has-vivid-cyan-blue-background-color has-text-color has-background wp-element-button" href="#features">Features</a></div>
<!-- /wp:button -->
<!-- wp:button {"textColor":"background","backgroundColor":"luminous-vivid-orange"} -->
<div class="wp-block-button"><a class="wp-block-button__link has-background-color has-luminous-vivid-orange-background-color has-text-color has-background wp-element-button" href="#pricing">Pricing</a></div>
<!-- /wp:button -->
</div>
<!-- /wp:buttons -->
```

## Layout Blocks

### Columns

Two columns:

```html
<!-- wp:columns -->
<div class="wp-block-columns">
<!-- wp:column -->
<div class="wp-block-column">
<!-- wp:paragraph -->
<p>Left column content</p>
<!-- /wp:paragraph -->
</div>
<!-- /wp:column -->
<!-- wp:column -->
<div class="wp-block-column">
<!-- wp:paragraph -->
<p>Right column content</p>
<!-- /wp:paragraph -->
</div>
<!-- /wp:column -->
</div>
<!-- /wp:columns -->
```

With width percentages:

```html
<!-- wp:columns -->
<div class="wp-block-columns">
<!-- wp:column {"width":"66.66%"} -->
<div class="wp-block-column" style="flex-basis:66.66%">
<!-- wp:paragraph -->
<p>Main content (2/3)</p>
<!-- /wp:paragraph -->
</div>
<!-- /wp:column -->
<!-- wp:column {"width":"33.33%"} -->
<div class="wp-block-column" style="flex-basis:33.33%">
<!-- wp:paragraph -->
<p>Sidebar (1/3)</p>
<!-- /wp:paragraph -->
</div>
<!-- /wp:column -->
</div>
<!-- /wp:columns -->
```

### Group

For grouping blocks with background:

```html
<!-- wp:group {"backgroundColor":"luminous-vivid-amber","layout":{"type":"constrained"}} -->
<div class="wp-block-group has-luminous-vivid-amber-background-color has-background">
<!-- wp:paragraph -->
<p>Content inside a group with yellow background.</p>
<!-- /wp:paragraph -->
</div>
<!-- /wp:group -->
```

### Separator

```html
<!-- wp:separator -->
<hr class="wp-block-separator has-alpha-channel-opacity"/>
<!-- /wp:separator -->
```

Dotted style:

```html
<!-- wp:separator {"style":{"color":{"background":"#ccc"}},"className":"is-style-dots"} -->
<hr class="wp-block-separator has-text-color has-alpha-channel-opacity has-background is-style-dots" style="background-color:#ccc;color:#ccc"/>
<!-- /wp:separator -->
```

## Media Blocks

### Gallery

```html
<!-- wp:gallery {"linkTo":"media"} -->
<figure class="wp-block-gallery has-nested-images columns-3 is-cropped">
<!-- wp:image {"id":123,"sizeSlug":"large","linkDestination":"media"} -->
<figure class="wp-block-image size-large"><a href="https://example.com/wp-content/uploads/2025/01/image1.jpg"><img src="https://example.com/wp-content/uploads/2025/01/image1.jpg" alt="" class="wp-image-123"/></a></figure>
<!-- /wp:image -->
<!-- wp:image {"id":124,"sizeSlug":"large","linkDestination":"media"} -->
<figure class="wp-block-image size-large"><a href="https://example.com/wp-content/uploads/2025/01/image2.jpg"><img src="https://example.com/wp-content/uploads/2025/01/image2.jpg" alt="" class="wp-image-124"/></a></figure>
<!-- /wp:image -->
</figure>
<!-- /wp:gallery -->
```

### Cover

Image with text overlay:

```html
<!-- wp:cover {"url":"https://example.com/wp-content/uploads/2025/01/hero.jpg","dimRatio":50,"overlayColor":"black"} -->
<div class="wp-block-cover"><span aria-hidden="true" class="wp-block-cover__background has-black-background-color has-background-dim-50 has-background-dim"></span><img class="wp-block-cover__image-background" alt="" src="https://example.com/wp-content/uploads/2025/01/hero.jpg" data-object-fit="cover"/>
<div class="wp-block-cover__inner-container">
<!-- wp:paragraph {"align":"center","textColor":"white","fontSize":"large"} -->
<p class="has-text-align-center has-white-color has-large-font-size">Hero text over image</p>
<!-- /wp:paragraph -->
</div>
</div>
<!-- /wp:cover -->
```

## Embed Blocks

### YouTube

```html
<!-- wp:embed {"url":"https://www.youtube.com/watch?v=dQw4w9WgXcQ","type":"video","providerNameSlug":"youtube","responsive":true} -->
<figure class="wp-block-embed is-type-video is-provider-youtube wp-block-embed-youtube"><div class="wp-block-embed__wrapper">
https://www.youtube.com/watch?v=dQw4w9WgXcQ
</div></figure>
<!-- /wp:embed -->
```

### Twitter

```html
<!-- wp:embed {"url":"https://twitter.com/WordPress/status/123456789","type":"rich","providerNameSlug":"twitter"} -->
<figure class="wp-block-embed is-type-rich is-provider-twitter wp-block-embed-twitter"><div class="wp-block-embed__wrapper">
https://twitter.com/WordPress/status/123456789
</div></figure>
<!-- /wp:embed -->
```

## Custom Block Examples

### Shortcode

```html
<!-- wp:shortcode -->
[my_custom_shortcode param="value"]
<!-- /wp:shortcode -->
```

### Custom HTML

```html
<!-- wp:html -->
<div class="custom-widget">
  <h3>Custom HTML</h3>
  <p>This can contain any HTML.</p>
</div>
<!-- /wp:html -->
```

## Block Combinations

### Article Introduction

```html
<!-- wp:heading -->
<h2>Article Title</h2>
<!-- /wp:heading -->

<!-- wp:paragraph -->
<p>This is the introduction paragraph that summarizes what the article is about.</p>
<!-- /wp:paragraph -->

<!-- wp:image {"id":123,"align":"center","sizeSlug":"large"} -->
<figure class="wp-block-image aligncenter size-large"><img src="https://example.com/image.jpg" alt="Relevant image" class="wp-image-123"/><figcaption class="wp-element-caption">Image caption explaining relevance</figcaption></figure>
<!-- /wp:image -->

<!-- wp:paragraph -->
<p>The article continues here...</p>
<!-- /wp:paragraph -->
```

### Feature List

```html
<!-- wp:columns -->
<div class="wp-block-columns">
<!-- wp:column -->
<div class="wp-block-column">
<!-- wp:heading {"level":3} -->
<h3>Feature One</h3>
<!-- /wp:heading -->
<!-- wp:paragraph -->
<p>Description of first feature with benefits.</p>
<!-- /wp:paragraph -->
</div>
<!-- /wp:column -->
<!-- wp:column -->
<div class="wp-block-column">
<!-- wp:heading {"level":3} -->
<h3>Feature Two</h3>
<!-- /wp:heading -->
<!-- wp:paragraph -->
<p>Description of second feature with benefits.</p>
<!-- /wp:paragraph -->
</div>
<!-- /wp:column -->
<!-- wp:column -->
<div class="wp-block-column">
<!-- wp:heading {"level":3} -->
<h3>Feature Three</h3>
<!-- /wp:heading -->
<!-- wp:paragraph -->
<p>Description of third feature with benefits.</p>
<!-- /wp:paragraph -->
</div>
<!-- /wp:column -->
</div>
<!-- /wp:columns -->
```