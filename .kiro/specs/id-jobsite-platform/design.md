# Design — ID Job-Site Management & Communication Platform

## Overview

A mobile-first platform for a Singapore interior design company that centralizes
job-site management and communication between interior designers (IDs), clients,
and contractors. The system is a **Flutter** mobile app talking to a **FastAPI**
backend backed by **PostgreSQL** and **S3-compatible** object storage. It adds a
defect/rectification workflow with explicit client accept/reject, all-party site
photo capture, bidirectional Google Calendar sync, and an **agentic AI assistant**
that drafts replies for **human approval** before they are sent over **WhatsApp**.

### Design Goals
- **Clarity of communication**: every important action produces a notification and an audit entry.
- **Role-safe**: all access is checked against role + job membership.
- **Pluggable integrations**: LLM, WhatsApp, Google, and storage sit behind interfaces so they can run in mock mode and be swapped without touching business logic.
- **Mobile-first**: optimized for on-site use — camera capture, offline-tolerant uploads, push notifications.

---

## Architecture

```
┌──────────────────────────────────────────────────────────────┐
│                      Flutter App (iOS/Android)                 │
│  Auth · Jobs · Documents · Defects · Accept/Reject · Photos    │
│  Schedule · Notifications · AI Review Inbox                    │
└───────────────▲───────────────────────────────▲───────────────┘
                │ HTTPS / REST (JSON)            │ Push (FCM/APNs)
                │                                │
┌───────────────┴────────────────────────────────────────────────┐
│                      FastAPI Backend (Python)                    │
│                                                                  │
│  API Layer (routers)   ── AuthN/AuthZ middleware (JWT + RBAC)    │
│  Service Layer         ── Jobs, Documents, Defects, Rectify,     │
│                            Scheduling, Photos, Notifications,     │
│                            AI/HITL, Messaging                     │
│  Integration Adapters  ── StoragePort · LLMPort · WhatsAppPort · │
│                            CalendarPort · PushPort (all mockable) │
│  Persistence           ── SQLAlchemy + Alembic                   │
└───────┬──────────────┬───────────────┬───────────────┬──────────┘
        │              │               │               │
   ┌────▼────┐   ┌─────▼─────┐   ┌─────▼──────┐   ┌─────▼──────┐
   │Postgres │   │ S3-compat │   │ LLM API    │   │ WhatsApp / │
   │         │   │ (MinIO/S3)│   │ (provider) │   │ Google API │
   └─────────┘   └───────────┘   └────────────┘   └────────────┘

   Background workers (async queue): calendar sync, WhatsApp send,
   AI drafting, push delivery, upload post-processing.
```

### Technology Decisions

| Concern | Choice | Rationale |
|---|---|---|
| Frontend | Flutter 3.x (Dart) | Single codebase iOS+Android, native camera, good offline/file handling |
| Backend | FastAPI (Python 3.12+) | Async, typed, fast to build, great for integrating LLM SDKs |
| ORM / migrations | SQLAlchemy 2.x + Alembic | Mature, typed, versioned schema |
| DB | PostgreSQL 15+ | Relational integrity, JSONB for flexible metadata |
| Storage | S3-compatible (MinIO in dev, S3 in prod) | Pre-signed URLs, cheap large-file storage |
| Auth | JWT access + refresh, Argon2 password hashing | Stateless API, mobile-friendly |
| Async work | **arq** + Redis | Lightweight, async-native, pairs cleanly with FastAPI; calendar/WhatsApp/AI are slow & retryable |
| Realtime chat | WebSocket (FastAPI) + Redis pub/sub | First-class in-app chat with live delivery; Redis fans out across API instances |
| LLM | Provider-agnostic `LLMPort` | Swap OpenAI/Anthropic/Bedrock without caller changes |
| Push | `PushPort` → FCM/APNs | Mobile notifications |
| Local dev | docker-compose (api, postgres, redis, minio) | One-command environment |

