"""Database session and wellness data repository."""

from datetime import date

from sqlalchemy import select
from sqlalchemy.orm import Session, sessionmaker

from app.config import get_settings
from src.db.engine import create_db_engine
from src.models import ChatMessage, Insight, JournalEntry, MoodEntry, User
from src.models.base import Base


class WellnessRepository:
    def __init__(self, database_url: str | None = None) -> None:
        settings = get_settings()
        url = database_url or settings.database_url
        self.engine = create_db_engine(url)
        Base.metadata.create_all(self.engine)
        self.SessionLocal = sessionmaker(bind=self.engine, autoflush=False, autocommit=False)

    def _session(self) -> Session:
        return self.SessionLocal()

    def get_or_create_default_user(self) -> User:
        with self._session() as session:
            user = session.execute(select(User).where(User.id == 1)).scalar_one_or_none()
            if user is None:
                user = User(id=1, exam_type="NEET")
                session.add(user)
                session.commit()
                session.refresh(user)
            return user

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
