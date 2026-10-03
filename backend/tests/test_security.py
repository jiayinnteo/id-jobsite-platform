"""Unit tests for password hashing and JWT handling (no DB needed)."""

import pytest
from jose import JWTError

from app.core.security import (
    ACCESS,
    REFRESH,
    create_access_token,
    create_refresh_token,
    decode_token,
    hash_password,
    verify_password,
)


def test_password_hash_roundtrip():
    h = hash_password("correct horse battery")
    assert h != "correct horse battery"
    assert verify_password("correct horse battery", h) is True
    assert verify_password("wrong", h) is False


def test_access_token_type_enforced():
    token = create_access_token("user-123")
    payload = decode_token(token, expected_type=ACCESS)
    assert payload["sub"] == "user-123"
    assert payload["type"] == ACCESS


def test_refresh_token_rejected_as_access():
    refresh = create_refresh_token("user-123")
    with pytest.raises(JWTError):
        decode_token(refresh, expected_type=ACCESS)


def test_decode_rejects_tampered_token():
    token = create_access_token("user-123") + "tamper"
    with pytest.raises(JWTError):
        decode_token(token)
