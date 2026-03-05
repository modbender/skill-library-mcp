# Smart accounts

**List smart accounts:** **GET** `/smart-accounts`  
Requires JWT. Returns smart accounts for the authenticated user. Supports pagination: `page`, `limit`, `sortBy`, `sortOrder`, `search` (query params).

**Get one smart account:** **GET** `/smart-accounts/:id`  
Requires JWT. User must own the smart account.

**Get workflow count for a smart account:** **GET** `/smart-accounts/:id/workflows/count`  
Response: `{ "count": number }`.

Use a smart account `id` from these endpoints as `smartAccountId` when calling `POST /ai/generate-workflow` or creating workflows.
