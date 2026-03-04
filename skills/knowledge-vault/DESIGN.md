# Design: Knowledge Vault

**Role:** The "Semantic Brain"
**Tech:** TiDB Serverless `VECTOR` type + Google Gemini Embeddings (`text-embedding-004`).

## 🏗 Architecture

1.  **Embedding:** Text -> Gemini API -> 768-dim Vector.
2.  **Storage:** TiDB Table `knowledge_vault` with `VECTOR(768)` column.
3.  **Search:** SQL `VEC_COSINE_DISTANCE` for similarity ranking.

## ⚠️ Requirements
*   `GEMINI_API_KEY` must be set in the environment.
