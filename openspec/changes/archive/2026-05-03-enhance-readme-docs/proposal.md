## Why

The project's README.md lacks essential onboarding content, making it difficult for new contributors or evaluators to understand system requirements, set up the environment correctly, and grasp the overall architecture and data model. Adding structured documentation now will reduce friction for local development and provide a clear reference for the project's design.

## What Changes

- Add system requirements section (Docker, Docker Compose version minimums)
- Add step-by-step `.env` setup guide referencing all required variables
- Add architecture overview with a high-level Mermaid diagram showing components and their relationships
- Add database schema section with Mermaid ER diagram covering critical tables only

## Capabilities

### New Capabilities

- `readme-docs`: Comprehensive README.md content covering system requirements, environment setup, architecture overview (Mermaid diagram), and database schema (Mermaid ER diagram)

### Modified Capabilities

<!-- None — this change only adds documentation content to README.md -->

## Impact

- `README.md` at project root (only file modified)
- No code, API, or runtime changes
- No breaking changes
