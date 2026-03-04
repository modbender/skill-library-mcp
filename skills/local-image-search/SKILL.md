---
name: local-image-search
description: Fast local image search using macOS Spotlight or fd. Search images by name, date, location, or metadata. Use when users need to find images on their local machine quickly without manual browsing.
---

# Local Image Search

Search local images quickly using macOS Spotlight or fd.

## Quick Start

### Search by Name
```bash
# Using fd (fastest)
fd -e jpg -e png -e jpeg -e heic -e webp -e gif -e tiff "pattern" /path/to/search

# Using Spotlight
mdfind -onlyin /path/to/search "kMDItemDisplayName == '*pattern*'"
```

### Search by Date
```bash
# Today
mdfind -onlyin ~/Pictures "kMDItemContentTypeTree == 'public.image' && kMDItemFSContentChangeDate > $time.today()"

# Last 7 days
mdfind -onlyin ~/Pictures "kMDItemContentTypeTree == 'public.image' && kMDItemFSContentChangeDate > $time.now(-604800)"

# This month
mdfind -onlyin ~/Pictures "kMDItemContentTypeTree == 'public.image' && kMDItemFSContentChangeDate > $time.this_month()"
```

### Search by Location (GPS)
```bash
# Has GPS coordinates
mdfind "kMDItemContentTypeTree == 'public.image' && kMDItemGPSStatus == 'GPS'"

# In specific area (approximate)
mdfind "kMDItemContentTypeTree == 'public.image' && kMDItemGPSLatitude > 39 && kMDItemGPSLatitude < 41"
```

### List All Images
```bash
# All images in home
mdfind "kMDItemContentTypeTree == 'public.image'"

# Specific directory only
mdfind -onlyin ~/Pictures "kMDItemContentTypeTree == 'public.image'"

# Specific types only
mdfind -onlyin ~/Pictures "kMDItemContentType == 'public.png'"
```

## Available Scripts

### Basic Search
- `scripts/search_by_name.sh` - Search images by filename pattern
- `scripts/search_by_date.sh` - Search by creation/modification date
- `scripts/list_all.sh` - List all images in a directory

### Advanced Search
- `scripts/search_by_location.sh` - Search by GPS coordinates
- `scripts/search_by_size.sh` - Search by image dimensions
- `scripts/search_similar.sh` - Find visually similar images (requires perceptual hash)

### Utility
- `scripts/thumbnail.sh` - Generate thumbnails for results
- `scripts/copy_results.sh` - Copy search results to destination

## Image Types Supported

| Extension | Type |
|-----------|------|
| jpg/jpeg | JPEG images |
| png | PNG images |
| heic | iPhone photos |
| webp | WebP images |
| gif | GIF images |
| tiff | TIFF images |
| raw | RAW camera files |
| dng | Digital negatives |

## Metadata Search Keys

| Key | Description |
|-----|-------------|
| kMDItemDisplayName | Filename |
| kMDItemFSContentChangeDate | Modification date |
| kMDItemContentCreationDate | Creation date |
| kMDItemPixelWidth | Image width |
| kMDItemPixelHeight | Image height |
| kMDItemGPSLatitude | GPS latitude |
| kMDItemGPSLongitude | GPS longitude |
| kMDItemMake | Camera make |
| kMDItemModel | Camera model |

## Examples

```bash
# Find all screenshots
./scripts/search_by_name.sh "Screen Shot" ~/Desktop

# Find photos from today
./scripts/search_by_date.sh today ~/Pictures

# Find iPhone photos
./scripts/search_by_name.sh "IMG_" ~/Pictures

# Copy results to folder
./scripts/search_by_date.sh today ~/Pictures | ./scripts/copy_results.sh ~/Desktop/today_photos
```

## Requirements

- macOS (uses Spotlight/mdfind)
- fd (optional, for faster filename search): `brew install fd`
- exiftool (optional, for advanced metadata): `brew install exiftool`
