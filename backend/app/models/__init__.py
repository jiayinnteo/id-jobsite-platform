"""ORM models. Importing this package registers all models on Base.metadata."""

from app.models.chat import (  # noqa: F401
    AIDraft,
    Channel,
    Conversation,
    DraftStatus,
    Message,
    MessageDirection,
    MessageRead,
)
from app.models.defect import (  # noqa: F401
    ALLOWED_TRANSITIONS,
    Defect,
    DefectStatus,
    DefectStatusHistory,
    Photo,
    Rectification,
    RectificationDecision,
)
from app.models.document import (  # noqa: F401
    Document,
    DocumentType,
    DocumentVersion,
)
from app.models.job import (  # noqa: F401
    Job,
    JobMember,
    JobReview,
    JobStatus,
    OversightFlag,
    OversightReview,
)
from app.models.material import (  # noqa: F401
    Country,
    MaterialCategory,
    MaterialProduct,
    MaterialSelection,
    MaterialSupplier,
    SelectionStatus,
)
from app.models.schedule import (  # noqa: F401
    CalendarEventLink,
    CalendarLink,
    SiteVisit,
    VisitStatus,
    VisitWorker,
)
from app.models.system import AuditLog, Notification  # noqa: F401
from app.models.user import Company, CompanyType, User, UserRole  # noqa: F401

__all__ = [
    "User",
    "Company",
    "CompanyType",
    "UserRole",
    "Job",
    "JobMember",
    "JobStatus",
    "OversightReview",
    "OversightFlag",
    "JobReview",
    "Document",
    "DocumentType",
    "DocumentVersion",
    "Defect",
    "DefectStatus",
    "DefectStatusHistory",
    "ALLOWED_TRANSITIONS",
    "Rectification",
    "RectificationDecision",
    "Photo",
    "Notification",
    "AuditLog",
    "SiteVisit",
    "VisitStatus",
    "VisitWorker",
    "CalendarLink",
    "CalendarEventLink",
    "Conversation",
    "Message",
    "MessageRead",
    "Channel",
    "MessageDirection",
    "AIDraft",
    "DraftStatus",
    "MaterialSupplier",
    "MaterialProduct",
    "MaterialSelection",
    "MaterialCategory",
    "Country",
    "SelectionStatus",
]
