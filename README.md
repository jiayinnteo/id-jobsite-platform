# ID Job-Site Management & Communication Platform

A mobile-first platform for a Singapore interior design (ID) company to manage job
sites and coordinate clearly with clients and contractors — reducing
miscommunication across the renovation lifecycle.

## What it does

- **Four roles:** Interior Designer (ID), Client, Contractor (boss), Worker
- **Shared project artifacts:** quotations (Excel/PDF), 2D & 3D drawings, work schedules
- **Defect tracking** with photos, and an explicit client **Accept / Reject** step on rectification work
- **Site photo capture** for all parties
- **Contractor scheduling:** dispatch workers with date & time
- **In-app chat** (first-class, realtime) plus **WhatsApp** messaging
- **Agentic AI assistant** with **human-in-the-loop** — drafts replies the ID approves before sending (never auto-sends)
- **Bidirectional Google Calendar** sync

## Tech stack

| Layer | Choice |
|-------|--------|
| Frontend | Flutter (iOS + Android) |
| Backend | Python + FastAPI |
| Database | PostgreSQL |
| Storage | S3-compatible (MinIO dev / S3 prod) |
| Async | arq + Redis |
| Realtime | WebSocket + Redis pub/sub |
| AI | Provider-agnostic LLM API |
| Messaging | WhatsApp Business Cloud API |
| Calendar | Google Calendar OAuth |

## Documentation

- **Spec** — [`.kiro/specs/id-jobsite-platform/`](.kiro/specs/id-jobsite-platform/)
  - [`requirements.md`](.kiro/specs/id-jobsite-platform/requirements.md) — 13 requirements (EARS format)
  - [`design.md`](.kiro/specs/id-jobsite-platform/design.md) — architecture, data model, APIs
  - [`tasks.md`](.kiro/specs/id-jobsite-platform/tasks.md) — phased implementation plan
- **Diagrams** — [`docs/diagrams.md`](docs/diagrams.md) — 6 Mermaid diagrams (architecture, workflow, state machine, AI HITL, ERD, screen map)

## Status

📐 **Design phase** — spec and diagrams complete, awaiting sign-off before implementation. Build is phased: MVP (auth → jobs → documents → defects + accept/reject + photos) first, then integrations.
