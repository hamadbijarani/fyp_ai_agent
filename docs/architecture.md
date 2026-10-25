# Architecture

```mermaid
flowchart TD
  A[Email Adapter] --> M[Normalized Message]
  B[WhatsApp Importer] --> M
  M --> C[Intent Classifier (local LLM)]
  C --> D{needs file context?}
  D -- no --> G[Response Generator]
  D -- yes --> E[Filesystem Authorizer (allow-list)]
  E --> F[Doc Ingestion + Chunking]
  F --> H[Hybrid Retrieval: filename + FAISS semantic]
  H --> I[Context Builder (bounded, sources)]
  I --> G
  G --> J[Draft Object (never sent)]
  J --> K[Notifier + Audit Log (SQLite)]
```

Security boundary: `FilesystemAuthorizer` sits outside the model. The model never controls filesystem or send actions.
