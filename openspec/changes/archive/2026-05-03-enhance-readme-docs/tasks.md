## 1. System Requirements Section

- [x] 1.1 Add a "System Requirements" section to README.md listing Docker ≥ 24.0 and Docker Compose ≥ 2.20 (plugin syntax `docker compose`)

## 2. Environment Setup Guide

- [x] 2.1 Add an "Environment Setup" step-by-step section with `cp .env.example .env` as the first step
- [x] 2.2 Document all six variables (`LIVEKIT_URL`, `LIVEKIT_API_KEY`, `LIVEKIT_API_SECRET`, `OPENAI_API_KEY`, `DATABASE_URL`, `VITE_BACKEND_URL`) with required/optional status, default values, and descriptions

## 3. Architecture Diagram

- [x] 3.1 Add an "Architecture Overview" section with a Mermaid `graph TD` diagram showing Browser, Frontend, Backend, Agent, LiveKit Server, and SQLite nodes with labelled edges

## 4. Database Schema Diagram

- [x] 4.1 Add a "Database Schema" section with a Mermaid `erDiagram` covering the six critical tables: USERS, SESSIONS, MESSAGES, TOPICS, SESSION_TOPICS, USER_TOPIC_PROGRESS with crow's-foot FK notation

## 5. Verification

- [x] 5.1 Preview README.md locally (or via GitHub) to confirm both Mermaid diagrams render correctly
- [x] 5.2 Verify all six env variables are documented and correctly marked as required/optional
