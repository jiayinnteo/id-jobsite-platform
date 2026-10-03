# Implementation Plan — ID Job-Site Management & Communication Platform

Phased so a working MVP (auth, jobs, documents, defects, accept/reject, photos)
comes first, with external integrations (Google, WhatsApp, AI, push) layered on
behind mockable adapters.

## Phase 0 — Project Scaffolding & Dev Environment

- [x] 1. Set up the backend project skeleton and tooling
  - Create FastAPI app structure (routers, services, repositories, adapters, core/config).
  - Add dependency management (pyproject/uv), ruff + black, pytest.
  - Add `app/main.py` with a `/health` endpoint and settings loaded from env.
  - _Requirements: 13.2, 13.5_

- [x] 2. Set up local infrastructure with docker-compose
  - Services: api, postgres, redis, minio (S3), worker.
  - Add `.env.example` enumerating DB, S3, JWT, LLM, WhatsApp, Google keys.
  - _Requirements: 13.2, 13.4_

- [x] 3. Set up the Flutter app skeleton + design system
  - Initialize Flutter project; add Riverpod, dio, go_router, secure storage, image_picker, google_fonts.
  - Create app shell, routing, and a configurable API base URL.
  - Build the shared design system: warm Material 3 theme (light + dark) in `lib/theme/`, and reusable widgets (`AppScaffold`, `AppButton`, `AppCard`, `StatusChip`, `EmptyState`, `LoadingState`, `ConfirmDialog`) in `lib/widgets/`.
  - Add per-role bottom-navigation shell.
  - _Requirements: 1.2, 7.1, 14.1, 14.2, 14.3, 14.4, 14.6_

- [x] 4. Database foundation
  - Configure SQLAlchemy 2.x + Alembic; create the initial migration for core tables.
  - _Requirements: 2.1, 13.1_

## Phase 1 — Authentication & RBAC

- [x] 5. Implement user model, registration, and login
  - Argon2 password hashing; JWT access + refresh issuance; refresh rotation.
  - Register with role (ID/Client/Contractor/Worker); login; refresh; password reset request.
  - _Requirements: 1.1, 1.2, 1.3, 1.6_

- [x] 6. Implement RBAC + job-membership authorization
  - [x] Role-based `require_roles(...)` dependency; 401 on missing/expired/invalid token (`get_current_user`); 403 on insufficient role. Unit tests for the role matrix.
  - [x] Job-membership `authorize_job_access(user, job)` (creator / client / member / firm-boss), returning 403 for non-members (`app/services/common.py`).
  - _Requirements: 1.3, 1.4, 1.5_

- [x] 7. Flutter auth flow
  - Login/register screens, token storage, dio auth-refresh interceptor, route guards.
  - _Requirements: 1.2, 1.3_

## Phase 2 — Jobs & Documents

- [x] 8. Job management API + services (incl. ID_BOSS oversight)
  - Create/list/get/update job; add members; status transitions; audit entries.
  - Enforce ID-only create/delete; `firm_id` on jobs.
  - ID_BOSS firm-wide job list + read access; internal oversight reviews (flag + note) that notify the assigned ID and are hidden from client/contractor/worker.
  - _Requirements: 2.1, 2.2, 2.3, 2.4, 2.5, 13.1, 15.1, 15.2, 15.3, 15.4, 15.5, 15.6_

- [x] 9. StoragePort + document/version management
  - `StoragePort` with S3 and Mock impls; pre-signed upload/download URLs.
  - Upload quotation (xlsx/pdf), 2D/3D drawings, schedule; versioning; type/size validation.
  - _Requirements: 3.1, 3.2, 3.4, 3.5, 3.6, 13.4_

- [x] 10. Flutter jobs + document screens (+ boss oversight UI)
  - Live job list → job detail (tabbed: Overview/Documents/Defects/Photos/Chat); documents tab with pre-signed download; ID_BOSS "Review job" oversight + client review actions on the Overview tab.
  - _Requirements: 2.3, 3.3, 15.1, 15.3_

