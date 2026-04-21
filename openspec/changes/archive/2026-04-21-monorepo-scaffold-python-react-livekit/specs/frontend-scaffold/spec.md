## ADDED Requirements

### Requirement: React + Vite application skeleton
The frontend SHALL be a React application in `/frontend/` built with Vite, including TypeScript support and the LiveKit JS SDK (`livekit-client` and `@livekit/components-react`).

#### Scenario: Dev server starts
- **WHEN** `npm run dev` is run inside `/frontend`
- **THEN** the Vite dev server SHALL start on port 5173 with HMR enabled

#### Scenario: Production build succeeds
- **WHEN** `npm run build` is run
- **THEN** the build SHALL complete without errors and output to `dist/`

### Requirement: LiveKit room join UI
The frontend SHALL include a minimal room join page that allows a user to enter a room name and connect to a LiveKit session using a token fetched from the backend.

#### Scenario: User joins a room
- **WHEN** a user enters a room name and clicks "Join"
- **THEN** the frontend SHALL request a token from `GET /api/token?room=<name>` and connect to the LiveKit room

#### Scenario: Backend unavailable
- **WHEN** the token fetch fails (backend not running)
- **THEN** the UI SHALL display an error message "Could not connect to backend"

### Requirement: Backend API proxy in dev
The frontend Vite config SHALL proxy `/api` requests to the backend service, avoiding CORS issues in local development.

#### Scenario: API call proxied to backend
- **WHEN** the frontend makes a fetch to `/api/health` during development
- **THEN** Vite SHALL forward the request to `http://backend:8000/health` and return the response

### Requirement: Environment variable for backend URL
The frontend SHALL read the backend URL from `VITE_BACKEND_URL` and fall back to `http://localhost:8000` if not set.

#### Scenario: Custom backend URL
- **WHEN** `VITE_BACKEND_URL=http://custom:9000` is set
- **THEN** the frontend SHALL direct all API calls to `http://custom:9000`
