"""Schemas for materials, suppliers and selections."""

import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from app.models.material import Country, MaterialCategory, SelectionStatus


class SupplierOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    key: str
    name: str
    country: Country
    website_url: str | None


class ProductOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    supplier_id: uuid.UUID
    category: MaterialCategory
    name: str
    product_code: str | None
    colour: str | None
    colour_hex: str | None
    finish: str | None
    swatch_url: str | None
    source_url: str | None


class SelectionCreate(BaseModel):
    product_id: uuid.UUID | None = None
    category: MaterialCategory
    area: str | None = Field(default=None, max_length=160)
    model_surface: str | None = Field(default=None, max_length=160)
    colour: str | None = Field(default=None, max_length=120)
    colour_hex: str | None = Field(default=None, max_length=9)
    note: str | None = Field(default=None, max_length=2000)


class SurfaceMapUpdate(BaseModel):
    """Map a selection to a named surface/material in the 3D model."""

    model_surface: str = Field(min_length=1, max_length=160)


class PreviewMaterial(BaseModel):
    """A surface→colour mapping the 3D viewer applies to the model."""

    selection_id: uuid.UUID
    model_surface: str
    colour_hex: str | None
    colour: str | None
    category: MaterialCategory
    status: SelectionStatus


class SelectionDecision(BaseModel):
    approve: bool
    note: str | None = Field(default=None, max_length=2000)


class SelectionOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    job_id: uuid.UUID
    product_id: uuid.UUID | None
    category: MaterialCategory
    area: str | None
    model_surface: str | None
    colour: str | None
    colour_hex: str | None
    note: str | None
    status: SelectionStatus
    selected_by: uuid.UUID
    created_at: datetime
