"""Unit tests for supplier catalogue adapters (no DB)."""

import pytest

from app.adapters.suppliers import all_suppliers
from app.models.material import Country


@pytest.mark.asyncio
async def test_all_suppliers_have_sg_and_my_coverage():
    countries = {s.info.country for s in all_suppliers()}
    assert Country.SG in countries
    assert Country.MY in countries


@pytest.mark.asyncio
async def test_catalogues_are_non_empty_and_carry_source_url():
    for supplier in all_suppliers():
        items = await supplier.fetch_catalogue()
        assert items, f"{supplier.info.key} returned no items"
        for item in items:
            # Attribution: every item links back to the supplier page.
            assert item.source_url, f"{supplier.info.key} item missing source_url"
            assert item.name


@pytest.mark.asyncio
async def test_known_suppliers_present():
    keys = {s.info.key for s in all_suppliers()}
    assert "eco_plus" in keys       # ECO+ vinyl
    assert "nippon_paint" in keys   # Nippon paint
