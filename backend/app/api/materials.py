"""Materials, suppliers and selection endpoints."""

import uuid

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user, require_roles
from app.db.base import get_db
from app.models.material import MaterialCategory
from app.models.user import User, UserRole
from app.schemas.material import (
    PreviewMaterial,
    ProductOut,
    SelectionCreate,
    SelectionDecision,
    SelectionOut,
    SupplierOut,
    SurfaceMapUpdate,
)
from app.services import material_service

suppliers_router = APIRouter(prefix="/materials", tags=["materials"])
job_materials_router = APIRouter(prefix="/jobs", tags=["materials"])
selections_router = APIRouter(prefix="/material-selections", tags=["materials"])


@suppliers_router.post("/sync", status_code=status.HTTP_202_ACCEPTED)
async def sync_catalogues(
    db: AsyncSession = Depends(get_db),
    user: User = Depends(require_roles(UserRole.ID, UserRole.ID_BOSS)),
):
    added = await material_service.sync_suppliers(db)
    return {"synced": True, "new_products": added}


@suppliers_router.get("/suppliers", response_model=list[SupplierOut])
async def list_suppliers(
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    return await material_service.list_suppliers(db)


@suppliers_router.get("/products", response_model=list[ProductOut])
async def list_products(
    category: MaterialCategory | None = None,
    supplier_id: uuid.UUID | None = None,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    return await material_service.list_products(
        db, category=category, supplier_id=supplier_id
    )


@job_materials_router.get("/{job_id}/materials", response_model=list[SelectionOut])
async def list_selections(
    job_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    return await material_service.list_selections(db, user, job_id)


@job_materials_router.post(
    "/{job_id}/materials", response_model=SelectionOut, status_code=status.HTTP_201_CREATED
)
async def create_selection(
    job_id: uuid.UUID,
    data: SelectionCreate,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    return await material_service.create_selection(db, user, job_id, data)


@selections_router.post("/{selection_id}/decision", response_model=SelectionOut)
async def decide_selection(
    selection_id: uuid.UUID,
    data: SelectionDecision,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    return await material_service.decide_selection(db, user, selection_id, data)


@selections_router.patch("/{selection_id}/surface", response_model=SelectionOut)
async def map_surface(
    selection_id: uuid.UUID,
    data: SurfaceMapUpdate,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    return await material_service.map_surface(
        db, user, selection_id, data.model_surface
    )


@job_materials_router.get(
    "/{job_id}/materials/preview", response_model=list[PreviewMaterial]
)
async def preview_materials(
    job_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    selections = await material_service.preview_materials(db, user, job_id)
    return [
        PreviewMaterial(
            selection_id=s.id,
            model_surface=s.model_surface,
            colour_hex=s.colour_hex,
            colour=s.colour,
            swatch_url=s.swatch_url,
            category=s.category,
            status=s.status,
        )
        for s in selections
    ]
