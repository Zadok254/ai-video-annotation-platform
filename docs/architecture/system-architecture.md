# System Architecture

## Architectural principles

- **Modular monolith first:** the API owns core transactional boundaries while workers and inference adapters remain independently deployable. This keeps early development coherent without preventing later service extraction.
- **PostgreSQL is the source of truth:** Redis is a cache/queue broker, never the durable record of annotation state.
- **Object storage is immutable-by-default:** source video, derived media, exports, and model artifacts are addressed through metadata and signed, time-limited URLs.
- **Events are durable:** transactional writes create outbox records; workers publish downstream events after commit.

## Backend and frontend

```mermaid
flowchart LR
  UI[Next.js annotation workspace] -->|OIDC/JWT + HTTPS| API[FastAPI domain API]
  API --> DB[(PostgreSQL)]
  API --> Cache[(Redis)]
  API --> Store[(Object storage)]
  API --> WS[WebSocket collaboration gateway]
  API --> Outbox[Transactional outbox]
  Outbox --> Queue[Celery queues]
  Queue --> Media[Media workers]
  Queue --> AI[Inference workers]
  Media --> Store
  AI --> DB
  UI -->|signed URL| CDN[CDN / streaming origin]
  CDN --> Store
```

The web client uses React Query for server state, Zustand for editor-local state, and a typed OpenAPI client for domain calls. Browser editing state is isolated from persisted annotation revisions so an interrupted session can be reconciled safely.

## AI pipeline

```mermaid
flowchart LR
  Request[Inference request] --> Validate[Validate tenant, model, quota, media]
  Validate --> Plan[Inference manager creates idempotent plan]
  Plan --> Schedule{GPU capacity?}
  Schedule -->|yes| GPU[GPU queue]
  Schedule -->|fallback allowed| CPU[CPU queue]
  GPU --> Adapter[Versioned model adapter]
  CPU --> Adapter
  Adapter --> Calibrate[Confidence calibration]
  Calibrate --> Predictions[(Predictions + provenance)]
  Predictions --> Review[Human review queue]
```

Adapters expose a stable capability contract, rather than leaking model-specific formats into annotation tables. YOLO, ByteTrack, SAM2, PaddleOCR, and video-language models are implementation details behind that contract.

## Authentication and authorization

```mermaid
sequenceDiagram
  participant U as User
  participant W as Web client
  participant A as API
  participant D as PostgreSQL
  U->>W: Sign in
  W->>A: Credentials or external identity assertion
  A->>D: Verify user and active membership
  A-->>W: Short-lived access token + rotating refresh token
  W->>A: Organization-scoped request
  A->>D: Load membership and role permissions
  A-->>W: Allowed resource only
  A->>D: Append audit event for sensitive action
```

Tokens include subject, token type, expiration, issuer, audience, and a revocation-aware session identifier. Every organization-scoped repository call requires an organization predicate, even when a resource UUID is known.

## Storage and event flow

```mermaid
flowchart TD
  Upload[Authorized direct upload] --> Verify[Checksum and upload completion]
  Verify --> MediaRow[Video row + outbox event]
  MediaRow --> Transcode[Transcoding / thumbnails / frame index]
  Transcode --> Ready[Media ready event]
  Ready --> Annotate[Annotation & review]
  Annotate --> Version[Annotation revision]
  Version --> Export[Validated export job]
  Export --> Manifest[Immutable manifest + artifacts]
```

## Deployment

```mermaid
flowchart TB
  Internet --> WAF[WAF / ingress]
  WAF --> Web[Next.js replicas]
  WAF --> API[FastAPI replicas]
  API --> PG[(Managed PostgreSQL)]
  API --> Redis[(Managed Redis)]
  API --> S3[(Object storage)]
  Redis --> Workers[Autoscaled worker pools]
  Workers --> GPU[GPU node pool]
  API --> OTel[OpenTelemetry collector]
  Workers --> OTel
  OTel --> Obs[Logs, metrics, traces, alerts]
```

Network policy isolates database and worker resources. Secrets are provided by a managed secret store, not image layers or repository files. The Terraform-ready and Kubernetes configuration will encode these boundaries as the deployment subsystem is added.
