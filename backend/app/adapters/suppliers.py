"""Supplier catalogue adapters (pluggable).

Each supplier is a `SupplierCatalogue` that yields `CatalogueItem`s. A supplier
can be backed by an official API, a periodic import of its public catalogue, or
curated data — all behind the same interface, so new suppliers (Singapore and
Malaysia) are added without changing callers (Requirement 17.3).

Important: where a supplier has no open API or rights to reuse imagery, we keep a
`source_url` and link out to the supplier page rather than rehosting their data
(Requirement 17.4 / 17.8). The sample catalogues below are small, illustrative
placeholders — real catalogue data/credentials are wired per supplier later.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass

from app.models.material import Country, MaterialCategory


@dataclass
class CatalogueItem:
    category: MaterialCategory
    name: str
    product_code: str | None = None
    colour: str | None = None
    colour_hex: str | None = None
    finish: str | None = None
    swatch_url: str | None = None
    source_url: str | None = None


@dataclass
class SupplierInfo:
    key: str
    name: str
    country: Country
    website_url: str


class SupplierCatalogue(ABC):
    info: SupplierInfo

    @abstractmethod
    async def fetch_catalogue(self) -> list[CatalogueItem]:
        """Return the supplier's catalogue items (API / import / curated)."""


class EcoPlusVinyl(SupplierCatalogue):
    """ECO+ — vinyl flooring (Singapore). Sample curated data."""

    info = SupplierInfo(
        key="eco_plus",
        name="ECO+ Vinyl",
        country=Country.SG,
        website_url="https://www.ecoplus.com.sg",
    )

    async def fetch_catalogue(self) -> list[CatalogueItem]:
        base = self.info.website_url
        return [
            CatalogueItem(
                category=MaterialCategory.VINYL,
                name="Natural Oak",
                product_code="EP-V101",
                colour="Warm Oak",
                colour_hex="#C8A27A",
                finish="Matte",
                source_url=base,
            ),
            CatalogueItem(
                category=MaterialCategory.VINYL,
                name="Smoked Walnut",
                product_code="EP-V204",
                colour="Dark Walnut",
                colour_hex="#5B4636",
                finish="Textured",
                source_url=base,
            ),
            CatalogueItem(
                category=MaterialCategory.VINYL,
                name="Nordic Ash",
                product_code="EP-V310",
                colour="Light Grey",
                colour_hex="#C9C6BF",
                finish="Matte",
                source_url=base,
            ),
        ]


class NipponPaint(SupplierCatalogue):
    """Nippon Paint — paints (Singapore / Malaysia). Sample curated data."""

    info = SupplierInfo(
        key="nippon_paint",
        name="Nippon Paint",
        country=Country.SG,
        website_url="https://www.nipponpaint.com.sg",
    )

    async def fetch_catalogue(self) -> list[CatalogueItem]:
        base = self.info.website_url
        return [
            CatalogueItem(
                category=MaterialCategory.PAINT,
                name="Vinilex",
                product_code="NP-OW1001P",
                colour="Hog Bristle",
                colour_hex="#E7E0CF",
                finish="Matte",
                source_url=base,
            ),
            CatalogueItem(
                category=MaterialCategory.PAINT,
                name="Odour-less All-in-1",
                product_code="NP-N1876P",
                colour="Misty Grey",
                colour_hex="#B9BBB6",
                finish="Low Sheen",
                source_url=base,
            ),
            CatalogueItem(
                category=MaterialCategory.PAINT,
                name="Momento Textured",
                product_code="NP-SE05",
                colour="Terra Clay",
                colour_hex="#C07A54",
                finish="Textured",
                source_url=base,
            ),
        ]


class LamitakLaminate(SupplierCatalogue):
    """Lamitak — laminates (Singapore). Sample curated data."""

    info = SupplierInfo(
        key="lamitak",
        name="Lamitak Laminate",
        country=Country.SG,
        website_url="https://www.lamitak.com",
    )

    async def fetch_catalogue(self) -> list[CatalogueItem]:
        base = self.info.website_url
        return [
            CatalogueItem(
                category=MaterialCategory.LAMINATE,
                name="Fine Oak",
                product_code="LT-8812",
                colour="Honey Oak",
                colour_hex="#CBA16B",
                finish="Woodgrain",
                source_url=base,
            ),
            CatalogueItem(
                category=MaterialCategory.LAMINATE,
                name="Marble Carrara",
                product_code="LT-9901",
                colour="White Marble",
                colour_hex="#EDEDEA",
                finish="Gloss",
                source_url=base,
            ),
        ]


class NiroTile(SupplierCatalogue):
    """Niro Granite — tiles (Malaysia). Sample curated data."""

    info = SupplierInfo(
        key="niro_granite",
        name="Niro Granite Tiles",
        country=Country.MY,
        website_url="https://www.nirogranite.com.my",
    )

    async def fetch_catalogue(self) -> list[CatalogueItem]:
        base = self.info.website_url
        return [
            CatalogueItem(
                category=MaterialCategory.TILE,
                name="Grand Marble",
                product_code="NG-GM60",
                colour="Statuario",
                colour_hex="#F0F0ED",
                finish="Polished",
                source_url=base,
            ),
            CatalogueItem(
                category=MaterialCategory.TILE,
                name="Urban Concrete",
                product_code="NG-UC30",
                colour="Mid Grey",
                colour_hex="#9A9A96",
                finish="Matte",
                source_url=base,
            ),
        ]


class HafaryWorktop(SupplierCatalogue):
    """Hafary — worktops/surfaces (Singapore). Sample curated data."""

    info = SupplierInfo(
        key="hafary",
        name="Hafary Worktop",
        country=Country.SG,
        website_url="https://www.hafary.com.sg",
    )

    async def fetch_catalogue(self) -> list[CatalogueItem]:
        base = self.info.website_url
        return [
            CatalogueItem(
                category=MaterialCategory.WORKTOP,
                name="Quartz Pure",
                product_code="HF-Q10",
                colour="Pure White",
                colour_hex="#F4F4F2",
                finish="Honed",
                source_url=base,
            ),
            CatalogueItem(
                category=MaterialCategory.WORKTOP,
                name="Sintered Stone",
                product_code="HF-SS22",
                colour="Graphite",
                colour_hex="#3C3C3E",
                finish="Matte",
                source_url=base,
            ),
        ]


# Registry of all known suppliers. Add new SG/MY suppliers here.
ALL_SUPPLIERS: list[SupplierCatalogue] = [
    EcoPlusVinyl(),
    NipponPaint(),
    LamitakLaminate(),
    NiroTile(),
    HafaryWorktop(),
]


def all_suppliers() -> list[SupplierCatalogue]:
    return ALL_SUPPLIERS
