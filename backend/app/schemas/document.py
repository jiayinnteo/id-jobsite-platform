"""Schemas for documents and versions."""

import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from app.models.document import DocumentType

# Allowed mime types per document kind.
QUOTATION_MIMES = {
    "application/pdf",
    "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",  # xlsx
    "application/vnd.ms-excel",
}


class DocumentCreate(BaseModel):
    type: DocumentType
    title: str = Field(min_length=1, max_length=200)
    filename: str = Field(min_length=1, max_length=200)
    mime_type: str
    size_bytes: int = Field(ge=1)


class VersionCreate(BaseModel):
    filename: str = Field(min_length=1, max_length=200)
    mime_type: str
    size_bytes: int = Field(ge=1)


class UploadTarget(BaseModel):
    """Returned to the client: upload the file to `upload_url`, then it's recorded."""

    document_id: uuid.UUID
    version_no: int
    storage_key: str
    upload_url: str


class DocumentVersionOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    version_no: int
    mime_type: str
    size_bytes: int
    uploaded_by: uuid.UUID
    created_at: datetime


class DocumentOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    job_id: uuid.UUID
    type: DocumentType
    title: str
    current_version_no: int
    created_at: datetime


class DownloadUrl(BaseModel):
    url: str
