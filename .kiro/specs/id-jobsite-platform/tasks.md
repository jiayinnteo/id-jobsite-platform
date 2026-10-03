# Implementation Plan — ID Job-Site Management & Communication Platform

Phased so a working MVP (auth, jobs, documents, defects, accept/reject, photos)
comes first, with external integrations (Google, WhatsApp, AI, push) layered on
behind mockable adapters.

## Phase 0 — Project Scaffolding & Dev Environment

- [ ] 1. Set up the backend project skeleton and tooling
  - Create FastAPI app structure (routers, services, repositories, adapters, core/config).
  - Add dependency management (pyproject/uv), ruff + black, pytest.
  - Add `app/main.py` with a `/health` endpoint and settings loaded from env.
  - _Requirements: 13.2, 13.5_

- [ ] 2. Set up local infrastructure with docker-compose
  - Services: api, postgres, redis, minio (S3), worker.
  - Add `.env.example` enumerating DB, S3, JWT, LLM, WhatsApp, Google keys.
  - _Requirements: 13.2, 13.4_

- [ ] 3. Set up the Flutter app skeleton
  - Initialize Flutter project; add Riverpod, dio, go_router, secure storage, image_picker.
  - Create app shell, routing, and a configurable API base URL.
  - _Requirements: 1.2, 7.1_

- [ ] 4. Database foundation
  - Configure SQLAlchemy 2.x + Alembic; create the initial migration for core tables.
  - _Requirements: 2.1, 13.1_

## Phase 1 — Authentication & RBAC

- [ ] 5. Implement user model, registration, and login
  - Argon2 password hashing; JWT access + refresh issuance; refresh rotation.
  - Register with role (ID/Client/Contractor/Worker); login; refresh; password reset request.
  - _Requirements: 1.1, 1.2, 1.3, 1.6_

- [ ] 6. Implement RBAC + job-membership authorization
  - `authorize(user, job, action)` dependency; 401 on expired, 403 on non-member.
  - Unit tests for role/membership matrix.
  - _Requirements: 1.3, 1.4, 1.5_

- [ ] 7. Flutter auth flow
  - Login/register screens, token storage, dio auth-refresh interceptor, route guards.
  - _Requirements: 1.2, 1.3_

## Phase 2 — Jobs & Documents

- [ ] 8. Job management API + services
  - Create/list/get/update job; add members; status transitions; audit entries.
  - Enforce ID-only create/delete.
  - _Requirements: 2.1, 2.2, 2.3, 2.4, 2.5, 13.1_

- [ ] 9. StoragePort + document/version management
  - `StoragePort` with S3 and Mock impls; pre-signed upload/download URLs.
  - Upload quotation (xlsx/pdf), 2D/3D drawings, schedule; versioning; type/size validation.
  - _Requirements: 3.1, 3.2, 3.4, 3.5, 3.6, 13.4_

- [ ] 10. Flutter jobs + document screens
  - Job list/detail; participant management (ID); document upload & viewer/download for clients.
  - _Requirements: 2.3, 3.3_

## Phase 3 — Defects, Rectification & Photos (core differentiator)

- [ ] 11. Defect reporting & tracking API
  - Create defect with photos; assign to contractor; status state machine with history.
  - Notify on create/assign/status change.
  - _Requirements: 4.1, 4.2, 4.3, 4.4, 4.5, 4.6_

- [ ] 12. Rectification accept/reject API
  - Mark rectified; client Accept/Reject (reject requires reason); record decision; notify ID/contractor.
  - Enforce client-only decision (403 otherwise).
  - _Requirements: 5.1, 5.2, 5.3, 5.4, 5.5_

- [ ] 13. Site photo capture & gallery API
  - Upload photo attached to job/defect/visit; metadata; permission-scoped gallery; retry-safe.
  - _Requirements: 7.1, 7.2, 7.3, 7.4, 7.5_

- [ ] 14. Flutter defect + photo + accept/reject UI
  - Defect create with camera capture; defect detail w/ history & photos; Accept/Reject buttons; job photo gallery.
  - _Requirements: 4.1, 4.6, 5.1, 5.2, 5.3, 7.1, 7.3_

## Phase 4 — Scheduling & Contractor Workflow

- [ ] 15. Contractor work queue + site-visit scheduling API
  - List assigned rectification work; create/update/cancel visits with worker, date, time; notify ID/client; expose to assigned worker.
  - _Requirements: 6.1, 6.2, 6.3, 6.4, 6.5_

- [ ] 16. Flutter contractor + schedule UI
  - Contractor work list; schedule a visit; worker's assigned-visit view; job schedule display.
  - _Requirements: 6.1, 6.2, 6.5_

## Phase 5 — Notifications

- [ ] 17. In-app notifications + PushPort
  - Notification fan-out on all notifiable events; unread count; mark-read + deep link; `PushPort` (FCM/APNs) with mock.
  - _Requirements: 8.1, 8.2, 8.3, 8.4_

- [ ] 18. Flutter notifications UI + push registration
  - Notification center, unread badge, device token registration, deep-link handling.
  - _Requirements: 8.2, 8.3, 8.4_

## Phase 6 — Google Calendar (bidirectional)

- [ ] 19. CalendarPort + Google OAuth
  - OAuth connect/callback; secure token storage; disconnect/revoke.
  - _Requirements: 9.1, 9.4, 13.2_

- [ ] 20. Two-way schedule sync worker
  - App→Google on create/update; Google→app via sync tokens; retry with backoff; surface persistent failures.
  - _Requirements: 9.2, 9.3, 9.5_

## Phase 7 — In-App Chat (First-Class)

- [ ] 21. Conversation + message API with realtime delivery
  - Auto-create a conversation per job; send/list messages; per-member read state; attachments + entity links.
  - WebSocket endpoint with Redis pub/sub fan-out; notify offline members; 403 for non-members.
  - _Requirements: 11.1, 11.2, 11.3, 11.4, 11.5, 11.6_

- [ ] 22. Flutter chat UI
  - Conversation screen (history newest-at-bottom), live updates, send message, attach photo/document, deep-link to defect/visit, unread markers.
  - _Requirements: 11.2, 11.3, 11.4, 11.5_

## Phase 8 — Agentic AI (Human-in-the-Loop) & WhatsApp

- [ ] 23. LLMPort + AI draft lifecycle
  - Provider-agnostic `LLMPort` (real + mock); build job context; create `AIDraft(PENDING_REVIEW)`; never auto-send.
  - Edit/approve/reject endpoints; audit who approved. Works for both in-app chat and WhatsApp replies.
  - _Requirements: 10.1, 10.2, 10.3, 10.4, 10.5, 10.6, 10.7, 11.7_

- [ ] 24. WhatsAppPort + webhook
  - Webhook verification + inbound receive → conversation/message; send approved reply; mock/disabled mode; failure retry.
  - _Requirements: 12.1, 12.2, 12.3, 12.4, 12.5_

- [ ] 25. Flutter AI review inbox
  - Pending-review list; edit draft; approve/reject; conversation view.
  - _Requirements: 10.2, 10.3, 10.4, 10.5_

## Phase 9 — Hardening & Audit

- [ ] 26. Audit log + centralized error handling
  - Append-only `AuditLog` for all state-changing actions; structured error responses; input validation everywhere.
  - _Requirements: 13.1, 13.3_

- [ ] 27. Test suites + CI
  - Unit (RBAC, state machines, AI never-auto-send), integration (ephemeral Postgres), webhook, Flutter widget/contract tests; CI pipeline (lint + test).
  - _Requirements: all (verification)_
