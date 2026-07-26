# Security Baseline

## Controls in the first platform slice

- Passwords are stored only as Argon2id hashes; plaintext credentials never enter logs or audit payloads.
- Access tokens are short-lived, type-bound JWTs. Refresh tokens are separately typed, rotate on use, and are revoked on suspicious or explicit logout events.
- Every project and dataset operation verifies an active organization membership and the minimum role required for the action.
- API configuration requires an explicit signing secret and database URL. There are no checked-in development credentials.
- Request validation rejects unknown or malformed object shapes before domain services execute.
- Security-relevant actions create audit events with actor, organization, action, subject, request ID, and structured metadata.

## Planned controls

| Area | Approach |
| --- | --- |
| Browser security | HttpOnly/Secure refresh cookie in production, CSRF protection for cookie-authenticated writes, CSP, same-site policy, and strict CORS allow lists. |
| Upload safety | Direct signed uploads, media type allow list, content-length limits, checksum verification, malware scanning integration, and quarantined processing. |
| Abuse resistance | Per-identity and per-organization rate limits, request-size limits, idempotency keys, WAF rules, and queue quotas. |
| Data protection | TLS in transit, encryption at rest, tenant-specific access policies, expiring URLs, key rotation, and backup encryption. |
| Operations | Secrets manager, least-privilege service identities, SAST/DAST/dependency scanning, SBOM generation, and alerting on anomalous access. |

## Threat-model assumptions

The service must assume a malicious browser client, compromised user credentials, malformed media, replayed requests, accidental cross-tenant queries, and noisy/expensive inference jobs. It does not assume that a model result is trustworthy. Architecture, authorization tests, input validation, and immutable audit records are the primary defenses.
