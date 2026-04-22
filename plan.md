### plan
0. confirmed the AI tooling: claude code & openspec
1. have conversations with AI, clarify the requirements and added in openspec/specs/project-requirements.md, and feed it to openspec, which will manage the spec and prompts
2. what are you build and why?  
   * A real-time voice AI photography tutor. The core idea is that learning photography is hard to do from text, you need someone to talk through concepts with you, adapt to your level, and give you feedback in the moment. This app puts an AI
  tutor in your ear: you speak, it listens, teaches structured lessons or gives on-location scene advice, and tracks what you've covered across sessions.
3. prioritized features
   * Voice-first interaction: the entire UX is built around speaking, not typing. STT → GPT-4o → TTS is the core loop everything else supports.
   * Structured curriculum with progress tracking, topics organized by skill level (beginner/intermediate/advanced), with the agent tracking what's been covered per session and across sessions via the database.
   * Assessment flow, for new users, the agent asks about experience level and equipment before teaching, so lessons are calibrated from the first turn.
   * Session continuity(bonus point), prior conversation history is injected back into the AI context on reconnect, so the tutor remembers where you left off.
   * Post session summary(bonus point), able to check the study journey for the topic status(in process / done)

