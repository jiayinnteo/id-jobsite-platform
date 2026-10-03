"""Document & version management with pre-signed uploads/downloads."""

from __future__ import annotations

import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.adapters.storage import get_storage
from app.core.config import get_settings
from app.core.errors import AppError, ForbiddenError, NotFoundError
from app.models.document import Document, DocumentType, DocumentVersion
from app.models.user import User, UserRole
from app.schemas.document import (
    QUOTATION_MIMES,
    DocumentCreate,
    UploadTarget,
    VersionCreate,
)
from app.services.common import (
    authorize_job_access,
    get_job_or_404,
    member_user_ids,
    notify,
    write_audit,
)

settings = get_settings()


def _validate_upload(doc_type: DocumentType, mime_type: str, size_bytes: int) -> None:
    max_bytes = settings.max_upload_size_mb * 1024 * 1024
    if size_bytes > max_bytes:
        raise AppError(
            f"File exceeds the {settings.max_upload_size_mb} MB limit.",
            code="file_too_large",
        )
    if doc_type == DocumentType.QUOTATION and mime_type not in QUOTATION_MIMES:
        raise AppError(
            "Quotations must be a PDF or Excel file.", code="unsupported_type"
        )


async def create_document(
    db: AsyncSession, user: User, job_id: uuid.UUID, data: DocumentCreate
) -> UploadTarget:
    job = await get_job_or_404(db, job_id)
    if user.role not in (UserRole.ID, UserRole.ID_BOSS):
        raise ForbiddenError("Only the ID firm can upload documents.", code="id_only")
    await authorize_job_access(db, user, job)
    _validate_upload(data.type, data.mime_type, data.size_bytes)

    storage = get_storage()
    key = storage.generate_key(f"jobs/{job_id}/documents", data.filename)

    doc = Document(
        job_id=job_id, type=data.type, title=data.title,
        created_by=user.id, current_version_no=1,
    )
    db.add(doc)
    await db.flush()
    db.add(
        DocumentVersion(
            document_id=doc.id, version_no=1, storage_key=key,
            mime_type=data.mime_type, size_bytes=data.size_bytes, uploaded_by=user.id,
        )
    )
    await notify(
        db, await member_user_ids(db, job), type="document.new",
        title=f"New {data.type.value.replace('_', ' ').title()}: {data.title}",
        deep_link=f"/jobs/{job_id}/documents/{doc.id}",
    )
    await write_audit(
        db, actor_id=user.id, action="document.create", target_type="document",
        target_id=str(doc.id), job_id=job_id, metadata={"type": data.type.value},
    )
    await db.commit()
    await db.refresh(doc)
    return UploadTarget(
        document_id=doc.id, version_no=1, storage_key=key,
        upload_url=storage.presigned_put_url(key, data.mime_type),
    )


async def add_version(
    db: AsyncSession, user: User, document_id: uuid.UUID, data: VersionCreate
) -> UploadTarget:
    doc = await db.get(Document, document_id)
    if not doc:
        raise NotFoundError("Document not found.", code="document_not_found")
    job = await get_job_or_404(db, doc.job_id)
    if user.role not in (UserRole.ID, UserRole.ID_BOSS):
        raise ForbiddenError("Only the ID firm can upload documents.", code="id_only")
    await authorize_job_access(db, user, job)
    _validate_upload(doc.type, data.mime_type, data.size_bytes)

    storage = get_storage()
    key = storage.generate_key(f"jobs/{doc.job_id}/documents", data.filename)
    next_no = doc.current_version_no + 1

    db.add(
        DocumentVersion(
            document_id=doc.id, version_no=next_no, storage_key=key,
            mime_type=data.mime_type, size_bytes=data.size_bytes, uploaded_by=user.id,
        )
    )
    doc.current_version_no = next_no  # previous versions retained
    await write_audit(
        db, actor_id=user.id, action="document.add_version", target_type="document",
        target_id=str(doc.id), job_id=doc.job_id, metadata={"version": next_no},
    )
    await db.commit()
    return UploadTarget(
        document_id=doc.id, version_no=next_no, storage_key=key,
        upload_url=storage.presigned_put_url(key, data.mime_type),
    )


async def list_documents(
    db: AsyncSession, user: User, job_id: uuid.UUID
) -> list[Document]:
    job = await get_job_or_404(db, job_id)
    await authorize_job_access(db, user, job)
    rows = await db.scalars(select(Document).where(Document.job_id == job_id))
    return list(rows.all())


async def download_url(db: AsyncSession, user: User, document_id: uuid.UUID) -> str:
    doc = await db.get(Document, document_id)
    if not doc:
        raise NotFoundError("Document not found.", code="document_not_found")
    job = await get_job_or_404(db, doc.job_id)
    await authorize_job_access(db, user, job)

    version = await db.scalar(
        select(DocumentVersion)
        .where(DocumentVersion.document_id == doc.id)
        .order_by(DocumentVersion.version_no.desc())
    )
    if not version:
        raise NotFoundError("No file uploaded for this document.", code="no_version")
    return get_storage().presigned_get_url(version.storage_key)
