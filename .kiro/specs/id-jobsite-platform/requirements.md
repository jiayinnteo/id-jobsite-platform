# Requirements — ID Job-Site Management & Communication Platform

## Introduction

This document defines the requirements for a job-site management and communication
platform for a Singapore-based interior design (ID) company. The platform helps
interior designers manage job sites and coordinate clearly with both clients and
contractors, reducing miscommunication across the renovation lifecycle.

The system serves four roles — **Interior Designer (ID)**, **Client**,
**Contractor (company boss)**, and **Worker** — and provides shared project
artifacts (quotations, 2D/3D drawings, schedules), a defect tracking and
rectification workflow with explicit client accept/reject, site-photo capture for
all parties, bidirectional Google Calendar sync, a first-class in-app chat, and an
agentic-AI assistant with a human-in-the-loop approval step that can reply in-app
or over WhatsApp.

### Technology Direction (agreed)
- **Frontend:** Flutter (iOS + Android, mobile-first, native camera capture)
- **Backend:** Python + FastAPI
- **Database:** PostgreSQL
- **File storage:** S3-compatible object storage
- **AI:** LLM via API, provider-agnostic/pluggable
- **Messaging:** WhatsApp Business Cloud API (pluggable; credentials wired later)
- **Calendar:** Google Calendar OAuth (bidirectional)
- Region/PDPA residency: not required for the initial build; design to allow it later.

---

## Glossary
- **ID**: Interior Designer — primary operator of the platform.
- **Job / Project**: A renovation engagement for one client at one site.
- **Defect**: An issue raised against a job that needs rectification.
- **Rectification job**: Work scheduled to fix one or more defects.
- **Accept/Reject**: Client's explicit decision on a completed rectification.
- **HITL**: Human-in-the-loop — a human approves AI-drafted messages before sending.

---

## Requirements

### Requirement 1 — Authentication & Role-Based Access
**User Story:** As a user of any type, I want to sign in securely and only see what
my role permits, so that project data stays confidential and relevant.

#### Acceptance Criteria
1. WHEN a new user registers THEN the system SHALL create an account with exactly one of the roles: ID, Client, Contractor, Worker.
2. WHEN a user authenticates with valid credentials THEN the system SHALL issue a time-limited access token and a refresh token.
3. IF a user presents an expired access token WHEN calling an API THEN the system SHALL reject the request with HTTP 401.
4. WHEN a user accesses a resource THEN the system SHALL authorize the request against the user's role and their membership in the related job.
5. IF a user is not a member of a job WHEN they request that job's data THEN the system SHALL respond with HTTP 403.
6. WHEN a user requests a password reset THEN the system SHALL send a time-limited reset link to their verified email.

### Requirement 2 — Job / Project Management
**User Story:** As an ID, I want to create and manage job sites and the people on
them, so that each project's data and communication stay organized.

#### Acceptance Criteria
1. WHEN an ID creates a job THEN the system SHALL record a site name, address, client, and status (e.g. Draft, Active, On Hold, Completed).
2. WHEN an ID adds a participant to a job THEN the system SHALL link a Client, Contractor, or Worker to that job with the appropriate role.
3. WHEN a job participant opens the app THEN the system SHALL list only the jobs they are a member of.
4. WHEN an ID updates a job's status THEN the system SHALL persist the change and make it visible to all job members.
5. WHERE a user is not an ID THE SYSTEM SHALL NOT allow creating or deleting jobs.

### Requirement 3 — Document & Drawing Management (Quotations, 2D, 3D, Schedules)
**User Story:** As an ID, I want to upload quotations, 2D/3D drawings, and work
schedules, so that clients can review everything in one place.

#### Acceptance Criteria
1. WHEN an ID uploads a quotation THEN the system SHALL accept Excel (.xlsx) and PDF (.pdf) files and store them in object storage.
2. WHEN an ID uploads a 2D or 3D drawing THEN the system SHALL store the file and record its type (2D/3D), version, and upload timestamp.
3. WHEN a client opens a job THEN the system SHALL let them view/download the quotation, 2D drawings, 3D drawings, and work schedule for that job.
4. WHEN a new version of a document is uploaded THEN the system SHALL retain previous versions and mark the latest as current.
5. IF an uploaded file exceeds the configured size limit OR has an unsupported type THEN the system SHALL reject it with a clear error.
6. WHEN any document is requested for download THEN the system SHALL serve it via a time-limited pre-signed URL.

