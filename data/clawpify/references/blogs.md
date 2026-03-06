# Shopify Blogs & Articles

Manage blogs and blog articles via the GraphQL Admin API.

## Overview

Blogs are containers for articles (blog posts). Each shop can have multiple blogs, and each blog contains multiple articles.

## List Blogs

```graphql
query ListBlogs($first: Int!) {
  blogs(first: $first) {
    nodes {
      id
      title
      handle
      articlesCount {
        count
      }
    }
  }
}
```
Variables: `{ "first": 10 }`

## Get Blog

```graphql
query GetBlog($id: ID!) {
  blog(id: $id) {
    id
    title
    handle
    articlesCount {
      count
    }
    articles(first: 10) {
      nodes {
        id
        title
        publishedAt
      }
    }
  }
}
```
Variables: `{ "id": "gid://shopify/Blog/123" }`

## Create Blog

```graphql
mutation CreateBlog($blog: BlogCreateInput!) {
  blogCreate(blog: $blog) {
    blog {
      id
      title
      handle
    }
    userErrors {
      field
      message
    }
  }
}
```
Variables:
```json
{
  "blog": {
    "title": "Company News",
    "handle": "news"
  }
}
```

## Update Blog

```graphql
mutation UpdateBlog($id: ID!, $blog: BlogUpdateInput!) {
  blogUpdate(id: $id, blog: $blog) {
    blog {
      id
      title
      handle
    }
    userErrors {
      field
      message
    }
  }
}
```
Variables:
```json
{
  "id": "gid://shopify/Blog/123",
  "blog": {
    "title": "Latest News"
  }
}
```

## Delete Blog

```graphql
mutation DeleteBlog($id: ID!) {
  blogDelete(id: $id) {
    deletedBlogId
    userErrors {
      field
      message
    }
  }
}
```

## List Articles

```graphql
query ListArticles($first: Int!, $after: String, $query: String) {
  articles(first: $first, after: $after, query: $query, sortKey: PUBLISHED_AT, reverse: true) {
    pageInfo {
      hasNextPage
      endCursor
    }
    nodes {
      id
      title
      handle
      publishedAt
      author {
        name
      }
      blog {
        title
      }
      tags
    }
  }
}
```
Variables: `{ "first": 10 }`

## Get Article

```graphql
query GetArticle($id: ID!) {
  article(id: $id) {
    id
    title
    handle
    body
    summary
    publishedAt
    author {
      name
      email
    }
    blog {
      id
      title
    }
    image {
      url
      altText
    }
    tags
    templateSuffix
  }
}
```
Variables: `{ "id": "gid://shopify/Article/123" }`

## Create Article

```graphql
mutation CreateArticle($article: ArticleCreateInput!, $blog: ArticleBlogInput) {
  articleCreate(article: $article, blog: $blog) {
    article {
      id
      title
      handle
      publishedAt
    }
    userErrors {
      field
      message
    }
  }
}
```
Variables:
```json
{
  "article": {
    "title": "Summer Collection Launch",
    "handle": "summer-collection-launch",
    "body": "<p>We're excited to announce our new summer collection...</p>",
    "summary": "Introducing our latest summer styles",
    "author": {
      "name": "Marketing Team"
    },
    "tags": ["summer", "new-arrivals", "collection"],
    "isPublished": true,
    "publishedAt": "2025-06-01T09:00:00Z"
  },
  "blog": {
    "id": "gid://shopify/Blog/123"
  }
}
```

## Create Article with Image

```graphql
mutation CreateArticleWithImage($article: ArticleCreateInput!, $blog: ArticleBlogInput) {
  articleCreate(article: $article, blog: $blog) {
    article {
      id
      title
      image {
        url
      }
    }
    userErrors {
      field
      message
    }
  }
}
```
Variables:
```json
{
  "article": {
    "title": "Product Spotlight",
    "body": "<p>Check out our featured product...</p>",
    "isPublished": true,
    "image": {
      "url": "https://example.com/images/featured.jpg",
      "altText": "Featured product image"
    }
  },
  "blog": {
    "id": "gid://shopify/Blog/123"
  }
}
```

## Update Article

```graphql
mutation UpdateArticle($id: ID!, $article: ArticleUpdateInput!) {
  articleUpdate(id: $id, article: $article) {
    article {
      id
      title
      body
    }
    userErrors {
      field
      message
    }
  }
}
```
Variables:
```json
{
  "id": "gid://shopify/Article/123",
  "article": {
    "body": "<p>Updated article content...</p>",
    "tags": ["summer", "sale", "featured"]
  }
}
```

## Move Article to Different Blog

```graphql
mutation MoveArticle($id: ID!, $article: ArticleUpdateInput!, $blog: ArticleBlogInput) {
  articleUpdate(id: $id, article: $article, blog: $blog) {
    article {
      id
      blog {
        id
        title
      }
    }
    userErrors {
      field
      message
    }
  }
}
```
Variables:
```json
{
  "id": "gid://shopify/Article/123",
  "article": {},
  "blog": {
    "id": "gid://shopify/Blog/456"
  }
}
```

## Delete Article

```graphql
mutation DeleteArticle($id: ID!) {
  articleDelete(id: $id) {
    deletedArticleId
    userErrors {
      field
      message
    }
  }
}
```

## Get Article Tags

```graphql
query GetArticleTags($limit: Int!) {
  articleTags(limit: $limit, sort: POPULAR) {
    ... on String {
      __typename
    }
  }
}
```

## Get Article Authors

```graphql
query GetArticleAuthors($first: Int!) {
  articleAuthors(first: $first) {
    nodes {
      name
    }
  }
}
```

## Search Articles by Tag

```graphql
query SearchArticlesByTag($tag: String!) {
  articles(first: 10, query: $tag) {
    nodes {
      id
      title
      tags
    }
  }
}
```
Variables: `{ "tag": "tag:summer" }`

## Article Search Filters

| Filter | Example | Description |
|--------|---------|-------------|
| `title` | `title:summer` | Filter by title |
| `author` | `author:John` | Filter by author |
| `tag` | `tag:featured` | Filter by tag |
| `blog_title` | `blog_title:News` | Filter by blog |
| `created_at` | `created_at:>2024-01-01` | Filter by creation date |
| `published_at` | `published_at:>2024-01-01` | Filter by publish date |

## API Scopes Required

- `read_content` - Read blogs and articles
- `write_content` - Create, update, delete blogs and articles

## Notes

- Articles require a blog to belong to
- Tags are strings and case-insensitive
- Use `publishedAt` to schedule future publication
- Set `isPublished: false` to save as draft
- HTML in body is sanitized by Shopify
- Images should be uploaded first or provided via URL