### State management (Flutter)
- **Riverpod** for state + dependency injection; **dio** for HTTP with auth-refresh interceptor; **go_router** for navigation; **image_picker/camera** for capture; secure storage for tokens.

---

## Data Model

```
User(id, email, password_hash, full_name, role[ID|CLIENT|CONTRACTOR|WORKER],
     phone, company_id?, google_tokens?, push_tokens[], created_at)

Company(id, name, type[ID_FIRM|CONTRACTOR], created_at)   # groups contractor workers

Job(id, name, address, status[DRAFT|ACTIVE|ON_HOLD|COMPLETED],
    created_by(ID), client_id, created_at, updated_at)

JobMember(id, job_id, user_id, role_in_job)               # membership + RBAC scope

Document(id, job_id, type[QUOTATION|DRAWING_2D|DRAWING_3D|SCHEDULE|OTHER],
         title, current_version_id, created_by, created_at)
DocumentVersion(id, document_id, version_no, storage_key, mime_type,
                size_bytes, uploaded_by, uploaded_at)

Defect(id, job_id, title, description, location,
       status[OPEN|ASSIGNED|IN_PROGRESS|RECTIFIED|ACCEPTED|REJECTED|CLOSED],
       created_by(client), assigned_contractor_id?, created_at)
DefectStatusHistory(id, defect_id, from_status, to_status, changed_by, reason?, at)

Rectification(id, defect_id, contractor_id, status, created_at)
RectificationDecision(id, rectification_id, decision[ACCEPTED|REJECTED],
                      decided_by(client), reason?, at)

SiteVisit(id, job_id, rectification_id?, contractor_id, scheduled_date,
          scheduled_time, status, created_by, created_at)
VisitWorker(id, site_visit_id, worker_id)

Photo(id, job_id, defect_id?, site_visit_id?, storage_key, caption?,
      uploaded_by, created_at)

ScheduleItem(id, job_id, title, start, end, type, google_event_id?, created_by)
CalendarLink(id, user_id, google_calendar_id, sync_token, status)

Conversation(id, job_id, channel[IN_APP|WHATSAPP], external_ref?, created_at)
Message(id, conversation_id, direction[INBOUND|OUTBOUND], sender_id,
        body, attachment_ref?, linked_entity?, status, created_at)
MessageRead(id, message_id, user_id, read_at)   # per-member read state for in-app chat
AIDraft(id, conversation_id, message_context, draft_text, edited_text?,
        status[PENDING_REVIEW|APPROVED|REJECTED|SENT], reviewed_by?, reviewed_at?)

Notification(id, user_id, type, title, body, deep_link, read_at?, created_at)
AuditLog(id, job_id?, actor_id, action, target_type, target_id, metadata(jsonb), at)
```

Key relationships: a `Job` has many members, documents, defects, photos, schedule
items and conversations. `Defect → Rectification → RectificationDecision` captures
the accept/reject flow. `SiteVisit → VisitWorker` captures contractor dispatch.

---

## Components and Interfaces

### Backend layering
- **Routers** (`/api/v1/...`): thin HTTP handlers, request/response validation via Pydantic.
- **Services**: business rules (job membership checks, state transitions, notification fan-out, audit writes).
- **Ports (adapters)**: `StoragePort`, `LLMPort`, `WhatsAppPort`, `CalendarPort`, `PushPort` — interfaces with a real and a mock implementation each, chosen by config.
- **Repositories**: SQLAlchemy data access.

