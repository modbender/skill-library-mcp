# OpenStreetCam API Reference

Source: [OpenStreetCam API Doc](https://api.openstreetcam.org/api/doc.html)

## Base URL

- **API:** `https://api.openstreetcam.org/`
- **Terms:** https://openstreetcam.com/terms/

## Authentication

Required only for **upload** and **my-list** operations. For **nearby-tracks** and **nearby-photos** no token is needed.

- **POST /auth/openstreetmap/client_auth**  
  Body (formData): `request_token`, `secret_token` (from OSM OAuth).  
  Returns: `access_token` for use as `access_token` in other requests.

## Map / Display (no auth)

### Nearby sequences

- **POST /nearby-tracks**
- Body (formData): `lat` (number), `lng` (number), `distance` (number, radius in km).
- Response: `osv` (Nearby)`, `status`.  
  `Nearby` has `lat`, `lng`, `from`, `to`, `way_id`, `sequences[]`.

### Nearby photos

- **POST /1.0/list/nearby-photos/**
- Body (formData): `lat`, `lng`, `radius` (meters). Optional: `heading`, `wayId`, `page`, `ipp`, `externalUserId`, `date`.
- Response: paginated; includes `currentPageItems`, `totalFilteredItems`, `tracksStatus`. Each photo item has: `id`, `lat`, `lng`, `name` (full image URL), `lth_name` (large thumbnail), `th_name` (small thumbnail), `sequence_id`, `sequence_index`, `date_added`, `heading`, etc.

### Matched tracks (bounding box)

- **POST /1.0/tracks/**
- Body: `bbTopLeft` (`'lat,lng'`), `bbBottomRight` (`'lat,lng'`). Optional: `obdInfo`, `platform`, `page`, `ipp`, `zoom`, `requestedParams`.
- Use to get segments (polylines) with coverage in a bbox.

## Sequence (auth required for create/delete)

- **POST /1.0/sequence/** – Create (metaData file, uploadSource, etc.).
- **POST /details** – Get sequence details (formData: `id`).
- **POST /1.0/sequence/photo-list/** – Photo list for sequence (`sequenceId`, `access_token`).
- **POST /1.0/sequence/remove/** – Remove sequence.
- **POST /1.0/sequence/finished-uploading/** – Mark upload finished.
- **POST /1.0/list/my-list** – List of user's sequences (bbox, filters, `access_token`).

## Photo (auth for upload/remove)

- **POST /1.0/photo/** – Upload photo (sequenceId, sequenceIndex, coordinate, gpsAccuracy, photo file, `access_token`).
- **POST /1.0/photo/remove/** – Remove photo (`photoId`, `access_token`).

## Video (auth)

- **POST /1.0/video/** – Upload video to sequence (`sequenceId`, `sequenceIndex`, video file, `access_token`).

## Usage in this skill

Use only read endpoints:

1. **Geocode** city → (lat, lng).
2. **POST /nearby-tracks** with (lat, lng, distance) to discover sequences.
3. **POST /1.0/list/nearby-photos/** with (lat, lng, radius, page, ipp) to get photo list; then download from `name` or `th_name`/`lth_name` URLs.
