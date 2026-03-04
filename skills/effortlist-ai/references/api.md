# 📖 EffortList AI — Technical API Reference

The EffortList AI Personal Data API provides authenticated REST endpoints for reading and writing user-scoped account data.

---

## 🔐 Authentication

- **Method:** Bearer Token in `Authorization` header.
- **Format:** `efai_<48 hex characters>` (Persistent API Keys).
- **Base URL:** `https://effortlist.io/api/v1`

---

## 📐 Data Architecture & Logic

### Hierarchy

```text
📁 Folder (Optional Container)
└── 📋 Task (Actionable Project)
    └── ✅ Todo (Granular Step / Time Slot)
```

### Business Logic & Constraints

- **Atomic Cascading Deletes:** Deleting a Folder or Task automatically purges all child records via Firestore `batch()` transactions. This prevents orphaned data.
- **Omni AI Engine:** Supports parallel task processing and intelligent break protection (`isProtectedTime`).
- **Stateless Undo/Redo:** Every mutation is strictly tracked (up to 20 snapshots). Supports targeted restoration via `?id=`.
- **Recurrence:** Supports RFC 5545 (RRule) for complex repetition patterns.
- **Fetch Logic:**
  - Use `?id=<ID>` for **Surgical Extraction** (most efficient).
  - Use `?from=` and `?to=` (ISO-8601) for **Range-Based Retrieval**.
- **Query Optimization:** Use `folderId` and `taskId` for database-level filtering.

---

## 📡 Endpoints

### ↩️ History (Undo/Redo)

| Method | Endpoint       | Description        | Params                |
| :----- | :------------- | :----------------- | :-------------------- |
| `GET`  | `/api/v1/undo` | Fetch undo history | -                     |
| `GET`  | `/api/v1/redo` | Fetch redo history | -                     |
| `POST` | `/api/v1/undo` | Reverse action     | `?id=<ID>` (optional) |
| `POST` | `/api/v1/redo` | Re-apply action    | `?id=<ID>` (optional) |

### 📁 Folders

| Method   | Endpoint          | Description   | Params / Body                                             |
| :------- | :---------------- | :------------ | :-------------------------------------------------------- |
| `GET`    | `/api/v1/folders` | List folders  | `?archived=true` (optional)                               |
| `POST`   | `/api/v1/folders` | Create folder | `{ "name", "description"? }`                              |
| `PATCH`  | `/api/v1/folders` | Update folder | `?id=<ID>` + `{ "name"?, "description"?, "isArchived"? }` |
| `DELETE` | `/api/v1/folders` | Delete folder | `?id=<ID>`                                                |

### 📋 Tasks

| Method   | Endpoint        | Description | Params / Body                                                                                    |
| :------- | :-------------- | :---------- | :----------------------------------------------------------------------------------------------- |
| `GET`    | `/api/v1/tasks` | List tasks  | `?id=`, `?folderId=`, `?archived=`                                                               |
| `POST`   | `/api/v1/tasks` | Create task | `{ "title", "description"?, "folderId"? }`                                                       |
| `PATCH`  | `/api/v1/tasks` | Update task | `?id=<ID>` + `{ "title"?, "description"?, "folderId"?, "completionPercentage"?, "isArchived"? }` |
| `DELETE` | `/api/v1/tasks` | Delete task | `?id=<ID>`                                                                                       |

### ✅ Todos

| Method   | Endpoint        | Description | Params / Body                                                                                                      |
| :------- | :-------------- | :---------- | :----------------------------------------------------------------------------------------------------------------- |
| `GET`    | `/api/v1/todos` | List todos  | `?id=`, `?taskId=`, `?from=`, `?to=`                                                                               |
| `POST`   | `/api/v1/todos` | Create todo | `{ "title", "description"?, "taskId", "dueDate"?, "endTime"?, "recurrence"?, "isReminder"?, "url"?, "location"? }` |
| `PATCH`  | `/api/v1/todos` | Update todo | `?id=<ID>` + `{ "title"?, "description"?, "taskId"?, "dueDate"?, ... }`                                            |
| `DELETE` | `/api/v1/todos` | Delete todo | `?id=<ID>`                                                                                                         |

### 💬 Chats

| Method   | Endpoint        | Description      | Params                |
| :------- | :-------------- | :--------------- | :-------------------- |
| `GET`    | `/api/v1/chats` | List/Fetch chats | `?id=<ID>` (optional) |
| `DELETE` | `/api/v1/chats` | Delete chat      | `?id=<ID>`            |

---

## ⚠️ Error Codes

- `401`: Missing or invalid API key.
- `400`: Invalid body/parameters (e.g. non-empty title).
- `404`: Entity not found or access denied.
- `500`: Internal server error.