### Key API surface (v1, representative)
```
POST   /auth/register           POST /auth/login        POST /auth/refresh
POST   /auth/password-reset

GET    /jobs                     POST /jobs              GET  /jobs/{id}
PATCH  /jobs/{id}                POST /jobs/{id}/members

POST   /jobs/{id}/documents      GET  /jobs/{id}/documents
POST   /documents/{id}/versions  GET  /documents/{id}/download   # pre-signed URL

POST   /jobs/{id}/defects        GET  /jobs/{id}/defects
GET    /defects/{id}             PATCH /defects/{id}/status
POST   /defects/{id}/assign

POST   /rectifications/{id}/decision     # client Accept/Reject (+reason)

GET    /contractor/work                  # assigned rectification queue
POST   /jobs/{id}/visits         PATCH /visits/{id}      POST /visits/{id}/workers

POST   /jobs/{id}/photos         GET  /jobs/{id}/photos  # upload + gallery

GET    /notifications            POST /notifications/{id}/read

POST   /integrations/google/connect      GET /integrations/google/callback
GET    /jobs/{id}/conversation            GET  /conversations/{id}/messages
POST   /conversations/{id}/messages       POST /conversations/{id}/read
WS     /ws/conversations/{id}             # realtime in-app chat (WebSocket)
POST   /webhooks/whatsapp (GET verify / POST receive)

GET    /ai/drafts                PATCH /ai/drafts/{id}   # edit
POST   /ai/drafts/{id}/approve   POST /ai/drafts/{id}/reject

GET    /health
```

### Human-in-the-loop AI flow
1. Inbound message (WhatsApp/in-app) stored → event triggers AI drafting worker.
2. Worker builds context (recent messages + defect/schedule state) and calls `LLMPort`.
3. Draft saved as `AIDraft(PENDING_REVIEW)`; ID notified. **Nothing is sent yet.**
4. ID edits/approves/rejects in the app. On approve → `WhatsAppPort.send()` (or in-app), status `SENT`, audit entry written.

### Integration adapters (mock-first)
Each port has a `Mock*` implementation enabled when credentials are absent, so the
whole app runs end-to-end in local dev and tests without external accounts. This
directly satisfies "operate without WhatsApp/LLM credentials" requirements.

---

## Security & RBAC
- JWT access (short-lived) + refresh (rotating). Passwords hashed with Argon2.
- Every job-scoped endpoint runs an `authorize(user, job, action)` check against
  `JobMember` + role. Non-members → 403.
- Accept/Reject restricted to the job's client; job create/delete restricted to ID.
- Files only via time-limited pre-signed URLs; buckets are private.
- Secrets via environment/config; `.env.example` documents required keys.
- `AuditLog` written for every state-changing action.

---

## Error Handling
- Centralized FastAPI exception handlers → structured JSON `{error, code, detail}`; no stack traces leak to clients.
- Integration calls (LLM/WhatsApp/Google/push) run in workers with retry + backoff; terminal failures recorded and surfaced.
- Uploads: client requests pre-signed URL, uploads directly to storage, then confirms; failed confirmations are retryable without data loss.
- Optimistic concurrency / explicit allowed state transitions for defect & rectification status to prevent illegal jumps.

---

## Testing Strategy
- **Unit**: service-layer rules — RBAC checks, defect/rectification state machine, AI draft lifecycle (never auto-sends).
- **Integration**: FastAPI + ephemeral Postgres (testcontainers or docker-compose) for auth, jobs, documents, defects, accept/reject, visits, photos.
- **Adapter mocks**: verify app works with all integrations in mock mode.
- **Webhook**: WhatsApp verification + inbound message handling.
- **Flutter**: widget tests for key flows (login, defect create w/ photo, accept/reject, AI review inbox); contract tests against the API schema.
- **CI**: lint (ruff/black, dart analyze) + tests on each push.

---

## Deployment (initial, region-agnostic)
- docker-compose for local dev: `api`, `postgres`, `redis`, `minio`, `worker`.
- Config via environment; `.env.example` enumerates DB, S3, JWT, LLM, WhatsApp, Google keys.
- Alembic migrations run on deploy. Health endpoint for orchestration.
- Region/PDPA residency intentionally deferred; nothing in the design blocks pinning to `ap-southeast-1` later.
