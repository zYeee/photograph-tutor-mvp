import logging
import os

from dotenv import load_dotenv

load_dotenv()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def main() -> None:
    livekit_url = os.getenv("LIVEKIT_URL", "ws://localhost:7880")
    api_key = os.getenv("LIVEKIT_API_KEY", "")
    api_secret = os.getenv("LIVEKIT_API_SECRET", "")
    openai_key = os.getenv("OPENAI_API_KEY", "")

    if not openai_key:
        logger.warning("OPENAI_API_KEY not set — AI features disabled")

    if not api_key or not api_secret:
        logger.error("LIVEKIT_API_KEY and LIVEKIT_API_SECRET are required")
        return

    logger.info("Agent connecting to LiveKit at %s", livekit_url)
    # LiveKit Agents SDK entrypoint — expand here with actual agent logic
    logger.info("Agent connected (stub mode — no AI pipeline configured)")


if __name__ == "__main__":
    main()
