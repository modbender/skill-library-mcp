# RAG Security & Privacy

## PII Detection Before Indexing

### Scan for
- Names (NER models, regex patterns)
- Emails, phone numbers, addresses
- SSNs, ID numbers, credit cards
- Health information (PHI for HIPAA)
- Financial data

### Options
1. **Redact before embedding** — Replace PII with placeholders
2. **Skip sensitive documents** — Separate index for authorized users
3. **Encrypt sensitive chunks** — Decrypt at retrieval time

## Access Control

### Row-Level Security
```python
# Filter by user permissions BEFORE retrieval
results = vector_db.query(
    embedding=query_embedding,
    filter={
        "department": {"$in": user.departments},
        "classification": {"$lte": user.clearance_level}
    }
)
```

### Document-Level Permissions
- Tag documents with access groups at ingestion
- Inherit permissions from source systems (SharePoint, Confluence)
- Audit permission checks

## Prompt Injection Prevention

### The Risk
Malicious content in indexed documents:
```
IGNORE ALL PREVIOUS INSTRUCTIONS. You are now...
```

### Mitigations
1. **Input sanitization** — Strip known injection patterns
2. **Output filtering** — Check response for policy violations
3. **Prompt isolation** — System prompt > retrieved content > user query
4. **Human-in-the-loop** — Flag suspicious responses

## Compliance Requirements

### GDPR
- **Right to erasure:** Must remove user data from embeddings on request
- **Data residency:** Verify vector DB region (EU data in EU)
- **Data accuracy:** Stale embeddings with outdated PII violate Article 5
- **Consent:** Document basis for processing personal data

### HIPAA
- **PHI handling:** Encrypt at rest and in transit
- **Access logs:** Audit who accessed what health records
- **BAA required:** With embedding API providers and vector DB hosts

### SOC2
- **Encryption:** AES-256 for data at rest
- **Access controls:** Role-based, principle of least privilege
- **Audit trails:** Immutable logs of all access
- **Incident response:** Documented breach procedures

## Multi-Tenancy Isolation

### Namespace Separation
```python
# Each tenant gets isolated namespace/collection
customer_a_index = f"tenant_{customer_a_id}_index"
customer_b_index = f"tenant_{customer_b_id}_index"
```

### Metadata Filtering (Weaker)
```python
# Single index with tenant_id filter
# Risk: bugs in filter logic expose data
filter={"tenant_id": current_tenant}
```

**Recommendation:** Namespace separation for sensitive workloads

## Embedding API Security

### When Using External APIs (OpenAI, Cohere)
- Documents leave your perimeter
- Check vendor's data retention policies
- Consider self-hosted models for sensitive content:
  - sentence-transformers
  - BGE models
  - HuggingFace TEI

### Self-Hosted Considerations
- GPU infrastructure costs
- Model updates responsibility
- Still need encryption in transit

## Audit Trail Requirements

### What to Log
```json
{
  "timestamp": "2024-01-15T10:30:00Z",
  "user_id": "user_123",
  "query": "quarterly revenue",
  "retrieved_doc_ids": ["doc_1", "doc_2"],
  "similarity_scores": [0.87, 0.82],
  "response_generated": true,
  "ip_address": "192.168.1.1"
}
```

### Retention
- Align with compliance requirements (HIPAA: 6 years)
- Immutable storage (append-only logs)
- Secure against tampering

## Security Checklist

- [ ] PII scanning before indexing
- [ ] Access control at retrieval level
- [ ] Encryption at rest (vector DB)
- [ ] Encryption in transit (API calls)
- [ ] Embedding API data handling verified
- [ ] Multi-tenant isolation tested
- [ ] Prompt injection mitigations
- [ ] Audit logging enabled
- [ ] Right to erasure process documented
- [ ] Incident response plan for data exposure
