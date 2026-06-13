"""Database engine factory for SQLite and PostgreSQL (Supabase)."""

from sqlalchemy import Engine, create_engine


def create_db_engine(database_url: str) -> Engine:
    """Create a SQLAlchemy engine with driver-appropriate options."""
    if database_url.startswith(("http://", "https://")):
        raise ValueError(
            "DATABASE_URL must be a PostgreSQL connection string, not a Supabase project URL. "
            "In Supabase go to Project Settings → Database → Connection string → URI, "
            "copy the postgresql:// value, then change it to postgresql+psycopg:// in .env."
        )

    if database_url.startswith("sqlite"):
        return create_engine(
            database_url,
            connect_args={"check_same_thread": False},
        )

    return create_engine(
        database_url,
        pool_pre_ping=True,
    )
