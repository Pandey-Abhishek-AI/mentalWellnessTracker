"""Tests for database engine factory."""

import pytest
from sqlalchemy.dialects import sqlite

from src.db.engine import create_db_engine


def test_create_db_engine_rejects_supabase_project_url():
    with pytest.raises(ValueError, match="not a Supabase project URL"):
        create_db_engine("https://sgdaflmiplpeuixeulrq.supabase.co")


def test_create_db_engine_sqlite_uses_check_same_thread():
    engine = create_db_engine("sqlite:///:memory:")
    try:
        assert isinstance(engine.dialect, sqlite.dialect)
        assert engine.url.drivername == "sqlite"
    finally:
        engine.dispose()


def test_create_db_engine_postgres_uses_pool_pre_ping():
    pytest.importorskip("psycopg")
    engine = create_db_engine("postgresql+psycopg://user:pass@localhost/test")
    try:
        assert engine.url.drivername == "postgresql+psycopg"
        assert engine.pool._pre_ping is True
    finally:
        engine.dispose()