## Phase 3 — Defects, Rectification & Photos (core differentiator)

- [x] 11. Defect reporting & tracking API
  - Create defect with photos; assign to contractor; status state machine with history.
  - Notify on create/assign/status change.
  - _Requirements: 4.1, 4.2, 4.3, 4.4, 4.5, 4.6_

- [x] 12. Rectification accept/reject API
  - Mark rectified; client Accept/Reject (reject requires reason); record decision; notify ID/contractor.
  - Enforce client-only decision (403 otherwise).
  - _Requirements: 5.1, 5.2, 5.3, 5.4, 5.5_

- [x] 13. Site photo capture & gallery API
  - Upload photo attached to job/defect/visit; metadata; permission-scoped gallery; retry-safe.
  - _Requirements: 7.1, 7.2, 7.3, 7.4, 7.5_

- [x] 14. Flutter defect + photo + accept/reject UI
  - Defects tab + report-defect sheet; defect detail (status history, role-aware status advance, client Accept/Reject with reason); shared photo gallery with camera/gallery upload via pre-signed URLs.
  - _Requirements: 4.1, 4.6, 5.1, 5.2, 5.3, 7.1, 7.3_

- [x] 14b. Client reviews & ratings (API + Flutter)
  - On Completed jobs: client submits/edits a star rating (1–5) + comment; notify ID & ID_BOSS; client-only write (403 otherwise).
  - Firm views show a "Reviewed" tag + rating; aggregate average per ID and per firm.
  - _Requirements: 16.1, 16.2, 16.3, 16.4, 16.5, 16.6_

## Phase 4 — Scheduling & Contractor Workflow

- [x] 15. Contractor work queue + site-visit scheduling API (+ auto-calendar hook)
  - List assigned rectification work; create/update/cancel visits with worker, date, time; notify ID/client; expose to assigned worker.
  - On every create/update, enqueue `CalendarPort.upsert_event` for all linked participants (auto Google Calendar linking); store `google_event_id` per user for idempotent updates. CalendarPort has a mock until OAuth lands in Phase 6.
  - _Requirements: 6.1, 6.2, 6.3, 6.4, 6.5, 9.2, 9.2a_

- [x] 16. Flutter contractor + schedule UI
  - Contractor work list + schedule-visit sheet (date/time, calendar auto-link note); worker's assigned-visit screen.
  - _Requirements: 6.1, 6.2, 6.5_

## Phase 5 — Notifications

- [x] 17. In-app notifications + PushPort
  - Notification fan-out on all notifiable events; unread count; mark-read + deep link; `PushPort` (FCM/APNs) with mock.
  - _Requirements: 8.1, 8.2, 8.3, 8.4_

- [x] 18. Flutter notifications UI + push registration
  - Notification center (list, unread styling, tap-to-read) + unread **badge** on the Alerts nav icon.
  - Device push-token registration end-to-end: backend DeviceToken model + register/unregister endpoints + FCM PushPort wired into the notification fan-out (prunes dead tokens); Flutter PushService captures the FCM token on sign-in, registers it, handles refresh, unregisters on sign-out. Runs in mock mode until a Firebase project is configured (FCM_* env + native config files).
  - _Requirements: 8.2, 8.3, 8.4_

## Phase 6 — Google Calendar (bidirectional)

- [x] 19. CalendarPort + Google OAuth
  - OAuth connect/callback; secure token storage; disconnect/revoke.
  - _Requirements: 9.1, 9.4, 13.2_

- [x] 20. Two-way schedule sync worker
  - App→Google on create/update; Google→app via sync tokens; retry with backoff; surface persistent failures.
  - _Requirements: 9.2, 9.3, 9.5_

## Phase 7 — In-App Chat (First-Class)

