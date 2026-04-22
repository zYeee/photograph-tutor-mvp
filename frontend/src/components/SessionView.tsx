import { useState, useCallback, useEffect, useRef } from 'react'
import { useQuery, useQueryClient } from '@tanstack/react-query'
import { LiveKitRoom, RoomAudioRenderer, useRoomContext } from '@livekit/components-react'
import { RoomEvent, type TranscriptionSegment, type Participant } from 'livekit-client'
import { getSession, getToken, closeSession, getMessages, type Session, type TokenResponse, type Message } from '../api'
import { Transcript } from './Transcript'
import './SessionView.css'

interface Props {
  sessionId: number | null
  userId: number
  onSessionClosed: () => void
}

const MODE_LABELS: Record<string, string> = {
  structured_learning: 'Structured Learning',
  scene_advice: 'Scene Advice',
}

export function SessionView({ sessionId, userId, onSessionClosed }: Props) {
  if (sessionId === null) {
    return (
      <div className="sv-empty">
        <p>Select a session or create a new one to get started.</p>
      </div>
    )
  }

  return <ActiveSession sessionId={sessionId} userId={userId} onSessionClosed={onSessionClosed} />
}

interface StreamingSegment {
  text: string
  role: 'user' | 'assistant'
}

function ActiveSession({ sessionId, userId }: { sessionId: number; userId: number; onSessionClosed: () => void }) {
  const queryClient = useQueryClient()
  const [tokenData, setTokenData] = useState<TokenResponse | null>(null)
  const [connected, setConnected] = useState(false)
  const [connecting, setConnecting] = useState(false)
  const [tokenError, setTokenError] = useState('')
  const [streamingSegments, setStreamingSegments] = useState<Map<string, StreamingSegment>>(new Map())

  const { data: session } = useQuery<Session>({
    queryKey: ['session', sessionId],
    queryFn: () => getSession(sessionId),
    refetchInterval: connected ? 3000 : false,
  })

  const { data: messages } = useQuery<Message[]>({
    queryKey: ['messages', sessionId],
    queryFn: () => getMessages(sessionId),
  })

  const isEmpty = !connected && (!messages || messages.length === 0)

  const handleConnect = useCallback(async () => {
    if (!session) return
    setConnecting(true)
    setTokenError('')
    try {
      const data = await getToken(session.livekit_room_name)
      setTokenData(data)
      setConnected(true)
    } catch (err) {
      setTokenError(err instanceof Error ? err.message : 'Failed to get token')
    } finally {
      setConnecting(false)
    }
  }, [session])

  const handleDisconnect = useCallback(async () => {
    setConnected(false)
    setTokenData(null)
    setStreamingSegments(new Map())
    try {
      await closeSession(sessionId)
      queryClient.invalidateQueries({ queryKey: ['sessions', userId] })
    } catch {
      // session may already be closed
    }
  }, [sessionId, userId, queryClient])

  const handleSegments = useCallback((segments: TranscriptionSegment[], participantIdentity: string) => {
    const role: 'user' | 'assistant' = participantIdentity === 'user' ? 'user' : 'assistant'
    setStreamingSegments((prev) => {
      const next = new Map(prev)
      for (const seg of segments) {
        if (seg.final) {
          // Keep the final segment briefly to bridge the gap until the next poll
          next.set(seg.id, { text: seg.text, role })
          setTimeout(() => {
            setStreamingSegments((current) => {
              const updated = new Map(current)
              updated.delete(seg.id)
              return updated
            })
          }, 3000)
        } else {
          next.set(seg.id, { text: seg.text, role })
        }
      }
      return next
    })
  }, [])

  // Merge streaming segments into a single preview per role (latest wins)
  const streamingPreviews = [...streamingSegments.values()]

  return (
    <div className="sv-container">
      <div className="sv-topbar">
        <div className="sv-topbar-info">
          <span className="sv-mode">{MODE_LABELS[session?.mode ?? ''] ?? session?.mode}</span>
          <span className="sv-topic">{session?.last_topic ?? 'No topic yet'}</span>
        </div>
        <div className="sv-topbar-controls">
          {tokenError && <span className="sv-error">{tokenError}</span>}
        </div>
      </div>

      {connected && tokenData && (
        <LiveKitRoom
          serverUrl={tokenData.url}
          token={tokenData.token}
          connect={connected}
          audio={true}
          video={false}
          onDisconnected={handleDisconnect}
        >
          <RoomAudioRenderer />
          <VoiceIndicator />
          <TranscriptStreamer onSegments={handleSegments} />
        </LiveKitRoom>
      )}

      {isEmpty ? (
        <div className="sv-hero">
          <button
            className="btn-start-chat-hero"
            onClick={handleConnect}
            disabled={connecting || !session}
          >
            {connecting ? '…' : '▶'}
          </button>
          <p className="sv-hero-label">{connecting ? 'Connecting…' : 'Start Chat'}</p>
        </div>
      ) : (
        <Transcript
          sessionId={sessionId}
          isConnected={connected}
          streamingPreviews={streamingPreviews}
        />
      )}

      {!isEmpty && (
        <div className="sv-bottom-bar">
          {connected ? (
            <button className="btn-disconnect btn-bottom" onClick={handleDisconnect}>
              End Chat
            </button>
          ) : (
            <button className="btn-connect btn-bottom" onClick={handleConnect} disabled={connecting || !session}>
              {connecting ? 'Connecting…' : 'Start Chat'}
            </button>
          )}
        </div>
      )}
    </div>
  )
}

function TranscriptStreamer({
  onSegments,
}: {
  onSegments: (segments: TranscriptionSegment[], participantIdentity: string) => void
}) {
  const room = useRoomContext()

  useEffect(() => {
    const handler = (segments: TranscriptionSegment[], participant: { identity: string }) => {
      onSegments(segments, participant.identity)
    }
    room.on(RoomEvent.TranscriptionReceived, handler)
    return () => { room.off(RoomEvent.TranscriptionReceived, handler) }
  }, [room, onSegments])

  return null
}

function VoiceIndicator() {
  const room = useRoomContext()
  const [agentSpeaking, setAgentSpeaking] = useState(false)
  const silenceTimer = useRef<ReturnType<typeof setTimeout> | null>(null)

  useEffect(() => {
    const handler = (speakers: Participant[]) => {
      const speaking = speakers.some((p) => p.identity !== 'user')
      if (speaking) {
        if (silenceTimer.current) {
          clearTimeout(silenceTimer.current)
          silenceTimer.current = null
        }
        setAgentSpeaking(true)
      } else {
        // Delay before switching to "Listening" to smooth over brief inter-sentence gaps
        silenceTimer.current = setTimeout(() => setAgentSpeaking(false), 800)
      }
    }
    room.on(RoomEvent.ActiveSpeakersChanged, handler)
    return () => {
      room.off(RoomEvent.ActiveSpeakersChanged, handler)
      if (silenceTimer.current) clearTimeout(silenceTimer.current)
    }
  }, [room])

  return (
    <div className="voice-indicator">
      {agentSpeaking ? (
        <span className="indicator indicator--speaking">Tutor speaking…</span>
      ) : (
        <span className="indicator indicator--listening">Listening…</span>
      )}
    </div>
  )
}
