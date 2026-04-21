from contextlib import asynccontextmanager

from fastapi import FastAPI
from sqlalchemy.dialects.sqlite import insert as sqlite_insert

from app.curriculum import TOPICS
from app.database import AsyncSessionLocal, async_setup_db
from app.api.token import router as token_router
from app.api.sessions import router as sessions_router
from app.api.messages import router as messages_router
from app.api.topics import router as topics_router
from app.api.progress import router as progress_router


async def _seed_curriculum() -> None:
    from app.models import Topic
    from sqlalchemy import select

    async with AsyncSessionLocal() as db:
        # Insert root categories first (parent_id = NULL)
        for t in TOPICS:
            if t["parent_slug"] is None:
                stmt = sqlite_insert(Topic).values(
                    slug=t["slug"],
                    title=t["title"],
                    description=t.get("description"),
                    parent_id=None,
                    difficulty=t["difficulty"],
                    sort_order=t["sort_order"],
                ).on_conflict_do_nothing(index_elements=["slug"])
                await db.execute(stmt)
        await db.commit()

        # Insert leaf topics (need parent_id resolved from slug)
        for t in TOPICS:
            if t["parent_slug"] is not None:
                result = await db.execute(
                    select(Topic.id).where(Topic.slug == t["parent_slug"])
                )
                parent_id = result.scalar_one_or_none()
                if parent_id is None:
                    continue
                stmt = sqlite_insert(Topic).values(
                    slug=t["slug"],
                    title=t["title"],
                    description=t.get("description"),
                    parent_id=parent_id,
                    difficulty=t["difficulty"],
                    sort_order=t["sort_order"],
                ).on_conflict_do_nothing(index_elements=["slug"])
                await db.execute(stmt)
        await db.commit()


@asynccontextmanager
async def lifespan(app: FastAPI):
    await async_setup_db()
    await _seed_curriculum()
    yield


app = FastAPI(title="photograph-tutor", lifespan=lifespan)

app.include_router(token_router, prefix="/api")
app.include_router(sessions_router, prefix="/api")
app.include_router(messages_router, prefix="/api")
app.include_router(topics_router, prefix="/api")
app.include_router(progress_router, prefix="/api")


@app.get("/health")
async def health() -> dict:
    return {"status": "ok"}
