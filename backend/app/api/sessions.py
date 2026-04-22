from datetime import datetime, timezone
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models import Session, Topic
from app.settings import settings

router = APIRouter()

AGENT_NAME = "photo-tutor"


class SessionCreate(BaseModel):
    user_id: int
    livekit_room_name: str
    mode: str
    user_level: str
    equipment_type: str


class SessionClose(BaseModel):
    summary: Optional[str] = None


class SessionPatch(BaseModel):
    user_level: Optional[str] = None
    equipment_type: Optional[str] = None
    current_topic_slug: Optional[str] = None


def _session_row(session: Session, last_topic: Optional[str]) -> dict:
    d = session.to_dict()
    d["last_topic"] = last_topic
    if isinstance(d.get("started_at"), datetime):
        d["started_at"] = d["started_at"].isoformat()
    if isinstance(d.get("ended_at"), datetime):
        d["ended_at"] = d["ended_at"].isoformat()
    return d


@router.post("/sessions", status_code=201)
async def create_session(body: SessionCreate, db: AsyncSession = Depends(get_db)):
    session = Session(
        user_id=body.user_id,
        livekit_room_name=body.livekit_room_name,
        mode=body.mode,
        user_level=body.user_level,
        equipment_type=body.equipment_type,
    )
    db.add(session)
    try:
        await db.commit()
        await db.refresh(session)
    except IntegrityError as e:
        await db.rollback()
        msg = str(e.orig).lower()
        if "unique" in msg or "livekit_room_name" in msg:
            raise HTTPException(status_code=409, detail="livekit_room_name already exists")
        raise HTTPException(status_code=422, detail=str(e.orig))

    return _session_row(session, None)


async def dispatch_agent(room_name: str) -> None:
    try:
        from livekit.api import LiveKitAPI, CreateAgentDispatchRequest
        async with LiveKitAPI(
            url=settings.livekit_url,
            api_key=settings.livekit_api_key,
            api_secret=settings.livekit_api_secret,
        ) as lk:
            await lk.agent_dispatch.create_dispatch(
                CreateAgentDispatchRequest(agent_name=AGENT_NAME, room=room_name)
            )
    except Exception as exc:
        import logging
        logging.getLogger(__name__).warning("Agent dispatch failed for room %s: %s", room_name, exc)


@router.get("/sessions")
async def list_sessions(user_id: int, db: AsyncSession = Depends(get_db)):
    stmt = (
        select(Session, Topic.title.label("last_topic"))
        .outerjoin(Topic, Session.last_topic_id == Topic.id)
        .where(Session.user_id == user_id)
        .order_by(Session.started_at.desc())
    )
    rows = (await db.execute(stmt)).all()
    return [_session_row(s, last_topic) for s, last_topic in rows]


@router.get("/sessions/lookup")
async def lookup_session(livekit_room_name: str, db: AsyncSession = Depends(get_db)):
    stmt = (
        select(Session, Topic.title.label("last_topic"))
        .outerjoin(Topic, Session.last_topic_id == Topic.id)
        .where(Session.livekit_room_name == livekit_room_name)
    )
    row = (await db.execute(stmt)).first()
    if row is None:
        raise HTTPException(status_code=404, detail="Session not found")
    session, last_topic = row
    return _session_row(session, last_topic)


@router.get("/sessions/{session_id}")
async def get_session(session_id: int, db: AsyncSession = Depends(get_db)):
    stmt = (
        select(Session, Topic.title.label("last_topic"))
        .outerjoin(Topic, Session.last_topic_id == Topic.id)
        .where(Session.id == session_id)
    )
    row = (await db.execute(stmt)).first()
    if row is None:
        raise HTTPException(status_code=404, detail="Session not found")
    session, last_topic = row
    return _session_row(session, last_topic)


@router.patch("/sessions/{session_id}", response_model=None)
async def patch_session(session_id: int, body: SessionPatch, db: AsyncSession = Depends(get_db)):
    result = await db.get(Session, session_id)
    if result is None:
        raise HTTPException(status_code=404, detail="Session not found")
    if body.user_level is not None:
        result.user_level = body.user_level
    if body.equipment_type is not None:
        result.equipment_type = body.equipment_type
    if body.current_topic_slug is not None:
        topic_result = await db.execute(select(Topic).where(Topic.slug == body.current_topic_slug))
        topic = topic_result.scalar_one_or_none()
        if topic is not None:
            result.last_topic_id = topic.id
    await db.commit()
    await db.refresh(result)
    return _session_row(result, None)


@router.patch("/sessions/{session_id}/close")
async def close_session(session_id: int, body: SessionClose, db: AsyncSession = Depends(get_db)):
    result = await db.get(Session, session_id)
    if result is None:
        raise HTTPException(status_code=404, detail="Session not found")
    result.ended_at = datetime.now(timezone.utc)
    if body.summary is not None:
        result.summary = body.summary
    await db.commit()
    await db.refresh(result)
    return _session_row(result, None)
