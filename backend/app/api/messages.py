from typing import Optional

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models import Message, Session

router = APIRouter()


class MessageCreate(BaseModel):
    role: str
    content: str
    token_count: Optional[int] = None


def _msg_dict(m: Message) -> dict:
    d = m.to_dict()
    if d.get("created_at") is not None:
        d["created_at"] = d["created_at"].isoformat()
    return d


@router.post("/sessions/{session_id}/messages", status_code=201)
async def append_message(session_id: int, body: MessageCreate, db: AsyncSession = Depends(get_db)):
    session = await db.get(Session, session_id)
    if session is None:
        raise HTTPException(status_code=404, detail="Session not found")
    msg = Message(
        session_id=session_id,
        role=body.role,
        content=body.content,
        token_count=body.token_count,
    )
    db.add(msg)
    try:
        await db.commit()
        await db.refresh(msg)
    except Exception:
        await db.rollback()
        raise
    return _msg_dict(msg)


@router.get("/sessions/{session_id}/messages")
async def list_messages(session_id: int, db: AsyncSession = Depends(get_db)):
    session = await db.get(Session, session_id)
    if session is None:
        raise HTTPException(status_code=404, detail="Session not found")
    result = await db.execute(
        select(Message)
        .where(Message.session_id == session_id)
        .order_by(Message.created_at.asc())
    )
    return [_msg_dict(m) for m in result.scalars().all()]
