from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import JSONResponse
from sqlalchemy import select
from sqlalchemy.dialects.sqlite import insert as sqlite_insert
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models import Session, SessionTopic, Topic

router = APIRouter()


def _topic_dict(t: Topic) -> dict:
    return t.to_dict()


@router.get("/topics")
async def list_topics(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Topic).order_by(Topic.sort_order))
    all_topics = result.scalars().all()

    roots = [t for t in all_topics if t.parent_id is None]
    children: dict[int, list[dict]] = {}
    for t in all_topics:
        if t.parent_id is not None:
            children.setdefault(t.parent_id, []).append(_topic_dict(t))

    return [
        {**_topic_dict(r), "children": sorted(children.get(r.id, []), key=lambda x: x["sort_order"])}
        for r in roots
    ]


@router.post("/sessions/{session_id}/topics/{slug}", status_code=201)
async def mark_topic_complete(session_id: int, slug: str, db: AsyncSession = Depends(get_db)):
    session = await db.get(Session, session_id)
    if session is None:
        raise HTTPException(status_code=404, detail="Session not found")

    topic_result = await db.execute(select(Topic).where(Topic.slug == slug))
    topic = topic_result.scalar_one_or_none()
    if topic is None:
        raise HTTPException(status_code=404, detail=f"Topic '{slug}' not found")

    stmt = (
        sqlite_insert(SessionTopic)
        .values(session_id=session_id, topic_id=topic.id)
        .on_conflict_do_nothing(index_elements=["session_id", "topic_id"])
    )
    result = await db.execute(stmt)
    already_complete = result.rowcount == 0

    session.last_topic_id = topic.id
    await db.commit()

    http_status = 200 if already_complete else 201
    return JSONResponse(
        status_code=http_status,
        content={"session_id": session_id, "topic_slug": slug, "already_complete": already_complete},
    )


@router.get("/sessions/{session_id}/topics")
async def list_session_topics(session_id: int, db: AsyncSession = Depends(get_db)):
    session = await db.get(Session, session_id)
    if session is None:
        raise HTTPException(status_code=404, detail="Session not found")

    result = await db.execute(
        select(SessionTopic, Topic)
        .join(Topic, SessionTopic.topic_id == Topic.id)
        .where(SessionTopic.session_id == session_id)
        .order_by(SessionTopic.completed_at.asc())
    )
    rows = result.all()
    return [
        {
            **st.to_dict(),
            "slug": t.slug,
            "title": t.title,
            "completed_at": st.completed_at.isoformat() if st.completed_at else None,
        }
        for st, t in rows
    ]
