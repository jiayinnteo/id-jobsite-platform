"""Materials: supplier catalogue sync, product listing, and job selections."""

from __future__ import annotations

import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.adapters.suppliers import all_suppliers
from app.core.errors import ForbiddenError, NotFoundError
from app.models.material import (
    MaterialCategory,
    MaterialProduct,
    MaterialSelection,
    MaterialSupplier,
    SelectionStatus,
)
from app.models.user import User, UserRole
from app.schemas.material import SelectionCreate, SelectionDecision
from app.services.common import (
    authorize_job_access,
    get_job_or_404,
    notify,
    write_audit,
)


async def sync_suppliers(db: AsyncSession) -> int:
    """Idempotently load supplier catalogues into the DB. Safe to re-run."""
    count = 0
    for supplier in all_suppliers():
        info = supplier.info
        row = await db.scalar(select(MaterialSupplier).where(MaterialSupplier.key == info.key))
        if not row:
            row = MaterialSupplier(
                key=info.key,
                name=info.name,
                country=info.country,
                website_url=info.website_url,
            )
            db.add(row)
            await db.flush()

        items = await supplier.fetch_catalogue()
        for item in items:
            exists = await db.scalar(
                select(MaterialProduct).where(
                    MaterialProduct.supplier_id == row.id,
                    MaterialProduct.name == item.name,
                    MaterialProduct.product_code == item.product_code,
                )
            )
            if exists:
                continue
            db.add(
                MaterialProduct(
                    supplier_id=row.id,
                    category=item.category,
                    name=item.name,
                    product_code=item.product_code,
                    colour=item.colour,
                    colour_hex=item.colour_hex,
                    finish=item.finish,
                    swatch_url=item.swatch_url,
                    source_url=item.source_url,
                )
            )
            count += 1
    await db.commit()
    return count


async def list_suppliers(db: AsyncSession) -> list[MaterialSupplier]:
    rows = await db.scalars(select(MaterialSupplier).order_by(MaterialSupplier.name))
    return list(rows.all())


async def list_products(
    db: AsyncSession,
    *,
    category: MaterialCategory | None = None,
    supplier_id: uuid.UUID | None = None,
) -> list[MaterialProduct]:
    stmt = select(MaterialProduct)
    if category:
        stmt = stmt.where(MaterialProduct.category == category)
    if supplier_id:
        stmt = stmt.where(MaterialProduct.supplier_id == supplier_id)
    rows = await db.scalars(stmt.order_by(MaterialProduct.name))
    return list(rows.all())


async def list_selections(
    db: AsyncSession, user: User, job_id: uuid.UUID
) -> list[MaterialSelection]:
    job = await get_job_or_404(db, job_id)
    await authorize_job_access(db, user, job)
    rows = await db.scalars(
        select(MaterialSelection)
        .where(MaterialSelection.job_id == job_id)
        .order_by(MaterialSelection.created_at.desc())
    )
    return list(rows.all())


async def create_selection(
    db: AsyncSession, user: User, job_id: uuid.UUID, data: SelectionCreate
) -> MaterialSelection:
    job = await get_job_or_404(db, job_id)
    if user.role not in (UserRole.ID, UserRole.ID_BOSS):
        raise ForbiddenError("Only the ID firm can select materials.", code="id_only")
    await authorize_job_access(db, user, job)

    colour = data.colour
    colour_hex = data.colour_hex
    swatch_url = None
    # If a catalogue product is chosen, default colour + texture from it.
    if data.product_id:
        product = await db.get(MaterialProduct, data.product_id)
        if product:
            colour = colour or product.colour
            colour_hex = colour_hex or product.colour_hex
            swatch_url = product.swatch_url

    selection = MaterialSelection(
        job_id=job_id,
        product_id=data.product_id,
        category=data.category,
        area=data.area,
        model_surface=data.model_surface,
        swatch_url=swatch_url,
        colour=colour,
        colour_hex=colour_hex,
        note=data.note,
        status=SelectionStatus.PROPOSED,
        selected_by=user.id,
    )
    db.add(selection)
    # Notify the client to review the proposed finish.
    if job.client_id:
        await notify(
            db,
            [job.client_id],
            type="material.proposed",
            title=f"New material to review: {data.category.value.title()}",
            body=data.area,
            deep_link=f"/jobs/{job_id}/materials",
        )
    await write_audit(
        db,
        actor_id=user.id,
        action="material.select",
        target_type="material_selection",
        target_id=str(selection.id),
        job_id=job_id,
        metadata={"category": data.category.value},
    )
    await db.commit()
    await db.refresh(selection)
    return selection


async def decide_selection(
    db: AsyncSession, client: User, selection_id: uuid.UUID, data: SelectionDecision
) -> MaterialSelection:
    selection = await db.get(MaterialSelection, selection_id)
    if not selection:
        raise NotFoundError("Selection not found.", code="selection_not_found")
    job = await get_job_or_404(db, selection.job_id)
    if client.id != job.client_id:
        raise ForbiddenError("Only the job's client can approve materials.", code="client_only")

    selection.status = (
        SelectionStatus.APPROVED if data.approve else SelectionStatus.CHANGE_REQUESTED
    )
    if data.note:
        selection.note = data.note
    await notify(
        db,
        [job.created_by],
        type="material.decision",
        title=f"Client {'approved' if data.approve else 'requested a change to'} a material",
        body=data.note,
        deep_link=f"/jobs/{job.id}/materials",
    )
    await write_audit(
        db,
        actor_id=client.id,
        action="material.decision",
        target_type="material_selection",
        target_id=str(selection.id),
        job_id=job.id,
        metadata={"approved": data.approve},
    )
    await db.commit()
    await db.refresh(selection)
    return selection


async def map_surface(
    db: AsyncSession, user: User, selection_id: uuid.UUID, model_surface: str
) -> MaterialSelection:
    """Map a selection to a named surface/material in the job's 3D model."""
    selection = await db.get(MaterialSelection, selection_id)
    if not selection:
        raise NotFoundError("Selection not found.", code="selection_not_found")
    job = await get_job_or_404(db, selection.job_id)
    if user.role not in (UserRole.ID, UserRole.ID_BOSS):
        raise ForbiddenError("Only the ID firm can map model surfaces.", code="id_only")
    await authorize_job_access(db, user, job)

    selection.model_surface = model_surface
    await write_audit(
        db,
        actor_id=user.id,
        action="material.map_surface",
        target_type="material_selection",
        target_id=str(selection.id),
        job_id=job.id,
        metadata={"surface": model_surface},
    )
    await db.commit()
    await db.refresh(selection)
    return selection


async def preview_materials(
    db: AsyncSession, user: User, job_id: uuid.UUID
) -> list[MaterialSelection]:
    """Selections that are mapped to a model surface, for the 3D preview.

    Latest selection per surface wins, so re-proposing a finish updates the view.
    """
    job = await get_job_or_404(db, job_id)
    await authorize_job_access(db, user, job)
    rows = await db.scalars(
        select(MaterialSelection)
        .where(
            MaterialSelection.job_id == job_id,
            MaterialSelection.model_surface.is_not(None),
        )
        .order_by(MaterialSelection.created_at.desc())
    )
    seen: set[str] = set()
    result: list[MaterialSelection] = []
    for sel in rows.all():
        if sel.model_surface in seen:
            continue
        seen.add(sel.model_surface)
        result.append(sel)
    return result
