"""Materials, suppliers and per-job material selections."""

import enum
import uuid

from sqlalchemy import Enum as SAEnum
from sqlalchemy import ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class MaterialCategory(str, enum.Enum):
    LAMINATE = "LAMINATE"
    TILE = "TILE"
    WORKTOP = "WORKTOP"
    PAINT = "PAINT"
    VINYL = "VINYL"
    FLOORING = "FLOORING"
    OTHER = "OTHER"


class Country(str, enum.Enum):
    SG = "SG"
    MY = "MY"


class MaterialSupplier(Base):
    __tablename__ = "material_suppliers"

    key: Mapped[str] = mapped_column(String(60), unique=True, nullable=False)  # e.g. "eco_plus"
    name: Mapped[str] = mapped_column(String(160), nullable=False)
    country: Mapped[Country] = mapped_column(
        SAEnum(Country, name="supplier_country"), nullable=False
    )
    website_url: Mapped[str | None] = mapped_column(String(400), nullable=True)

    products: Mapped[list["MaterialProduct"]] = relationship(back_populates="supplier")


class MaterialProduct(Base):
    __tablename__ = "material_products"

    supplier_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("material_suppliers.id", ondelete="CASCADE"), nullable=False, index=True
    )
    category: Mapped[MaterialCategory] = mapped_column(
        SAEnum(MaterialCategory, name="material_category"), nullable=False, index=True
    )
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    product_code: Mapped[str | None] = mapped_column(String(80), nullable=True)
    colour: Mapped[str | None] = mapped_column(String(120), nullable=True)
    colour_hex: Mapped[str | None] = mapped_column(String(9), nullable=True)  # #RRGGBB
    finish: Mapped[str | None] = mapped_column(String(120), nullable=True)
    swatch_url: Mapped[str | None] = mapped_column(String(600), nullable=True)
    source_url: Mapped[str | None] = mapped_column(String(600), nullable=True)

    supplier: Mapped[MaterialSupplier] = relationship(back_populates="products")


class SelectionStatus(str, enum.Enum):
    PROPOSED = "PROPOSED"
    APPROVED = "APPROVED"
    CHANGE_REQUESTED = "CHANGE_REQUESTED"


class MaterialSelection(Base):
    """A material/colour the ID has chosen for a job area, for client review."""

    __tablename__ = "material_selections"

    job_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("jobs.id", ondelete="CASCADE"), nullable=False, index=True
    )
    product_id: Mapped[uuid.UUID | None] = mapped_column(
        ForeignKey("material_products.id", ondelete="SET NULL"), nullable=True
    )
    category: Mapped[MaterialCategory] = mapped_column(
        SAEnum(MaterialCategory, name="material_category", create_type=False),
        nullable=False,
    )
    area: Mapped[str | None] = mapped_column(String(160), nullable=True)  # e.g. "Living room floor"
    colour: Mapped[str | None] = mapped_column(String(120), nullable=True)
    colour_hex: Mapped[str | None] = mapped_column(String(9), nullable=True)
    note: Mapped[str | None] = mapped_column(Text, nullable=True)
    status: Mapped[SelectionStatus] = mapped_column(
        SAEnum(SelectionStatus, name="selection_status"),
        default=SelectionStatus.PROPOSED,
        nullable=False,
    )
    selected_by: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id"), nullable=False)
