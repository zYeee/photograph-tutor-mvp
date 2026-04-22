import asyncio
import logging
import os
from typing import Annotated, Optional

import httpx
from dotenv import load_dotenv

from livekit.agents import (
    Agent,
    AgentSession,
    AutoSubscribe,
    ConversationItemAddedEvent,
    JobContext,
    RunContext,
    WorkerOptions,
    cli,
    function_tool,
    llm,
)

load_dotenv()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("photo-tutor-agent")

BACKEND_URL = os.getenv("BACKEND_URL", "http://backend:8000")
HISTORY_CAP = 50


# ── HTTP helpers ──────────────────────────────────────────────────────────────

async def _get(client: httpx.AsyncClient, path: str, **params) -> Optional[dict | list]:
    try:
        r = await client.get(f"{BACKEND_URL}{path}", params=params or None)
        r.raise_for_status()
        return r.json()
    except Exception as exc:
        logger.warning("GET %s failed: %s", path, exc)
        return None


async def _post(path: str, json: dict) -> None:
    try:
        async with httpx.AsyncClient(timeout=10.0) as c:
            await c.post(f"{BACKEND_URL}{path}", json=json)
    except Exception as exc:
        logger.warning("POST %s failed: %s", path, exc)


async def _put(path: str, json: dict) -> None:
    try:
        async with httpx.AsyncClient(timeout=10.0) as c:
            await c.put(f"{BACKEND_URL}{path}", json=json)
    except Exception as exc:
        logger.warning("PUT %s failed: %s", path, exc)


async def _patch(path: str, json: dict) -> None:
    try:
        async with httpx.AsyncClient(timeout=10.0) as c:
            await c.patch(f"{BACKEND_URL}{path}", json=json)
    except Exception as exc:
        logger.warning("PATCH %s failed: %s", path, exc)


# ── system prompt ─────────────────────────────────────────────────────────────

def _build_system_prompt(session: dict, next_topic: Optional[dict]) -> str:
    level = session.get("user_level") or "beginner"
    equipment = session.get("equipment_type") or "camera"
    mode = session.get("mode", "structured_learning")

    if mode == "scene_advice":
        return (
            "You are an expert on-location photography advisor. "
            "When the user describes a scene or subject they want to photograph, give practical, "
            "actionable advice that covers: (1) how to work with the lighting conditions, "
            "(2) composition suggestions, (3) appropriate exposure settings, and "
            f"(4) tips specific to a {equipment}. "
            f"The user's skill level is {level} — calibrate the depth of your advice accordingly. "
            "Keep responses focused and conversational — this is a voice interaction."
        )

    if not session.get("user_level"):
        return (
            "You are a patient photography tutor. Your first task is to assess the student. "
            "Ask them about their photography experience level (beginner, intermediate, or advanced) "
            "and what camera equipment they use. "
            "Once you have their answers, call the update_user_level tool to record the information. "
            "Then introduce the first lesson for their level."
        )

    persona = (
        "You are a patient, encouraging photography tutor. "
        "Guide the student through the current topic step by step, "
        "using clear explanations and practical examples. "
        "If the user asks about available topics or lessons, you MUST use the list_curriculum_topics tool. "
        "Once you are confident the student has understood the current topic, call the complete_current_topic tool "
        "to mark it as finished before moving on to the next one. "
        "You are FORBIDDEN from mentioning any topic that is not returned by the list_curriculum_topics tool. "
        "When responding, use the exact titles and descriptions from the tool output only. "
        "If the tool returns an empty list, say you don't have any specific lessons for that level yet. "
        "Keep responses concise and conversational — this is a voice interaction."
    )
    context = f"\nUser level: {level}. Equipment: {equipment}."

    if next_topic:
        points = "\n".join(f"- {p}" for p in next_topic.get("teaching_points", []))
        return (
            persona + context
            + f"\n\nCurrent topic: {next_topic['title']}\n"
            f"{next_topic.get('description', '')}\n"
            f"Teaching points to cover:\n{points}"
        )

    return (
        persona + context
        + "\n\nThe student has completed all topics for their level. "
        "Answer any photography questions they have or help them advance to the next level."
    )


# ── entrypoint ────────────────────────────────────────────────────────────────

