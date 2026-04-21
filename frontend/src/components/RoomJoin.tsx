import { useState } from 'react'
import { LiveKitRoom, VideoConference } from '@livekit/components-react'
import '@livekit/components-styles'

interface TokenResponse {
  token: string
  url: string
}

export function RoomJoin() {
  const [roomName, setRoomName] = useState('')
  const [connection, setConnection] = useState<TokenResponse | null>(null)
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(false)

  async function handleJoin() {
    if (!roomName.trim()) return
    setLoading(true)
    setError('')
    try {
      const res = await fetch(`/api/token?room=${encodeURIComponent(roomName)}`)
      if (!res.ok) throw new Error(`Backend returned ${res.status}`)
      const data: TokenResponse = await res.json()
      setConnection(data)
    } catch (e) {
      setError('Could not connect to backend')
      console.error(e)
    } finally {
      setLoading(false)
    }
  }

  if (connection) {
    return (
      <LiveKitRoom
        token={connection.token}
        serverUrl={connection.url}
        connect={true}
        video={false}
        audio={true}
      >
        <VideoConference />
      </LiveKitRoom>
    )
  }

  return (
    <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', padding: '2rem', gap: '1rem' }}>
      <h1>Photography Tutor</h1>
      <input
        type="text"
        placeholder="Room name"
        value={roomName}
        onChange={(e) => setRoomName(e.target.value)}
        onKeyDown={(e) => e.key === 'Enter' && handleJoin()}
        style={{ padding: '0.5rem', fontSize: '1rem', width: '240px' }}
      />
      <button onClick={handleJoin} disabled={loading || !roomName.trim()} style={{ padding: '0.5rem 1.5rem' }}>
        {loading ? 'Connecting…' : 'Join'}
      </button>
      {error && <p style={{ color: 'red' }}>{error}</p>}
    </div>
  )
}