- [x] 21. Conversation + message API with realtime delivery
  - Auto-create a conversation per job; send/list messages; per-member read state; attachments + entity links.
  - WebSocket endpoint with Redis pub/sub fan-out; notify offline members; 403 for non-members.
  - _Requirements: 11.1, 11.2, 11.3, 11.4, 11.5, 11.6_

- [x] 22. Flutter chat UI
  - Conversation screen (history, send, WhatsApp-channel badge) with **live WebSocket** updates, reached from the job-detail Chat tab.
  - _Requirements: 11.2, 11.3, 11.4, 11.5_

## Phase 8 — Agentic AI (Human-in-the-Loop) & WhatsApp

- [x] 23. LLMPort + AI draft lifecycle
  - Provider-agnostic `LLMPort` (real + mock); build job context; create `AIDraft(PENDING_REVIEW)`; never auto-send.
  - Edit/approve/reject endpoints; audit who approved. Works for both in-app chat and WhatsApp replies.
  - _Requirements: 10.1, 10.2, 10.3, 10.4, 10.5, 10.6, 10.7, 11.7_

- [x] 24. WhatsAppPort + webhook + chat bridge
  - Webhook verification + inbound receive → conversation/message, mirrored into in-app chat; send in-app/approved messages out to WhatsApp; idempotent de-dup by channel + external id; mock/disabled mode; failure retry.
  - _Requirements: 11.8, 11.9, 12.1, 12.2, 12.3, 12.4, 12.5_

- [x] 25. Flutter AI review inbox
  - Pending-review list; edit draft inline; approve-&-send / reject; empty state. Wired into the ID "AI Inbox" tab.
  - _Requirements: 10.2, 10.3, 10.4, 10.5_

## Phase 9 — Hardening & Audit

- [x] 26. Audit log + centralized error handling
  - Append-only `AuditLog` for all state-changing actions; structured error responses; input validation everywhere.
  - _Requirements: 13.1, 13.3_

- [x] 27. Test suites + CI
  - Unit (RBAC, state machines, AI never-auto-send), integration (ephemeral Postgres), webhook, Flutter widget/contract tests; CI pipeline (lint + test).
  - _Requirements: all (verification)_

## Phase 10 — Materials, Supplier Catalogues & 3D Viewing

- [x] 28. Materials + supplier catalogue backend
  - Models: MaterialSupplier, MaterialProduct, MaterialSelection; MODEL_3D document type.
  - Pluggable `SupplierCatalogue` adapters (ECO+ vinyl, Nippon paint, Lamitak, Niro, Hafary) across SG + MY; sync into DB; list products by category/supplier.
  - Per-job selections: ID proposes (notifies client); client approves / requests change; audit + notifications. Alembic 0005.
  - _Requirements: 17.1, 17.2, 17.3, 17.4, 17.5, 17.6, 17.7, 17.8_

- [x] 29. Materials Flutter UI
  - Materials tab (per-job selections with colour swatches); catalogue browser by category with supplier source links; add-selection flow; client approve / request-change.
  - _Requirements: 17.1, 17.2, 17.5, 17.6, 17.7_

- [x] 30. In-app 3D model viewing
  - `ModelViewerBody`/`ModelViewerScreen` (model_viewer_plus) renders uploaded glTF/GLB with orbit + zoom; graceful empty state; wired as a job-detail 3D tab fed by a MODEL_3D document.
  - Full 3D authoring intentionally out of scope — models imported from external tools (e.g. SketchUp).
  - _Requirements: 18.1, 18.2, 18.4, 18.5_

- [x] 31. 3D material preview (colour + texture)
  - Map a selection to a named model surface (ID); the viewer applies the mapped material to the matching glTF surface — a tiled **swatch texture** when the product has one, else a flat base colour — with a client on/off toggle.
  - Backend: model_surface + swatch_url on selections; /materials/preview + /surface endpoints; Alembic 0006 & 0007.
  - Note: texture quality depends on the uploaded model's UV maps and on having rights to the supplier swatch image; sample suppliers ship colour-only.
  - _Requirements: 18.3_
