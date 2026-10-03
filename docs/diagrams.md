# ID Job-Site Platform — Visual Workflow & App Design

Diagrams are written in **Mermaid**. They render automatically on GitHub and in any
Mermaid-capable viewer. A rendered PNG/SVG export is also saved alongside this file
(`architecture.svg`, `workflow.svg`) once generated.

---

## 1. System Architecture

```mermaid
flowchart TB
    subgraph Client["📱 Flutter App (iOS / Android)"]
        UI_Auth["Auth"]
        UI_Jobs["Jobs & Documents"]
        UI_Def["Defects + Accept/Reject"]
        UI_Photo["Site Photos (camera)"]
        UI_Sched["Schedule"]
        UI_Chat["In-App Chat"]
        UI_AI["AI Review Inbox"]
        UI_Notif["Notifications"]
    end

    subgraph API["⚙️ FastAPI Backend"]
        Routers["API Routers (REST + WebSocket)"]
        Auth["Auth / JWT + RBAC"]
        Services["Service Layer<br/>Jobs · Docs · Defects · Rectify ·<br/>Scheduling · Photos · Chat · Notify · AI"]
        Ports["Integration Ports (mockable)<br/>Storage · LLM · WhatsApp · Calendar · Push"]
        Repos["Repositories (SQLAlchemy)"]
    end

    subgraph Workers["🔄 arq Background Workers"]
        W1["Calendar Sync"]
        W2["WhatsApp Send"]
        W3["AI Drafting"]
        W4["Push Delivery"]
    end

    subgraph Infra["🗄️ Infrastructure"]
        PG[("PostgreSQL")]
        S3[("S3 / MinIO<br/>drawings · PDFs · photos")]
        Redis[("Redis<br/>queue + chat pub/sub")]
    end

    subgraph Ext["🌐 External Services"]
        LLM["LLM Provider API"]
        WA["WhatsApp Cloud API"]
        GCal["Google Calendar API"]
        FCM["FCM / APNs"]
    end

    Client -- "HTTPS REST" --> Routers
    Client -- "WebSocket (chat)" --> Routers
    FCM -- "Push" --> Client

    Routers --> Auth --> Services --> Repos --> PG
    Services --> Ports
    Services -- "enqueue jobs" --> Redis
    Redis --> Workers

    Ports --> S3
    W3 --> LLM
    W2 --> WA
    W1 --> GCal
    W4 --> FCM
    Routers <-- "pub/sub" --> Redis
```

---

## 2. End-to-End Workflow (renovation lifecycle)

```mermaid
flowchart TD
    Start([ID creates Job]) --> AddMembers[Add Client, Contractor, Workers]
    AddMembers --> Upload[ID uploads Quotation / 2D / 3D / Schedule]
    Upload --> ClientReview{Client reviews<br/>in app}
    ClientReview -->|questions| Chat[In-App Chat / WhatsApp]
    Chat --> AI[AI drafts reply → ID approves → sent]
    AI --> ClientReview

    ClientReview --> Work[Renovation work proceeds]
    Work --> Photos[All parties upload site photos]

    Photos --> Defect{Client finds<br/>a defect?}
    Defect -->|yes| RaiseDefect[Client raises defect + photos]
    RaiseDefect --> NotifyID[ID notified]
    NotifyID --> Assign[ID assigns defect to Contractor]
    Assign --> NotifyBoss[Contractor boss notified]
    NotifyBoss --> Schedule[Boss schedules worker: date + time]
    Schedule --> SyncCal[Site visit synced to Google Calendar<br/>+ ID & Client notified]
    SyncCal --> Fix[Worker performs rectification on site]
    Fix --> MarkRectified[Contractor marks RECTIFIED]

    MarkRectified --> Decision{Client taps<br/>Accept / Reject}
    Decision -->|Accept| Accepted[Status: ACCEPTED<br/>ID notified]
    Decision -->|Reject + reason| Rejected[Status: REJECTED<br/>ID + Contractor notified]
    Rejected --> Schedule

    Accepted --> MoreDefects{More defects?}
    Defect -->|no| MoreDefects
    MoreDefects -->|yes| RaiseDefect
    MoreDefects -->|no| Complete([ID marks Job COMPLETED])
```

---

## 3. Defect & Rectification State Machine

