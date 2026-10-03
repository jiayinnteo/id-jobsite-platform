"""Schemas for device push-token registration."""

import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from app.models.device import DevicePlatform


class DeviceRegister(BaseModel):
    token: str = Field(min_length=1, max_length=512)
    platform: DevicePlatform


class DeviceUnregister(BaseModel):
    token: str = Field(min_length=1, max_length=512)


class DeviceTokenOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    platform: DevicePlatform
    created_at: datetime
