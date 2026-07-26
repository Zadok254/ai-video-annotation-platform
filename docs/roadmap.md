# Delivery Roadmap

## Phase 0 — foundation (current)

1. Product requirements, architecture, data model, security baseline, and operating decisions.
2. FastAPI service skeleton with explicit configuration, health/readiness, structured errors, and OpenAPI.
3. Identity, organization membership, project, and dataset domain APIs with migrations and automated tests.
4. CI quality gates for format, lint, type checks, tests, dependency/security checks, and migration validation.

**Exit criteria:** a tenant cannot read or mutate another tenant's projects/datasets; schema changes are migration-managed; API contracts are documented and tested.

## Phase 1 — media and annotation core

1. Direct object-storage uploads, media metadata, checksum verification, and background transcoding.
2. Video playback API, thumbnails, frame indexing, streaming manifests, and cache policy.
3. Annotation types, revisions, tracks, undo/redo, comments, review queues, and WebSocket collaboration.
4. Next.js editor shell with accessible playback/timeline and typed API client.

## Phase 2 — AI assistance and data lifecycle

1. Model registry and capability contract; YOLO/ByteTrack/SAM2/PaddleOCR adapters.
2. GPU scheduling, batch/streaming inference, calibration, prediction provenance, and review policies.
3. Dataset validation, versions, exports, training splits, metrics, and model evaluation.

## Phase 3 — production operations

1. Multi-zone deployment manifests, Terraform modules, backups/restore drills, and disaster recovery runbooks.
2. OpenTelemetry dashboards, SLOs, alert policies, cost controls, and capacity planning.
3. Accessibility, load, security, and end-to-end regression suites.

Each completed module receives tests, documentation, an architecture review, and a focused commit before the next module begins.
