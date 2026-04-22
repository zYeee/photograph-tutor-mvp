export interface Session {
  id: number
  user_id: number
  livekit_room_name: string
  mode: string
  user_level: string
  equipment_type: string
  started_at: string
  ended_at: string | null
  last_topic: string | null
}

export interface Message {
  id: number
  session_id: number
  role: 'user' | 'assistant'
  content: string
  created_at: string
}

export interface TokenResponse {
  token: string
  url: string
}

export interface CreateSessionPayload {
  user_id: number
  livekit_room_name: string
  mode: string
  user_level: string
  equipment_type: string
}

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  const res = await fetch(path, init)
  if (!res.ok) {
    const text = await res.text().catch(() => '')
    throw new Error(`${res.status}: ${text}`)
  }
  return res.json() as Promise<T>
}

export const getSessions = (userId: number) =>
  request<Session[]>(`/api/sessions?user_id=${userId}`)

export const getSession = (sessionId: number) =>
  request<Session>(`/api/sessions/${sessionId}`)

export const createSession = (payload: CreateSessionPayload) =>
  request<Session>('/api/sessions', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload),
  })

export const getMessages = (sessionId: number) =>
  request<Message[]>(`/api/sessions/${sessionId}/messages`)

export const closeSession = (sessionId: number) =>
  request<Session>(`/api/sessions/${sessionId}/close`, {
    method: 'PATCH',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({}),
  })

export const getToken = (room: string, identity = 'user') =>
  request<TokenResponse>(`/api/token?room=${encodeURIComponent(room)}&identity=${encodeURIComponent(identity)}`)