### Requirement 4 — Defect Reporting & Tracking
**User Story:** As a client, I want to report defects with photos, so that the ID
and contractor can track and fix them.

#### Acceptance Criteria
1. WHEN a client creates a defect THEN the system SHALL record a title, description, location/room, one or more photos, and an initial status of "Open".
2. WHEN a defect is created THEN the system SHALL notify the job's ID.
3. WHEN an ID assigns a defect to a contractor THEN the system SHALL update the defect's assignee and status to "Assigned".
4. WHEN the status of a defect changes THEN the system SHALL record who changed it and when, and notify affected members.
5. WHERE a defect progresses THE SYSTEM SHALL support the states: Open → Assigned → In Progress → Rectified → (Accepted | Rejected) → Closed.
6. WHEN a job member views a defect THEN the system SHALL show its full status history and all attached photos.

### Requirement 5 — Rectification Accept/Reject (Client Decision)
**User Story:** As a client, I want to tap Accept or Reject on completed
rectification work, so that approval is explicit and the ID is informed immediately.

#### Acceptance Criteria
1. WHEN a contractor marks rectification work as "Rectified" THEN the system SHALL present the client with Accept and Reject actions for that work.
2. WHEN a client taps Accept THEN the system SHALL set the status to "Accepted" and notify the ID.
3. WHEN a client taps Reject THEN the system SHALL require a reason, set the status to "Rejected", and notify the ID and contractor.
4. WHEN an accept/reject decision is made THEN the system SHALL record the decision, the deciding client, a timestamp, and any reason.
5. IF a user who is not the job's client attempts to accept/reject THEN the system SHALL respond with HTTP 403.

### Requirement 6 — Contractor Work Scheduling
**User Story:** As a contractor boss, I want to see the rectification work assigned
to me and schedule my workers' site visits, so that work starts promptly.

#### Acceptance Criteria
1. WHEN a contractor opens the app THEN the system SHALL list all rectification work assigned to their company across their jobs.
2. WHEN a contractor schedules a site visit THEN the system SHALL record the assigned worker(s), date, time, and the related defect/rectification.
3. WHEN a site visit is scheduled THEN the system SHALL notify the ID and client and reflect it on the job schedule.
4. WHEN a contractor updates or cancels a scheduled visit THEN the system SHALL update the schedule and notify affected members.
5. WHERE a worker is assigned to a visit THE SYSTEM SHALL make that visit visible to the assigned worker.

### Requirement 7 — Site Photo Capture & Sharing (All Roles)
**User Story:** As any job member, I want to take and upload photos of the work, so
that everyone involved can see the current state of the site.

#### Acceptance Criteria
1. WHEN any job member captures or selects a photo THEN the system SHALL upload it to object storage and attach it to the job (optionally to a specific defect or work item).
2. WHEN a photo is uploaded THEN the system SHALL record the uploader, timestamp, and optional caption/location.
3. WHEN a job member opens the job gallery THEN the system SHALL display all photos they are permitted to see, newest first.
4. WHERE a photo is attached to a defect THE SYSTEM SHALL also show it within that defect's detail view.
5. WHEN a photo upload fails THEN the system SHALL report the failure and allow retry without data loss.

### Requirement 8 — Notifications
**User Story:** As a user, I want timely notifications about things that concern me,
so that I can respond quickly.

#### Acceptance Criteria
1. WHEN a notifiable event occurs (defect created, status change, accept/reject, visit scheduled, new document) THEN the system SHALL create an in-app notification for each affected member.
2. WHEN a user has an unread notification THEN the system SHALL indicate the unread count in the app.
3. WHEN a user opens a notification THEN the system SHALL mark it read and deep-link to the relevant item.
4. WHERE push notifications are configured THE SYSTEM SHALL also deliver the notification to the user's device.

### Requirement 9 — Google Calendar Integration (Bidirectional)
**User Story:** As any user, I want work schedules synced with my Google Calendar,
so that site visits and milestones appear in my own calendar and vice versa.

