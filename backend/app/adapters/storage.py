"""StoragePort — object storage behind an interface.

Real S3-compatible implementation (boto3) when credentials are configured;
otherwise a Mock that returns deterministic local-style URLs so the app runs
end-to-end without any cloud account.
"""

from __future__ import annotations

import uuid
from abc import ABC, abstractmethod

from app.core.config import Settings, get_settings


class StoragePort(ABC):
    @abstractmethod
    def generate_key(self, prefix: str, filename: str) -> str: ...

    @abstractmethod
    def presigned_put_url(self, key: str, content_type: str) -> str: ...

    @abstractmethod
    def presigned_get_url(self, key: str) -> str: ...


class MockStorage(StoragePort):
    """No external calls. Useful for local dev and tests."""

    def __init__(self, settings: Settings):
        self._ttl = settings.presigned_url_ttl_seconds
        self._bucket = settings.s3_bucket

    def generate_key(self, prefix: str, filename: str) -> str:
        return f"{prefix}/{uuid.uuid4()}/{filename}"

    def presigned_put_url(self, key: str, content_type: str) -> str:
        return f"mock://{self._bucket}/{key}?op=put&ttl={self._ttl}"

    def presigned_get_url(self, key: str) -> str:
        return f"mock://{self._bucket}/{key}?op=get&ttl={self._ttl}"


class S3Storage(StoragePort):
    def __init__(self, settings: Settings):
        import boto3  # imported lazily so the mock path needs no boto3

        self._bucket = settings.s3_bucket
        self._ttl = settings.presigned_url_ttl_seconds
        self._client = boto3.client(
            "s3",
            endpoint_url=settings.s3_endpoint_url,
            region_name=settings.s3_region,
            aws_access_key_id=settings.s3_access_key,
            aws_secret_access_key=settings.s3_secret_key,
        )

    def generate_key(self, prefix: str, filename: str) -> str:
        return f"{prefix}/{uuid.uuid4()}/{filename}"

    def presigned_put_url(self, key: str, content_type: str) -> str:
        return self._client.generate_presigned_url(
            "put_object",
            Params={"Bucket": self._bucket, "Key": key, "ContentType": content_type},
            ExpiresIn=self._ttl,
        )

    def presigned_get_url(self, key: str) -> str:
        return self._client.generate_presigned_url(
            "get_object",
            Params={"Bucket": self._bucket, "Key": key},
            ExpiresIn=self._ttl,
        )


def get_storage() -> StoragePort:
    settings = get_settings()
    if settings.storage_mode == "s3":
        return S3Storage(settings)
    return MockStorage(settings)
