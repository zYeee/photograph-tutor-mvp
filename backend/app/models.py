from datetime import datetime, timezone
from typing import Optional

from sqlalchemy import (
    CheckConstraint,
    DateTime,
    Float,
    ForeignKey,
    Integer,
    String,
    Text,
    UniqueConstraint,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    email: Mapped[str] = mapped_column(String, unique=True, nullable=False)
    display_name: Mapped[str] = mapped_column(String, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), onupdate=_utcnow, nullable=False)

    def to_dict(self) -> dict:
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}


class Session(Base):
    __tablename__ = "sessions"
    __table_args__ = (
        CheckConstraint("mode IN ('structured_learning','scene_advice')", name="ck_sessions_mode"),
        CheckConstraint("user_level IN ('beginner','intermediate','advanced')", name="ck_sessions_user_level"),
        CheckConstraint(
            "equipment_type IN ('smartphone','mirrorless','dslr','point-and-shoot','film')",
            name="ck_sessions_equipment_type",
        ),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"), nullable=False)
    livekit_room_name: Mapped[str] = mapped_column(String, unique=True, nullable=False)
    mode: Mapped[str] = mapped_column(String, nullable=False)
    user_level: Mapped[str] = mapped_column(String, nullable=False)
    equipment_type: Mapped[str] = mapped_column(String, nullable=False)
    last_topic_id: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("topics.id"), nullable=True)
    started_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), nullable=False)
    ended_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    summary: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    def to_dict(self) -> dict:
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}


class Message(Base):
    __tablename__ = "messages"
    __table_args__ = (
        CheckConstraint("role IN ('user','assistant','system')", name="ck_messages_role"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    session_id: Mapped[int] = mapped_column(Integer, ForeignKey("sessions.id"), nullable=False)
    role: Mapped[str] = mapped_column(String, nullable=False)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    token_count: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), nullable=False)

    def to_dict(self) -> dict:
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}


class Topic(Base):
    __tablename__ = "topics"
    __table_args__ = (
        CheckConstraint("difficulty BETWEEN 1 AND 5", name="ck_topics_difficulty"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    slug: Mapped[str] = mapped_column(String, unique=True, nullable=False)
    title: Mapped[str] = mapped_column(String, nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    level: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    parent_id: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("topics.id"), nullable=True)
    difficulty: Mapped[int] = mapped_column(Integer, nullable=False)
    sort_order: Mapped[int] = mapped_column(Integer, nullable=False, server_default="0")

    def to_dict(self) -> dict:
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}


class SessionTopic(Base):
    __tablename__ = "session_topics"
    __table_args__ = (
        UniqueConstraint("session_id", "topic_id", name="uq_session_topics"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    session_id: Mapped[int] = mapped_column(Integer, ForeignKey("sessions.id"), nullable=False)
    topic_id: Mapped[int] = mapped_column(Integer, ForeignKey("topics.id"), nullable=False)
    completed_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), nullable=False)

    def to_dict(self) -> dict:
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}


class UserTopicProgress(Base):
    __tablename__ = "user_topic_progress"
    __table_args__ = (
        UniqueConstraint("user_id", "topic_id", name="uq_user_topic_progress"),
        CheckConstraint(
            "status IN ('not_started','in_progress','completed')",
            name="ck_user_topic_progress_status",
        ),
        CheckConstraint("proficiency BETWEEN 0.0 AND 1.0", name="ck_user_topic_progress_proficiency"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"), nullable=False)
    topic_id: Mapped[int] = mapped_column(Integer, ForeignKey("topics.id"), nullable=False)
    status: Mapped[str] = mapped_column(String, nullable=False, server_default="not_started")
    proficiency: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    last_visited_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    updated_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), onupdate=_utcnow, nullable=False)

    def to_dict(self) -> dict:
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}


class PhotoSubmission(Base):
    __tablename__ = "photo_submissions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"), nullable=False)
    session_id: Mapped[int] = mapped_column(Integer, ForeignKey("sessions.id"), nullable=False)
    storage_path: Mapped[str] = mapped_column(String, nullable=False)
    caption: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    submitted_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), nullable=False)

    def to_dict(self) -> dict:
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}


class PhotoFeedback(Base):
    __tablename__ = "photo_feedback"
    __table_args__ = (
        CheckConstraint("composition_score BETWEEN 0.0 AND 1.0", name="ck_photo_feedback_composition"),
        CheckConstraint("exposure_score BETWEEN 0.0 AND 1.0", name="ck_photo_feedback_exposure"),
        CheckConstraint("focus_score BETWEEN 0.0 AND 1.0", name="ck_photo_feedback_focus"),
        CheckConstraint("lighting_score BETWEEN 0.0 AND 1.0", name="ck_photo_feedback_lighting"),
        CheckConstraint("overall_score BETWEEN 0.0 AND 1.0", name="ck_photo_feedback_overall"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    submission_id: Mapped[int] = mapped_column(Integer, ForeignKey("photo_submissions.id"), unique=True, nullable=False)
    message_id: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("messages.id"), nullable=True)
    composition_score: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    exposure_score: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    focus_score: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    lighting_score: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    overall_score: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), nullable=False)

    def to_dict(self) -> dict:
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}
