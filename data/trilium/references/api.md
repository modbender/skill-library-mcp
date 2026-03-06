# Trilium ETAPI Reference

The External Trilium API (ETAPI) allows external applications to interact with Trilium Notes.

## Authentication
All requests must include an `Authorization` header with your ETAPI token.

## Key Endpoints

### Notes
- `GET /etapi/notes/{noteId}`: Get note metadata.
- `GET /etapi/notes/{noteId}/content`: Get note content.
- `PUT /etapi/notes/{noteId}/content`: Update note content.
- `POST /etapi/notes`: Create a new note.
- `DELETE /etapi/notes/{noteId}`: Delete a note.

### Search
- `GET /etapi/notes?search={query}`: Search for notes using the Trilium search syntax.

### Attributes
- `GET /etapi/notes/{noteId}/attributes`: Get note attributes.
- `POST /etapi/attributes`: Create a new attribute.

## Search Syntax
Trilium uses a powerful search syntax:
- `#label`: Search by label.
- `text`: Search for text in title or content.
- `ancestor:noteId`: Search within a specific branch.