async def entrypoint(ctx: JobContext) -> None:
    await ctx.connect(auto_subscribe=AutoSubscribe.AUDIO_ONLY)

    openai_key = os.getenv("OPENAI_API_KEY", "")
    if not openai_key:
        logger.warning("OPENAI_API_KEY not set — AI features disabled; agent connected in no-op mode")
        await asyncio.sleep(float("inf"))
        return

    async with httpx.AsyncClient(timeout=10.0) as client:
        # Resolve session from room name
        session = await _get(client, "/api/sessions/lookup", livekit_room_name=ctx.room.name)
        if session is None:
            logger.error("No session found for room '%s'; disconnecting", ctx.room.name)
            return

        session_id: int = session["id"]  # type: ignore[index]
        user_id: int = session["user_id"]  # type: ignore[index]
        mode: str = session.get("mode", "structured_learning")  # type: ignore[union-attr]
        user_level: Optional[str] = session.get("user_level") or None  # type: ignore[union-attr]

        # Load prior message history (cap at most recent HISTORY_CAP)
        messages_raw = await _get(client, f"/api/sessions/{session_id}/messages") or []
        prior_messages: list[dict] = list(messages_raw)[-HISTORY_CAP:]  # type: ignore[arg-type]

        # Load next topic for structured learning
        next_topic: Optional[dict] = None
        if mode == "structured_learning" and user_level:
            nt_resp = await _get(client, f"/api/sessions/{session_id}/next-topic")
            if nt_resp and isinstance(nt_resp, dict):
                next_topic = nt_resp.get("next_topic")

    # Track the topic being taught (mutable via nonlocal in tool)
    current_topic_slug: Optional[str] = next_topic["slug"] if next_topic else None

    # Mark the current topic as in_progress when the session starts
    if mode == "structured_learning" and current_topic_slug:
        await _put(f"/api/users/{user_id}/progress/{current_topic_slug}", {"status": "in_progress"})

    # Build initial chat context from prior transcript
    chat_ctx = llm.ChatContext()
    for msg in prior_messages:
        role = msg.get("role", "")
        content = msg.get("content", "")
        if role in ("user", "assistant") and content:
            chat_ctx.add_message(role=role, content=content)  # type: ignore[arg-type]

    # Opening message based on mode / intent
    if prior_messages:
        opening = "Welcome back! I'm ready to continue when you are."
    elif mode == "structured_learning" and not user_level:
        opening = (
            "Hi! I'm your photography tutor. Before we dive in, I'd like to tailor the lessons to you. "
            "Could you tell me your current experience level — beginner, intermediate, or advanced? "
            "And what camera or device do you mainly use?"
        )
    elif mode == "structured_learning" and next_topic:
        opening = (
            f"Welcome! Today we're covering {next_topic['title']}. "
            f"{next_topic.get('description', '')} Ready to get started?"
        )
    elif mode == "structured_learning":
        opening = (
            "You've completed all the topics for your current level — great work! "
            "Feel free to ask me anything about photography, or let me know if you'd like to advance."
        )
    else:  # scene_advice
        opening = (
            "Hi! I'm your on-location photography advisor. "
            "Tell me about the scene or subject you're planning to shoot, "
            "and I'll give you tailored advice on lighting, composition, and exposure."
        )

    system_prompt = _build_system_prompt(session, next_topic)  # type: ignore[arg-type]

    # ── function tool for assessment flow ─────────────────────────────────────

    @function_tool
    async def update_user_level(
        _ctx: RunContext,
        level: Annotated[str, "Photography skill level: beginner, intermediate, or advanced"],
        equipment: Annotated[str, "Equipment type: smartphone, mirrorless, dslr, point-and-shoot, or film"],
    ) -> str:
        """Call this once you've determined the user's photography level and equipment from the assessment."""
        nonlocal current_topic_slug
        await _patch(f"/api/sessions/{session_id}", {"user_level": level, "equipment_type": equipment})
        async with httpx.AsyncClient(timeout=10.0) as c:
            nt = await _get(c, f"/api/sessions/{session_id}/next-topic")
        first_topic = nt.get("next_topic") if nt and isinstance(nt, dict) else None  # type: ignore[union-attr]
        if first_topic:
            current_topic_slug = first_topic["slug"]
            await _put(f"/api/users/{user_id}/progress/{current_topic_slug}", {"status": "in_progress"})
            return (
                f"Great — I've noted that you're at the {level} level using a {equipment}. "
                f"Let's start with our first topic: {first_topic['title']}. "
                f"{first_topic.get('description', '')} Shall we begin?"
            )
        return f"Got it — {level} level, {equipment}. Let's get started with photography!"

    @function_tool
    async def list_curriculum_topics(
        _ctx: RunContext,
    ) -> str:
        """Call this when the user asks to see what topics or lessons are available for their level."""
        logger.info("Agent calling list_curriculum_topics for level: %s", user_level)
        async with httpx.AsyncClient(timeout=10.0) as c:
            # We want to show all topics for the current user's level
            resp = await _get(c, "/api/topics")
            logger.info("Raw topics from API: %s", resp)
            if not resp or not isinstance(resp, list):
                return "I'm sorry, I couldn't retrieve the list of topics right now."

            # Filter for topics that belong to the user's level
            lines = [f"Here are the topics we can cover for your {user_level} level:"]
            found = False
            for root in resp:
                matching_children = [
                    child for child in root.get("children", [])
                    if child.get("level") == user_level
                ]
                if matching_children:
                    found = True
                    lines.append(f"\n{root['title'].upper()}")
                    for child in matching_children:
                        lines.append(f"• {child['title']}: {child['description']}")

            if not found:
                return f"It looks like I don't have any specific lessons categorized for the {user_level} level yet."

            return "\n".join(lines)

    @function_tool
    async def complete_current_topic(
        _ctx: RunContext,
        topic_slug: Annotated[str, "Exact slug of the topic the student just finished (e.g. 'golden-hour', 'aperture')"],
    ) -> str:
        """Call this when the student has successfully learned a topic and you're ready to move on.
        Always pass the slug of the topic that was actually taught in this conversation turn."""
        nonlocal current_topic_slug

        slug_to_finish = topic_slug.strip().lower()
        logger.info("Agent calling complete_current_topic for: %s", slug_to_finish)

        await _finish_topic(session_id, user_id, slug_to_finish)

        # Look up what's next
        async with httpx.AsyncClient(timeout=10.0) as c:
            nt = await _get(c, f"/api/sessions/{session_id}/next-topic")

        next_topic_data = nt.get("next_topic") if nt and isinstance(nt, dict) else None
        if next_topic_data:
            current_topic_slug = next_topic_data["slug"]
            await _put(f"/api/users/{user_id}/progress/{current_topic_slug}", {"status": "in_progress"})
            return (
                f"Excellent work! We've officially completed the topic on {slug_to_finish.replace('-', ' ').title()}. "
                f"Our next lesson will be: {next_topic_data['title']}. Shall we begin?"
            )

        current_topic_slug = None
        return (
            f"Great job! You've finished {slug_to_finish.replace('-', ' ').title()}. "
            "You've actually completed all the current lessons for your level! "
            "Is there anything else photography-related you'd like to discuss?"
        )

    # ── build agent and session ───────────────────────────────────────────────

    from livekit.plugins.openai import LLM, STT, TTS
    from livekit.plugins.silero import VAD

    agent = Agent(
        instructions=system_prompt,
        chat_ctx=chat_ctx,
        stt=STT(model="whisper-1"),
        llm=LLM(model="gpt-4o"),
        tts=TTS(),
        vad=VAD.load(),
        tools=[update_user_level, list_curriculum_topics, complete_current_topic],
    )

    agent_session = AgentSession(userdata={"session_id": session_id, "user_id": user_id})

    # ── transcript persistence ────────────────────────────────────────────────

    @agent_session.on("conversation_item_added")
    def _on_item_added(event: ConversationItemAddedEvent) -> None:
        item = event.item
        if not isinstance(item, llm.ChatMessage):
            return
        role = str(item.role)
        if role not in ("user", "assistant"):
            return
        content_parts = item.content or []
        text = "".join(
            part if isinstance(part, str) else (getattr(part, "text", None) or "")
            for part in content_parts
        )
        if text:
            _spawn(_post(f"/api/sessions/{session_id}/messages", {"role": role, "content": text}))

    # Keep strong references so tasks aren't GC'd before they finish.
    _background_tasks: set[asyncio.Task] = set()

    def _spawn(coro) -> None:
        t = asyncio.create_task(coro)
        _background_tasks.add(t)
        t.add_done_callback(_background_tasks.discard)

    async def _finish_topic(sid: int, uid: int, slug: str) -> None:
        await _post(f"/api/sessions/{sid}/topics/{slug}", {})
        await _put(f"/api/users/{uid}/progress/{slug}", {"status": "completed"})
        logger.info("Marked topic '%s' complete for session %d", slug, sid)

    # ── start ─────────────────────────────────────────────────────────────────

    await agent_session.start(agent, room=ctx.room)
    agent_session.say(opening)
    try:
        await asyncio.sleep(float("inf"))
    finally:
        # Drain any in-flight writes (e.g. topic completion triggered at disconnect)
        if _background_tasks:
            await asyncio.gather(*_background_tasks, return_exceptions=True)


AGENT_NAME = "photo-tutor"

if __name__ == "__main__":
    cli.run_app(WorkerOptions(entrypoint_fnc=entrypoint, agent_name=AGENT_NAME))
