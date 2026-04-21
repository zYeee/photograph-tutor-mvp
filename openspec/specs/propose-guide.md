Read openspec/specs/project-requirements.md first.

Based on the requirements, generate OpenSpec propose commands 
in the following order:

1. Project scaffold (monorepo, docker-compose, .env)
2. Database schema design, and SQLite + REST API implementation
3. Curriculum content design, and implementation 
4. LiveKit voice agent (STT, LLM, TTS, memory injection, 
   intent detection)
5. React frontend (sidebar, voice UI, transcript display)
6. Documentation

For each propose:
- Give the /opsx:propose command (concise, no more than 2 lines)
- Give supplementary details to feed after AI generates 
  the initial artifacts
- Give acceptance criteria for manual verification
