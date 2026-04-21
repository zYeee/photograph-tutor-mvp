from fastapi import APIRouter, Query
from livekit.api import AccessToken, VideoGrants

from app.settings import settings

router = APIRouter()


@router.get("/token")
async def get_token(
    room: str = Query(..., description="LiveKit room name"),
    identity: str = Query(default="user", description="Participant identity"),
) -> dict:
    token = (
        AccessToken(api_key=settings.livekit_api_key, api_secret=settings.livekit_api_secret)
        .with_identity(identity)
        .with_grants(VideoGrants(room_join=True, room=room))
        .to_jwt()
    )
    return {"token": token, "url": settings.livekit_public_url}
