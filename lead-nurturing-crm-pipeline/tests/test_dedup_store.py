import os

import pytest

from src.dedup_store import is_duplicate, record_lead


@pytest.fixture
def db_path(tmp_path):
    return str(tmp_path / "test_leads.db")


def test_new_lead_is_not_duplicate(db_path):
    assert is_duplicate(db_path, "email:new@example.com") is False


def test_recorded_lead_is_duplicate(db_path):
    record_lead(db_path, "email:seen@example.com", "warm")
    assert is_duplicate(db_path, "email:seen@example.com") is True


def test_recording_twice_does_not_error(db_path):
    record_lead(db_path, "email:seen@example.com", "warm")
    record_lead(db_path, "email:seen@example.com", "hot")
    assert is_duplicate(db_path, "email:seen@example.com") is True
