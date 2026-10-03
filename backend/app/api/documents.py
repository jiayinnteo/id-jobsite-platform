"""Document endpoints."""

import uuid

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user
from app.db.base import get_db
from app.models.user import User
from app.schemas.document import (
    DocumentCreate,
    DocumentOut,
    DownloadUrl,
    UploadTarget,
    VersionCreate,
)
from app.services import document_service

job_docs_router = APIRouter(prefix="/jobs", tags=["documents"])
docs_router = APIRouter(prefix="/documents", tags=["documents"])


@job_docs_router.post(
    "/{job_id}/documents", response_model=UploadTarget, status_code=status.HTTP_201_CREATED
)
async def create_document(
    job_id: uuid.UUID,
    data: DocumentCreate,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    return await document_service.create_document(db, user, job_id, data)


@job_docs_router.get("/{job_id}/documents", response_model=list[DocumentOut])
async def list_documents(
    job_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    return await document_service.list_documents(db, user, job_id)


@docs_router.post(
    "/{document_id}/versions", response_model=UploadTarget, status_code=status.HTTP_201_CREATED
)
async def add_version(
    document_id: uuid.UUID,
    data: VersionCreate,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    return await document_service.add_version(db, user, document_id, data)


@docs_router.get("/{document_id}/download", response_model=DownloadUrl)
async def download(
    document_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    return DownloadUrl(url=await document_service.download_url(db, user, document_id))
