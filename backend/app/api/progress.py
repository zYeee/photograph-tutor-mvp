from datetime import datetime, timezone
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.dialects.sqlite import insert as sqlite_insert
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models import Topic, UserTopicProgress

router = APIRouter()


class ProgressUpsert(BaseModel):
    status: str
    proficiency: Optional[float] = None


@router.get("/users/{user_id}/progress")
async def get_user_progress(user_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(UserTopicProgress, Topic.slug, Topic.title)
        .join(Topic, UserTopicProgress.topic_id == Topic.id)
        .where(UserTopicProgress.user_id == user_id)
        .order_by(Topic.slug)
    )
    rows = result.all()
    return [
        {
            **utp.to_dict(),
            "slug": slug,
            "title": title,
            "last_visited_at": utp.last_visited_at.isoformat() if utp.last_visited_at else None,
            "updated_at": utp.updated_at.isoformat() if utp.updated_at else None,
        }
        for utp, slug, title in rows
    ]


@router.put("/users/{user_id}/progress/{slug}")
async def upsert_user_progress(
    user_id: int, slug: str, body: ProgressUpsert, db: AsyncSession = Depends(get_db)
):
    topic_result = await db.execute(select(Topic.id).where(Topic.slug == slug))
    topic_id = topic_result.scalar_one_or_none()
    if topic_id is None:
        raise HTTPException(status_code=404, detail=f"Topic '{slug}' not found")

    now = datetime.now(timezone.utc)
    stmt = (
        sqlite_insert(UserTopicProgress)
        .values(
            user_id=user_id,
            topic_id=topic_id,
            status=body.status,
            proficiency=body.proficiency,
            last_visited_at=now,
            updated_at=now,
        )
        .on_conflict_do_update(
            index_elements=["user_id", "topic_id"],
            set_=dict(
                status=body.status,
                proficiency=body.proficiency,
                last_visited_at=now,
                updated_at=now,
            ),
        )
    )
    await db.execute(stmt)
    await db.commit()

    row = await db.execute(
        select(UserTopicProgress).where(
            UserTopicProgress.user_id == user_id,
            UserTopicProgress.topic_id == topic_id,
        )
    )
    utp = row.scalar_one()
    return {
        **utp.to_dict(),
        "slug": slug,
        "last_visited_at": utp.last_visited_at.isoformat() if utp.last_visited_at else None,
        "updated_at": utp.updated_at.isoformat() if utp.updated_at else None,
    }