#### Acceptance Criteria
1. WHEN a user connects their Google account THEN the system SHALL complete OAuth and store the user's calendar tokens securely.
2. WHEN a schedule item is created or updated in the app THEN the system SHALL create/update the corresponding Google Calendar event for linked users.
3. WHEN a linked Google Calendar event is changed externally THEN the system SHALL reflect the change on the app's schedule.
4. IF a user disconnects Google Calendar THEN the system SHALL stop syncing and revoke stored tokens.
5. IF a calendar sync operation fails THEN the system SHALL retry with backoff and surface a persistent error if it continues to fail.

### Requirement 10 — Agentic AI Assistant with Human-in-the-Loop
**User Story:** As an ID, I want an AI assistant to draft natural replies to client
and contractor messages that I review before sending, so communication is fast but
never sounds unnatural or goes out unapproved.

#### Acceptance Criteria
1. WHEN an inbound message needs a reply THEN the system SHALL generate a draft reply using the configured LLM provider.
2. WHEN a draft reply is generated THEN the system SHALL place it in an approval queue in a "Pending Review" state and SHALL NOT send it automatically.
3. WHEN an ID edits a draft THEN the system SHALL save the edited version as the content to be sent.
4. WHEN an ID approves a draft THEN the system SHALL send the message and record who approved it and when.
5. WHEN an ID rejects a draft THEN the system SHALL discard it (optionally regenerate) and send nothing.
6. WHERE the LLM provider is configured THE SYSTEM SHALL use a provider-agnostic interface so the provider can be swapped without changing callers.
7. WHILE drafting THE SYSTEM SHALL include relevant job context (recent messages, defect/schedule state) so drafts are accurate.

### Requirement 11 — In-App Chat (First-Class)
**User Story:** As a job member, I want to chat with other members of my job inside
the app, so that all project communication has a shared, searchable home even when
WhatsApp is not used.

#### Acceptance Criteria
1. WHEN a job is created THEN the system SHALL create an in-app conversation for that job.
2. WHEN a job member sends a chat message THEN the system SHALL persist it, deliver it in real time to online members, and notify offline members.
3. WHEN a member opens a conversation THEN the system SHALL show the message history newest-at-bottom and mark messages as read for that member.
4. WHEN a member attaches a photo or document reference to a chat message THEN the system SHALL render it inline within the conversation.
5. WHERE a message pertains to a defect, rectification, or schedule item THE SYSTEM SHALL allow linking it so members can deep-link to that item.
6. IF a user is not a member of the job THEN the system SHALL NOT allow them to read or post in that conversation (HTTP 403).
7. WHERE the AI assistant is enabled THE SYSTEM SHALL be able to draft a reply for a chat message that follows the same human-in-the-loop approval before sending.

### Requirement 12 — WhatsApp Messaging Integration
**User Story:** As an ID, I want client/contractor conversations to flow over
WhatsApp with AI-assisted, human-approved replies, so clients communicate on a
channel they already use.

#### Acceptance Criteria
1. WHEN an inbound WhatsApp message arrives at the webhook THEN the system SHALL record it against the matching job conversation.
2. WHEN an approved reply is sent THEN the system SHALL deliver it via the WhatsApp Business Cloud API to the correct recipient.
3. WHERE WhatsApp credentials are not configured THE SYSTEM SHALL operate in a disabled/mock mode without breaking other features.
4. IF a WhatsApp API call fails THEN the system SHALL record the failure and allow retry.
5. WHEN the webhook receives a verification challenge THEN the system SHALL respond per the WhatsApp verification protocol.

### Requirement 13 — Audit, Reliability & Non-Functional
**User Story:** As the business owner, I want the platform to be secure, reliable,
and auditable, so I can trust it with client projects.

#### Acceptance Criteria
1. WHEN any state-changing action occurs on a job THEN the system SHALL append an immutable audit entry (actor, action, target, timestamp).
2. WHERE secrets (DB, S3, LLM, WhatsApp, Google) are used THE SYSTEM SHALL load them from configuration/environment and never hard-code them.
3. WHEN the API receives invalid input THEN the system SHALL validate it and return a structured error without a stack trace.
4. WHERE object storage is used THE SYSTEM SHALL only expose files via time-limited pre-signed URLs, never public buckets.
5. THE SYSTEM SHALL expose a health-check endpoint for liveness/readiness.