```mermaid
stateDiagram-v2
    [*] --> OPEN: Client raises defect
    OPEN --> ASSIGNED: ID assigns contractor
    ASSIGNED --> IN_PROGRESS: Worker starts on site
    IN_PROGRESS --> RECTIFIED: Contractor marks done
    RECTIFIED --> ACCEPTED: Client taps Accept
    RECTIFIED --> REJECTED: Client taps Reject (+reason)
    REJECTED --> ASSIGNED: Re-scheduled for rework
    ACCEPTED --> CLOSED: ID closes
    CLOSED --> [*]
```

---

## 4. Agentic AI — Human-in-the-Loop (never auto-sends)

```mermaid
sequenceDiagram
    participant C as Client/Contractor
    participant WA as WhatsApp / In-App Chat
    participant API as FastAPI
    participant Q as arq Worker
    participant LLM as LLM Provider
    participant ID as Interior Designer

    C->>WA: Sends a message
    WA->>API: Inbound message (webhook / WS)
    API->>API: Store message in conversation
    API->>Q: Enqueue "draft reply"
    Q->>LLM: Prompt + job context
    LLM-->>Q: Draft reply
    Q->>API: Save AIDraft (PENDING_REVIEW)
    API-->>ID: Notify "draft ready for review"
    Note over API,ID: ⛔ Nothing is sent automatically
    ID->>API: Edit / Approve / Reject
    alt Approved
        API->>WA: Send approved message
        WA-->>C: Natural, human-approved reply
        API->>API: Audit (who approved, when)
    else Rejected
        API->>API: Discard (optionally regenerate)
    end
```

---

## 5. Data Model (ERD)

```mermaid
erDiagram
    USER ||--o{ JOBMEMBER : "belongs to"
    JOB  ||--o{ JOBMEMBER : "has"
    USER ||--o{ JOB : "ID creates"
    COMPANY ||--o{ USER : "employs"

    JOB ||--o{ DOCUMENT : "has"
    DOCUMENT ||--o{ DOCUMENTVERSION : "versions"

    JOB ||--o{ DEFECT : "has"
    DEFECT ||--o{ DEFECTSTATUSHISTORY : "tracks"
    DEFECT ||--o{ RECTIFICATION : "fixed by"
    RECTIFICATION ||--o| RECTIFICATIONDECISION : "accept/reject"

    JOB ||--o{ SITEVISIT : "scheduled"
    SITEVISIT ||--o{ VISITWORKER : "assigns"
    USER ||--o{ VISITWORKER : "worker"

    JOB ||--o{ PHOTO : "gallery"
    DEFECT ||--o{ PHOTO : "attached"

    JOB ||--o{ SCHEDULEITEM : "schedule"
    USER ||--o| CALENDARLINK : "google oauth"

    JOB ||--|| CONVERSATION : "in-app chat"
    CONVERSATION ||--o{ MESSAGE : "messages"
    MESSAGE ||--o{ MESSAGEREAD : "read state"
    CONVERSATION ||--o{ AIDRAFT : "ai drafts"

    USER ||--o{ NOTIFICATION : "receives"
    JOB  ||--o{ AUDITLOG : "audited"
```

---

## 6. Flutter App — Screen Map (by role)

```mermaid
flowchart LR
    Login[Login / Register] --> Home{Role?}

    Home -->|ID| ID_Home[ID Dashboard]
    Home -->|Client| CL_Home[Client Dashboard]
    Home -->|Contractor| CO_Home[Contractor Dashboard]
    Home -->|Worker| WK_Home[Worker Dashboard]

    ID_Home --> JobList[Jobs]
    JobList --> JobDetail[Job Detail]
    JobDetail --> Docs[Documents: Quote/2D/3D/Schedule]
    JobDetail --> Defects[Defects]
    JobDetail --> Gallery[Photo Gallery]
    JobDetail --> ScheduleV[Schedule]
    JobDetail --> ChatV[In-App Chat]
    ID_Home --> AIInbox[AI Review Inbox]
    ID_Home --> NotifC[Notifications]

    CL_Home --> CL_Job[Job Detail]
    CL_Job --> CL_View[View Quote/Drawings/Schedule]
    CL_Job --> CL_Defect[Raise Defect + Photo]
    CL_Job --> CL_AR[Accept / Reject Rectification]
    CL_Job --> ChatV

    CO_Home --> CO_Work[Assigned Work Queue]
    CO_Work --> CO_Sched[Schedule Visit: worker + date/time]
    CO_Home --> ChatV

    WK_Home --> WK_Visits[My Site Visits]
    WK_Visits --> WK_Photo[Upload Work Photos]
```
