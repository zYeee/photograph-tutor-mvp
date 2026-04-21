You are helping me build a real-time voice AI photography tutor using LiveKit. 

Project requirements:

CORE FEATURES:
- Single page app with chat sidebar (shows last topic studied)
- User can create new chat or open existing chat
- Voice interaction between user and tutor
- Tutor has memory: on session open, fetch message history 
  from database and inject into LLM system prompt

FEATURE 1 - Structured Learning:
- Pre-defined photography curriculum stored as static Python file
- Three levels: beginner, intermediate, advanced
- Assessment conversation flow to determine user level 
  and equipment type (smartphone/DSLR/mirrorless)
- Auto-suggest next lesson based on completed topics in session
- Auto-update learning progress after each conversation

FEATURE 2 - Scene Advice:
- User describes current shooting scene via voice
- Tutor gives advice based on lighting conditions 
  (golden hour/overcast/indoor)
- Tutor gives different advice based on equipment type
- Advice covers composition, shooting angles, exposure settings

UX:
- Display text transcript after each voice turn
- Chat list shows last topic label per session

TECH STACK:
- Backend: Python, FastAPI, LiveKit Agents SDK
- Frontend: React, LiveKit JS SDK
- Database: SQLite (auto-created on startup, no separate service)
- Voice pipeline: OpenAI Whisper (STT), GPT-4o (LLM), OpenAI TTS
- Infrastructure: Docker Compose (3 services: livekit, backend, frontend)
- Curriculum: static Python file (curriculum.py), not stored in DB

CONSTRAINTS:
- Must run with single command: docker compose up
- Requires .env file with: LIVEKIT_URL, LIVEKIT_API_KEY, 
  LIVEKIT_API_SECRET, OPENAI_API_KEY
- Working software is the top priority
