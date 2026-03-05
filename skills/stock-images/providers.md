# Stock Image Providers — Complete Reference

## No-API Placeholder Services

### Lorem Picsum
The Lorem Ipsum for photos. Random images from Unsplash.

```
# Basic usage
https://picsum.photos/800/600

# Square
https://picsum.photos/400

# Specific image (consistent)
https://picsum.photos/id/237/800/600

# Grayscale
https://picsum.photos/800/600?grayscale

# Blur (1-10)
https://picsum.photos/800/600?blur=2

# Combined
https://picsum.photos/id/870/800/600?grayscale&blur=2

# WebP format
https://picsum.photos/800/600.webp

# JPEG format
https://picsum.photos/800/600.jpg

# Multiple random (prevent caching)
https://picsum.photos/800/600?random=1
https://picsum.photos/800/600?random=2

# List all images (API)
https://picsum.photos/v2/list
https://picsum.photos/v2/list?page=2&limit=100
```

### Placehold.co
Customizable placeholder images with text.

```
# Basic (gray background)
https://placehold.co/800x600

# Custom colors (bg/text in hex)
https://placehold.co/800x600/000000/ffffff

# Named colors
https://placehold.co/800x600/orange/white

# Custom text
https://placehold.co/800x600?text=Hello+World

# Retina
https://placehold.co/400x300@2x
https://placehold.co/400x300@3x

# Formats
https://placehold.co/800x600.png
https://placehold.co/800x600.jpg
https://placehold.co/800x600.webp

# Transparent background
https://placehold.co/800x600/transparent/black
```

### PlaceKeanu
Keanu Reeves placeholder images.

```
# Basic
https://placekeanu.com/800/600

# Grayscale
https://placekeanu.com/g/800/600

# Young Keanu
https://placekeanu.com/y/800/600
```

### Placeholder.com
Simple dimension placeholders.

```
# Basic
https://via.placeholder.com/800x600

# Custom colors
https://via.placeholder.com/800x600/000000/ffffff

# With text
https://via.placeholder.com/800x600?text=Placeholder
```

---

## Stock Photo APIs (Free Tier)

### Unsplash
The largest library of high-quality free photos.

**Direct URL (no API):**
```
# Random from search
https://source.unsplash.com/800x600/?nature
https://source.unsplash.com/800x600/?office,work
https://source.unsplash.com/800x600/?food,restaurant

# Specific photo by ID
https://source.unsplash.com/PHOTO_ID/800x600

# Random featured
https://source.unsplash.com/featured/800x600

# From specific user
https://source.unsplash.com/user/USERNAME/800x600
```

**API (requires free key):**
- 50 requests/hour free tier
- Sign up: https://unsplash.com/developers

### Pexels
Free stock photos and videos.

**API (requires free key):**
- Unlimited requests for non-commercial
- Sign up: https://www.pexels.com/api/

```bash
curl -H "Authorization: YOUR_API_KEY" \
  "https://api.pexels.com/v1/search?query=nature&per_page=10"
```

### Pixabay
6M+ free images, vectors, videos.

**API (requires free key):**
- Sign up: https://pixabay.com/api/docs/

```bash
curl "https://pixabay.com/api/?key=YOUR_KEY&q=nature&image_type=photo"
```

---

## Specialized Services

### Faces & Avatars

| Service | URL | Description |
|---------|-----|-------------|
| UI Faces | uifaces.co | Real human faces for mockups |
| This Person Does Not Exist | thispersondoesnotexist.com | AI-generated faces |
| RoboHash | robohash.org | Robot/alien avatars from hash |
| Boring Avatars | boringavatars.com | Abstract avatars |
| DiceBear | dicebear.com | Avatar library (API) |

```
# RoboHash
https://robohash.org/username.png

# Boring Avatars
https://source.boringavatars.com/beam/120/username

# DiceBear
https://api.dicebear.com/7.x/avataaars/svg?seed=username
```

### Icons

| Service | URL | Description |
|---------|-----|-------------|
| Iconify | iconify.design | 100k+ icons, unified API |
| Feather | feathericons.com | Clean open source icons |
| Heroicons | heroicons.com | By Tailwind CSS team |
| Lucide | lucide.dev | Feather fork, more icons |

### Illustrations

| Service | URL | Description |
|---------|-----|-------------|
| unDraw | undraw.co | Open source illustrations |
| Open Peeps | openpeeps.com | Hand-drawn illustrations |
| Humaaans | humaaans.com | Mix-and-match humans |
| Open Doodles | opendoodles.com | Sketchy illustrations |

---

## Background Removal APIs

| Service | Free Tier | API |
|---------|-----------|-----|
| Remove.bg | 50/month | Yes |
| PhotoRoom | Limited | Yes |
| Poof | Limited | Yes |
| ObjectCut | Limited | Yes |

---

## Image Optimization APIs

| Service | Free Tier | Features |
|---------|-----------|----------|
| ReSmush.it | Unlimited | Compression, no auth |
| CheetahO | Limited | Resize, optimize |
| Sirv | Limited | CDN, manipulation |

```bash
# ReSmush.it (no auth needed)
curl -X POST "http://api.resmush.it/ws.php?img=https://example.com/image.jpg"
```
