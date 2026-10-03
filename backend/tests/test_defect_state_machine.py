"""Unit tests for the defect status transition rules (no DB)."""

from app.models.defect import ALLOWED_TRANSITIONS
from app.models.defect import DefectStatus as S


def _can(frm: S, to: S) -> bool:
    return to in ALLOWED_TRANSITIONS.get(frm, set())


def test_happy_path_transitions():
    assert _can(S.OPEN, S.ASSIGNED)
    assert _can(S.ASSIGNED, S.IN_PROGRESS)
    assert _can(S.IN_PROGRESS, S.RECTIFIED)
    assert _can(S.RECTIFIED, S.ACCEPTED)
    assert _can(S.RECTIFIED, S.REJECTED)
    assert _can(S.ACCEPTED, S.CLOSED)


def test_rejected_loops_back_to_assigned():
    assert _can(S.REJECTED, S.ASSIGNED)


def test_illegal_jumps_blocked():
    assert not _can(S.OPEN, S.RECTIFIED)
    assert not _can(S.OPEN, S.ACCEPTED)
    assert not _can(S.ASSIGNED, S.ACCEPTED)
    assert not _can(S.CLOSED, S.OPEN)  # terminal
    assert not _can(S.RECTIFIED, S.CLOSED)
