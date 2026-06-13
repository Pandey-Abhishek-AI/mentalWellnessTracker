"""Database session and wellness data repository."""

from datetime import date, datetime

from sqlalchemy import select, text
from sqlalchemy.orm import Session, sessionmaker

from app.config import get_settings
from src.db.engine import create_db_engine
from src.models import ChatMessage, Insight, JournalEntry, MoodEntry, User
from src.models.ai_usage import AiFeatureUsage
from src.models.base import Base
from src.utils.tokens import estimate_tokens


class WellnessRepository:
    def __init__(self, database_url: str | None = None) -> None:
        settings = get_settings()
        url = database_url or settings.database_url
        self.engine = create_db_engine(url)
        Base.metadata.create_all(self.engine)
        self._migrate_schema()
        self.SessionLocal = sessionmaker(bind=self.engine, autoflush=False, autocommit=False)

    def _migrate_schema(self) -> None:
        """Add auth columns to existing SQLite databases."""
        if not self.engine.url.drivername.startswith("sqlite"):
            return
        with self.engine.connect() as conn:
            rows = conn.execute(text("PRAGMA table_info(users)")).fetchall()
            columns = {row[1] for row in rows}
            additions = {
                "email": "VARCHAR(255)",
                "user_uuid": "VARCHAR(36)",
                "password_hash": "VARCHAR(128)",
                "password_salt": "VARCHAR(64)",
            }
            for name, col_type in additions.items():
                if name not in columns:
                    conn.execute(text(f"ALTER TABLE users ADD COLUMN {name} {col_type}"))
            conn.commit()

    def _session(self) -> Session:
        return self.SessionLocal()

    def create_user(
        self,
        email: str,
        user_uuid: str,
        password_hash: str,
        password_salt: str,
        exam_type: str = "NEET",
    ) -> User:
        with self._session() as session:
            user = User(
                email=email,
                user_uuid=user_uuid,
                password_hash=password_hash,
                password_salt=password_salt,
                exam_type=exam_type,
            )
            session.add(user)
            session.commit()
            session.refresh(user)
            return user

    def get_user_by_email(self, email: str) -> User | None:
        with self._session() as session:
            return session.execute(
                select(User).where(User.email == email)
            ).scalar_one_or_none()

    def get_user_by_uuid(self, user_uuid: str) -> User | None:
        with self._session() as session:
            return session.execute(
                select(User).where(User.user_uuid == user_uuid)
            ).scalar_one_or_none()

    def update_user_profile(
        self,
        user_id: int,
        exam_type: str,
        study_context: str,
        disclaimer_accepted: bool = False,
    ) -> User:
        from datetime import datetime

        with self._session() as session:
            user = session.get(User, user_id)
            if user is None:
                raise ValueError(f"User {user_id} not found")
            user.exam_type = exam_type
            user.study_context = study_context
            if disclaimer_accepted:
                user.disclaimer_accepted_at = datetime.utcnow()
            session.commit()
            session.refresh(user)
            return user

    def upsert_mood_entry(
        self,
        user_id: int,
        mood: int,
        energy: int,
        sleep_quality: int,
        tags: list[str],
        entry_date: date,
    ) -> MoodEntry:
        with self._session() as session:
            existing = session.execute(
                select(MoodEntry).where(
                    MoodEntry.user_id == user_id,
                    MoodEntry.entry_date == entry_date,
                )
            ).scalar_one_or_none()

            if existing:
                existing.mood = mood
                existing.energy = energy
                existing.sleep_quality = sleep_quality
                existing.tags = tags
                entry = existing
            else:
                entry = MoodEntry(
                    user_id=user_id,
                    mood=mood,
                    energy=energy,
                    sleep_quality=sleep_quality,
                    tags=tags,
                    entry_date=entry_date,
                )
                session.add(entry)
            session.commit()
            session.refresh(entry)
            return entry

    def upsert_journal_entry(
        self,
        user_id: int,
        content: str,
        crisis_flagged: bool,
        entry_date: date,
    ) -> JournalEntry:
        with self._session() as session:
            existing = session.execute(
                select(JournalEntry).where(
                    JournalEntry.user_id == user_id,
                    JournalEntry.entry_date == entry_date,
                )
            ).scalar_one_or_none()

            if existing:
                existing.content = content
                existing.crisis_flagged = crisis_flagged
                entry = existing
            else:
                entry = JournalEntry(
                    user_id=user_id,
                    content=content,
                    crisis_flagged=crisis_flagged,
                    entry_date=entry_date,
                )
                session.add(entry)
            session.commit()
            session.refresh(entry)
            return entry

    def get_mood_entries_since(self, user_id: int, since: date) -> list[MoodEntry]:
        with self._session() as session:
            return list(
                session.execute(
                    select(MoodEntry)
                    .where(MoodEntry.user_id == user_id, MoodEntry.entry_date >= since)
                    .order_by(MoodEntry.entry_date.desc())
                ).scalars()
            )

    def get_journal_entries_since(self, user_id: int, since: date) -> list[JournalEntry]:
        with self._session() as session:
            return list(
                session.execute(
                    select(JournalEntry)
                    .where(JournalEntry.user_id == user_id, JournalEntry.entry_date >= since)
                    .order_by(JournalEntry.entry_date.desc())
                ).scalars()
            )

    def save_insight(
        self,
        user_id: int,
        summary_json: dict,
        period_start: date,
        period_end: date,
    ) -> Insight:
        with self._session() as session:
            insight = Insight(
                user_id=user_id,
                summary_json=summary_json,
                period_start=period_start,
                period_end=period_end,
            )
            session.add(insight)
            session.commit()
            session.refresh(insight)
            return insight

    def get_latest_insight(self, user_id: int) -> Insight | None:
        with self._session() as session:
            return session.execute(
                select(Insight)
                .where(Insight.user_id == user_id)
                .order_by(Insight.created_at.desc())
                .limit(1)
            ).scalar_one_or_none()

    def get_insights(self, user_id: int, limit: int = 20) -> list[Insight]:
        with self._session() as session:
            return list(
                session.execute(
                    select(Insight)
                    .where(Insight.user_id == user_id)
                    .order_by(Insight.created_at.desc())
                    .limit(limit)
                ).scalars()
            )

    def save_chat_message(
        self,
        user_id: int,
        role: str,
        content: str,
        crisis_flagged: bool = False,
    ) -> ChatMessage:
        with self._session() as session:
            msg = ChatMessage(
                user_id=user_id,
                role=role,
                content=content,
                crisis_flagged=crisis_flagged,
            )
            session.add(msg)
            session.commit()
            session.refresh(msg)
            return msg

    def get_chat_history(self, user_id: int, limit: int = 50) -> list[ChatMessage]:
        with self._session() as session:
            return list(
                session.execute(
                    select(ChatMessage)
                    .where(ChatMessage.user_id == user_id)
                    .order_by(ChatMessage.created_at.desc())
                    .limit(limit)
                ).scalars()
            )

    def estimate_chat_tokens_since(self, user_id: int, since: datetime) -> int:
        with self._session() as session:
            messages = session.execute(
                select(ChatMessage)
                .where(ChatMessage.user_id == user_id)
                .where(ChatMessage.created_at >= since)
            ).scalars()
            return sum(estimate_tokens(msg.content) for msg in messages)

    def estimate_chat_tokens_since_uuid(self, user_uuid: str, since: datetime) -> int:
        with self._session() as session:
            messages = session.execute(
                select(ChatMessage)
                .join(User, ChatMessage.user_id == User.id)
                .where(User.user_uuid == user_uuid)
                .where(ChatMessage.created_at >= since)
            ).scalars()
            return sum(estimate_tokens(msg.content) for msg in messages)

    def count_insights_since(self, user_id: int, since: datetime) -> int:
        with self._session() as session:
            rows = session.execute(
                select(Insight)
                .where(Insight.user_id == user_id)
                .where(Insight.created_at >= since)
            ).scalars()
            return len(list(rows))

    def count_feature_usage_since_uuid(
        self, user_uuid: str, feature: str, since: datetime
    ) -> int:
        with self._session() as session:
            rows = session.execute(
                select(AiFeatureUsage)
                .where(AiFeatureUsage.user_uuid == user_uuid)
                .where(AiFeatureUsage.feature == feature)
                .where(AiFeatureUsage.created_at >= since)
            ).scalars()
            return len(list(rows))

    def log_feature_usage(self, user_uuid: str, feature: str) -> None:
        with self._session() as session:
            session.add(AiFeatureUsage(user_uuid=user_uuid, feature=feature))
            session.commit()

    def clear_user_data(self, user_id: int) -> None:
        with self._session() as session:
            for model in (ChatMessage, Insight, JournalEntry, MoodEntry):
                rows = session.execute(
                    select(model).where(model.user_id == user_id)
                ).scalars()
                for row in rows:
                    session.delete(row)
            session.commit()

    def get_user(self, user_id: int) -> User | None:
        with self._session() as session:
            return session.get(User, user_id)
