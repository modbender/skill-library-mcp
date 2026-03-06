# Immich API Endpoints Reference

## Base URL
```
{IMMICH_URL}/api
```

## Authentication
All requests require header: `x-api-key: {API_KEY}`

## Albums
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/albums` | List all albums |
| POST | `/albums` | Create new album |
| GET | `/albums/{id}` | Get album with assets |
| PUT | `/albums/{id}` | Update album |
| DELETE | `/albums/{id}` | Delete album |
| PUT | `/albums/{id}/assets` | Add assets to album |
| DELETE | `/albums/{id}/assets` | Remove assets from album |
| GET | `/albums/{id}/cover-image` | Get album cover |
| PUT | `/albums/{id}/cover-image` | Set album cover |

## Assets
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/assets` | List assets (paginated) |
| POST | `/assets` | Upload new asset |
| GET | `/assets/{id}` | Get asset info |
| PUT | `/assets/{id}` | Update asset metadata |
| DELETE | `/assets/{id}` | Delete asset |
| GET | `/assets/{id}/thumbnail` | Get thumbnail (format=jpeg/webp) |
| GET | `/assets/{id}/original` | Download original file |
| GET | `/assets/{id}/video/playback` | Get video playback info |
| PUT | `/assets/{id}/restore` | Restore from trash |
| PUT | `/assets/{id}/archive` | Archive asset |
| PUT | `/assets/{id}/favorite` | Favorite asset |

## Users
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/users` | List all users |
| POST | `/users` | Create new user |
| GET | `/users/me` | Get current user |
| GET | `/users/{id}` | Get user by ID |
| PUT | `/users/{id}` | Update user |
| DELETE | `/users/{id}` | Delete user |
| PUT | `/users/{id}/profile-image` | Set profile image |

## Libraries (External)
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/libraries` | List libraries |
| POST | `/libraries` | Create library |
| GET | `/libraries/{id}` | Get library details |
| PUT | `/libraries/{id}` | Update library |
| DELETE | `/libraries/{id}` | Delete library |
| POST | `/libraries/{id}/scan` | Scan library |
| POST | `/libraries/{id}/remove-offline` | Remove offline files |

## Search
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/search/assets` | Search assets |
| GET | `/search/metadata` | Get searchable fields |

## Jobs
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/jobs` | Get all job statuses |
| POST | `/jobs` | Start a job |
| DELETE | `/jobs/{id}` | Cancel a job |

Job names: `thumbnail-generation`, `video-transcoding`, `metadata-extraction`, `face-detection`, `search-indexing`

## Server
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/server-info/ping` | Health check |
| GET | `/server-info/stats` | Get server statistics |
| GET | `/server-info/features` | Get feature flags |

## Tags
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/tags` | List all tags |
| POST | `/tags` | Create tag |
| PUT | `/tags/{id}` | Update tag |
| DELETE | `/tags/{id}` | Delete tag |

## Shared Links
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/shared-links` | List shared links |
| POST | `/shared-links` | Create shared link |
| PUT | `/shared-links/{id}` | Update shared link |
| DELETE | `/shared-links/{id}` | Delete shared link |

## Activity
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/activities` | List activities |
| POST | `/activities` | Create activity |
| DELETE | `/activities/{id}` | Delete activity |

## Download
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/download/info` | Get download archive info |
| GET | `/download/archive` | Download full archive |

## Key: API Key Generation
1. Log into Immich web UI
2. Go to your Profile (top right)
3. Scroll to "API Keys"
4. Click "Create API Key"
5. Copy the key (shown once!)
